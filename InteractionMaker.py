from DetectionReader import DetectionReader
from DB import DB
from Command import Command
from VideoReader import VideoReader
import cv2
from Media import Media
from Types import CommandType, MediaType
from ImageProcessing import draw_det_boxes
from ImageOverlay import ImageOverlay
from Recognizer import Recognizer
from TextOverlay import TextOverlay
import numpy as np
from Colors import Color

class InteractionMaker:

    def __init__(self):
        self.detection_reader = DetectionReader('detections.json')
        self.project_file_name = '/home/algernon/lol'
        self.video_file_name = ''
        self.db_name = ''
        self.data_base = None
        self.video_maker = None
        self.db_user_name = 'root'
        self.db_user_pass = 'root'
        self.db_host = 'localhost'
        self.commands = []
        self.output_video_file_name = 'output.mkv'
        self.video_reader = None
        self.video_writer = None
        self.open_project()
        self.recognizer = Recognizer('/home/algernon/PycharmProjects/AIVlog/mmdetection/configs/pascal_voc/faster_rcnn_r50_fpn_1x_voc0712.py', '/home/algernon/PycharmProjects/AIVlog/mmdetection/work_dirs/faster_rcnn_r50_fpn_1x_voc0712/epoch_10.pth')


    def open_project(self):
        with open(self.project_file_name, 'r') as project_file:
            self.video_file_name = project_file.readline().strip()
            self.db_name = project_file.readline().strip()

            self.data_base = DB(self.db_host, self.db_user_name, self.db_user_pass, self.db_name)
            self.video_reader = VideoReader(self.video_file_name)
            self.video_writer = cv2.VideoWriter(self.output_video_file_name, cv2.VideoWriter_fourcc(*"XVID"),
                                                self.video_reader.fps,
                                                (self.video_reader.width, self.video_reader.height))
            self.load_commands_from_db()

    def load_commands_from_db(self):
        # upload commands
        cursor = self.data_base.exec_query("SELECT * FROM Command")
        while cursor.rownumber < cursor.rowcount:
            command_response = cursor.fetchone()
            query = "SELECT name FROM Labels WHERE label_id=%s"
            attached_character_class = \
            self.data_base.exec_template_query(query, [command_response['attached_character_class']]).fetchone()['name']
            relation_class = ''
            if command_response['relation_class'] is not None:
                relation_class = self.data_base.exec_template_query(query, [command_response['relation_class']]).fetchone()[
                'name']

            media_response = self.data_base.exec_query(
                f"SELECT * FROM Media WHERE media_id={command_response['media_id']}").fetchone()
            media = Media(media_response['file_name'], media_response['type'], media_response['duration'])

            trigger_cmd_name = ''
            trigger_cmd_id = command_response['trigger_event_id']
            if trigger_cmd_id:
                trigger_cmd_name = self.data_base.exec_query(f"SELECT name FROM Command WHERE command_id={trigger_cmd_id}").fetchone()['name']

            delay = command_response['init_delay']
            command = Command(command_response['name'], command_response['centered'], command_response['type'], command_response['trigger_event_id'],
                              attached_character_class, relation_class, CommandType(command_response['command_type_id']),
                                trigger_cmd_name, media, command_response['duration'], delay)
            self.commands.append(command)

    def process_commands(self):
        while True:

            frame = self.video_reader.get_next_frame()

            cur_frame_num = self.video_reader.cur_frame_num
            #detections_per_frame = self.detection_reader.get_detections_per_specified_frame(cur_frame_num)
            _, detections_per_frame = self.recognizer.inference(frame)
            draw_det_boxes(frame, detections_per_frame)

            labels_per_frame = [detection[0] for detection in detections_per_frame]
            for command in self.commands:
                self.check_command_type(command, detections_per_frame, labels_per_frame)

            for active_cmd in [cmd for cmd in self.commands if cmd.executing]:
                active_cmd.exec(frame)

            cv2.imshow('frame', frame)
            self.video_writer.write(frame)
            cv2.waitKey(1)



    def check_command_type(self, command, detections_per_frame, labels_per_frame):
        if command.command_type == CommandType.OBJECT_ON_THE_SCREEN:
            self.check_object_on_the_screen_event(command, detections_per_frame, labels_per_frame)
        elif command.command_type == CommandType.REACTIONS_CHAIN:
            self.check_reactions_chain_event(command, detections_per_frame, labels_per_frame)


    def check_reactions_chain_event(self, command: Command, detections_per_frame, labels_per_frame):
        #there's main object
        if command.attached_character_class in labels_per_frame:
            #check whether triggered command is active
            active_command_names = [command.name for command in self.commands if command.executing]
            if command.trigger_cmd_name in active_command_names:
                self.custom_method(command, detections_per_frame, labels_per_frame)



    def custom_method(self, command: Command, detections_per_frame, labels_per_frame):
        main_box = detections_per_frame[labels_per_frame.index(command.attached_character_class)][1]
        coords = main_box

        if command.centered:
            secondary_box = detections_per_frame[labels_per_frame.index(command.relation_class)][1]
            main_box_center = [(main_box[i + 2] + main_box[i]) // 2 for i in range(2)]
            secondary_box_center = [(secondary_box[i + 2] + secondary_box[i]) // 2 for i in range(2)]
            boxes_center = [(main_box_center[i] + secondary_box_center[i]) // 2 for i in range(2)]
            coords = boxes_center

        if command.executing:
            command.overlay.set_coords(coords)
        else:
            if command.media.type == MediaType.IMAGE:
                command.overlay = self.generate_image_overlay_object(command, coords)
            elif command.media.type == MediaType.TEXT:
                command.overlay = self.generate_text_overlay_object(command, coords)

            command.mark_as_executing()

    def check_object_on_the_screen_event(self, command: Command, detections_per_frame, labels_per_frame):

        desired_classes = {command.attached_character_class, command.relation_class}
        # we found desired labels
        if desired_classes.issubset(labels_per_frame):
            self.custom_method(command, detections_per_frame, labels_per_frame)

    def generate_image_overlay_object(self, command: Command, coords: tuple):
        image = cv2.imread(command.media.file_name)
        delay = command.delay
        command.drop_delay()
        return ImageOverlay(image, command.duration, delay, coords, self.video_reader.one_frame_duration)

        
    def generate_text_overlay_object(self, command: Command, coords: tuple):
        texts = self.read_text_from_file(command.media.file_name)
        ellipse, text_rect = self.generate_thought_balloon_by_text(texts)
        delay = command.delay
        command.drop_delay()
        return TextOverlay((ellipse, text_rect), command.duration, delay, coords, self.video_reader.one_frame_duration)

    def generate_thought_balloon_by_text(self, texts: list):
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        color = Color.BLACK
        thickness = 2
        LINE_SPACING = 8
        text_settings = []
        for text in texts:
            text = text.rstrip()
            (text_width, text_height), shift = cv2.getTextSize(text, font, font_scale, thickness)
            text_height += shift + LINE_SPACING
            text_settings.append(((text_width, text_height), shift, text))

        rect_height = sum([text_size[0][1] for text_size in text_settings]) + LINE_SPACING * (len(texts) - 1)
        rect_width = max(text_settings, key=lambda text_size: text_size[0][0])[0][0]
        text_rect = np.ones([rect_height, rect_width, 3], 'uint8') * 255

        cur_height = -LINE_SPACING
        for (text_width, text_height), shift, text in text_settings:
            cur_height += text_height
            cur_width = (rect_width - text_width) // 2
            cv2.putText(text_rect, text, (cur_width, cur_height), font, font_scale, color, thickness)

        half_rect_width = rect_width // 2
        half_rect_height = rect_height // 2
        ellipse_height_delta = rect_height // 4
        ellipse_points = [(half_rect_width, half_rect_height), (-half_rect_width, half_rect_height), (-half_rect_width,
                                                                                                      -half_rect_height),
                          (half_rect_width, -half_rect_height), (0, half_rect_height + ellipse_height_delta)]

        ellipse_points = np.array(ellipse_points)
        ellipse = cv2.fitEllipse(ellipse_points)
        return ellipse, text_rect
        
    def read_text_from_file(self, txt_file):
        with open(txt_file) as txt:
            texts = txt.readlines()
        return texts

    def close(self):
        if self.video_reader:
            self.video_reader.close()
        if self.video_writer:
            self.video_writer.release()


interation_maker = InteractionMaker()
interation_maker.process_commands()
interation_maker.close()
