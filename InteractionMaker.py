from DetectionReader import DetectionReader
from DB import DB
from Command import Command
from VideoReader import VideoReader
import cv2
from Media import Media
from Types import CommandType, MediaType
from ImageProcessing import overlay_image_on_frame
from ImageOverlay import ImageOverlay
from Recognizer import Recognizer
from TextOverlay import TextOverlay
import numpy as np

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
            relation_class = self.data_base.exec_template_query(query, [command_response['relation_class']]).fetchone()[
                'name']
            media_response = self.data_base.exec_query(
                f"SELECT * FROM Media WHERE media_id={command_response['media_id']}").fetchone()
            media = Media(media_response['file_name'], media_response['type'], media_response['duration'])

            command = Command(command_response['name'], command_response['type'], command_response['trigger_event_id'],
                              attached_character_class,
                              relation_class, CommandType(command_response['command_type_id']), media,
                              command_response['duration'])
            self.commands.append(command)

        # now we use just one command
        self.commands = self.commands[:1]

    def process_commands(self):
        while True:

            frame = self.video_reader.get_next_frame()

            cur_frame_num = self.video_reader.cur_frame_num
            #detections_per_frame = self.detection_reader.get_detections_per_specified_frame(cur_frame_num)
            _, detections_per_frame = self.recognizer.inference(frame)

            labels_per_frame = [detection[0] for detection in detections_per_frame]

            for command in [command for command in self.commands if not command.executing]:
                self.check_command_type(command, detections_per_frame, labels_per_frame)

            for command in [command for command in self.commands if command.executing]:
                command.exec(frame)

            cv2.imshow('frame', frame)
            self.video_writer.write(frame)
            cv2.waitKey(1)

    def check_command_type(self, command, detections_per_frame, labels_per_frame):
        if command.command_type == CommandType.OBJECT_ON_THE_SCREEN:
            self.check_object_on_the_screen_event(command, detections_per_frame, labels_per_frame)

    def check_object_on_the_screen_event(self, command: Command, detections_per_frame, labels_per_frame):

        desired_classes = {command.attached_character_class, command.relation_class}
        # we found desired labels
        if desired_classes.issubset(labels_per_frame):

            main_character_box = \
                detections_per_frame[labels_per_frame.index(command.attached_character_class)][1]
            main_character_box = list(map(int, main_character_box))
            top_right_box_point = main_character_box[2], main_character_box[1]
            if command.media.type == MediaType.IMAGE:
                command.overlay = self.generate_image_overlay_object(command, top_right_box_point)
            elif command.media.type == MediaType.TEXT:
                command.overlay = self.generate_text_overlay_object(command, top_right_box_point)

            command.mark_as_executing()

    def generate_image_overlay_object(self, command: Command, point):
        image = cv2.imread(command.media.file_name)
        return ImageOverlay(image, command.duration, point, self.video_reader.one_frame_duration)
        
    def generate_text_overlay_object(self, command: Command, point):
        text = self.read_text_from_file(command.media.file_name)
        balloon = self.generate_balloon_by_text(text)
        return ImageOverlay(balloon, command.duration, point, self.video_reader.one_frame_duration)

    def generate_balloon_by_text(self, text: str):
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        color = (0, 0, 0)
        thickness = 2
        (font_width, font_height), shift = cv2.getTextSize(text, font, font_scale, thickness)
        delta_width = (font_height + shift)

        y_square = ((font_height + shift) / 2) ** 2
        x_square = (font_width / 2) ** 2
        a_square = (font_width / 2 + delta_width) ** 2

        ellipse_height = int((y_square / (1 - (x_square / a_square))) ** 0.5 * 2)
        print(font_height)
        print(ellipse_height)
        print(ellipse_height)
        font_width += delta_width * 2

        black_rect = np.zeros([ellipse_height, font_width, 3])
        cv2.ellipse(black_rect, (int(black_rect.shape[1] / 2), int(black_rect.shape[0] / 2)),
                    (int(black_rect.shape[1]/2), int(black_rect.shape[0]/2)), 0, 0, 360, (0, 0, 255), -1)
        text_y_position = int(((ellipse_height - font_height) / 2) + font_height)
        text_x_position = delta_width
        cv2.putText(black_rect, text, (text_x_position, text_y_position), font, font_scale, (255, 255, 0), thickness)

        return black_rect


        
    def read_text_from_file(self, txt_file):
        with open(txt_file) as txt:
            text = txt.read()
        return text

    def close(self):
        if self.video_reader:
            self.video_reader.close()
        if self.video_writer:
            self.video_writer.release()


interation_maker = InteractionMaker()
interation_maker.process_commands()
interation_maker.close()
