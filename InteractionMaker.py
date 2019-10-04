import cv2

from Colors import Color
from Command import Command
from DB import DB
from DetectionReader import DetectionReader
from Enums import CommandType, MediaType
from ImageOverlay import ImageOverlay
from ImageProcessing import draw_det_boxes, generate_thought_balloon_by_text
from Media import Media
from Recognizer import Recognizer
from TextOverlay import TextOverlay
from VideoOverlay import VideoOverlay
from VideoReader import VideoReader
from pprint import pprint
from FaceRecognizer import FaceRecognizer
from EmotionRecognizer import EmotionRecognizer
from Captioner import Captioner
from SceneSegmentator import SceneSegmentator
from tqdm import trange

class InteractionMaker:
    EMOTION_PROB_THRESH = 0

    def __init__(self):
        self.detection_reader = DetectionReader('detections.json')
        self.project_file_name = '/home/algernon/andro2'
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
        self.emotion_detection_reader = DetectionReader('emotion_results/er.json')
        self.emotion_recognizer = EmotionRecognizer(self.EMOTION_PROB_THRESH)
        self.captioner = Captioner('/home/algernon/a-PyTorch-Tutorial-to-Image-Captioning/weights/BEST_checkpoint_coco_5_cap_per_img_5_min_word_freq.pth.tar',
                                   '/home/algernon/a-PyTorch-Tutorial-to-Image-Captioning/weights/WORDMAP_coco_5_cap_per_img_5_min_word_freq.json')
        self.segmentator = None
        self.face_recognizer = FaceRecognizer()
        self.open_project()
        self.recognizer = Recognizer(
            '/home/algernon/PycharmProjects/AIVlog/mmdetection/configs/pascal_voc/faster_rcnn_r50_fpn_1x_voc0712.py',
            '/home/algernon/PycharmProjects/AIVlog/mmdetection/work_dirs/faster_rcnn_r50_fpn_1x_voc0712/epoch_10.pth')

    def open_project(self):
        with open(self.project_file_name, 'r') as project_file:
            self.video_file_name = project_file.readline().strip()
            self.db_name = project_file.readline().strip()
            self.data_base = DB(self.db_host, self.db_user_name, self.db_user_pass, self.db_name)
            self.video_reader = VideoReader(self.video_file_name)
            self.video_writer = cv2.VideoWriter(self.output_video_file_name, cv2.VideoWriter_fourcc(*"XVID"),
                                                self.video_reader.fps,
                                                (self.video_reader.width, self.video_reader.height))
            self.segmentator = SceneSegmentator(self.video_reader.fps * 5)
            self.load_commands_from_db()

    def load_commands_from_db(self):
        # upload commands
        cursor = self.data_base.exec_query("SELECT * FROM Command")
        while cursor.rownumber < cursor.rowcount:
            command_response = cursor.fetchone()
            query = "SELECT name FROM Labels WHERE label_id=%s"
            attached_character_class = \
                self.data_base.exec_template_query(query, [command_response['attached_character_class']]).fetchone()[
                    'name']
            relation_class = ''
            if command_response['relation_class'] is not None:
                relation_class = \
                    self.data_base.exec_template_query(query, [command_response['relation_class']]).fetchone()[
                        'name']

            media_response = self.data_base.exec_query(
                f"SELECT * FROM Media WHERE media_id={command_response['media_id']}").fetchone()
            media = Media(media_response['file_name'], media_response['type'], media_response['duration'])

            trigger_cmd_name = ''
            trigger_cmd_id = command_response['trigger_event_id']
            if trigger_cmd_id is not None:
                trigger_cmd_name = \
                    self.data_base.exec_query(f"SELECT name FROM Command WHERE command_id={trigger_cmd_id}").fetchone()[
                        'name']

            delay = command_response['delay']

            emotion = ''
            emotion_id = command_response['expected_emotion_id']
            if emotion_id is not None:
                emotion = \
                self.data_base.exec_query(f"SELECT name FROM Emotion WHERE emotion_id={emotion_id}").fetchone()['name']

            command = Command(command_response['name'], command_response['centered'],
                              command_response['trigger_event_id'],
                              attached_character_class, relation_class,
                              CommandType(command_response['command_type_id']),
                              trigger_cmd_name, media, command_response['duration'], delay, emotion)
            self.commands.append(command)


    def process_commands(self):
        for _ in trange(self.video_reader.frame_count):
            frame = self.video_reader.get_next_frame()
            cur_frame_num = self.video_reader.cur_frame_num
            #emotion_detections = self.detect_emotions_on_frame(frame)
            emotion_detections = []

            self.segmentator.push_frame(frame)

            emotions_per_frame = []
            for emotion_pos, emotion in emotion_detections:
                emotions_per_frame.append((emotion_pos, emotion))
                self.draw_emotion_box(frame, emotion_pos, emotion)

            #_, object_detections_per_frame = self.recognizer.inference(frame)
            object_detections_per_frame = []
            draw_det_boxes(frame, object_detections_per_frame)

            labels_per_frame = [detection[0] for detection in object_detections_per_frame]
            states_needed_to_be_checked_on_event = [Command.State.WAITING, Command.State.EXECUTING,
                                                    Command.State.AFTER_DELAYING]
            commands_needed_to_be_checked_on_event = [cmd for cmd in self.commands if
                                                      cmd.cur_state in states_needed_to_be_checked_on_event]
            for command in commands_needed_to_be_checked_on_event:
                self.update_commands(command, object_detections_per_frame, emotions_per_frame, labels_per_frame)

            executing_commands = [cmd for cmd in self.commands if cmd.cur_state == cmd.State.EXECUTING]
            for active_cmd in executing_commands:
                active_cmd.exec(frame)

            delaying_commands = [cmd for cmd in self.commands if cmd.cur_state == cmd.State.DELAYING]
            for delaying_command in delaying_commands:
                if delaying_command.wait_out_delay():
                    delaying_command.set_as_after_delay()


            most_clear_img = self.segmentator.get_most_clear_frame()
            caption = self.captioner.caption_img(most_clear_img)
            cv2.putText(frame, caption, (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, Color.GOLD, 2)

            cv2.imshow('frame', frame)
            self.video_writer.write(frame)
            cv2.waitKey(1)


    def detect_emotions_on_frame(self, frame):
        #return list of items of the following format: ((lt_point: tuple, rb_point: tuple), (emotion: str, prob: int))
        detected_faces = self.face_recognizer.recognize_faces_on_image(frame)
        emotions = []
        for face_pos in detected_faces:
            (l, t), (r, b) = face_pos
            face_img = frame[t:b, l:r]
            emotion = self.emotion_recognizer.recognize_emotion_by_face(face_img)
            if emotion:
                emotions.append((face_pos, emotion))
        return emotions

    def draw_emotion_box(self, frame, emotion_pos, emotion: list):

        cv2.rectangle(frame, *emotion_pos, Color.GOLD, 2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f'{emotion[0]} - {emotion[1]}', (emotion_pos[0][0], emotion_pos[0][1] - 5), font, 1,
                    Color.YELLOW, 3)

    def update_commands(self, command, detections_per_frame, emotions_per_frame, labels_per_frame):
        if command.command_type == CommandType.OBJECTS_TRIGGER:
            self.check_object_on_the_screen_event(command, detections_per_frame, labels_per_frame)
        elif command.command_type == CommandType.REACTION_CHAIN_TRIGGER:
            self.check_reactions_chain_event(command, detections_per_frame, labels_per_frame)
        elif command.command_type == CommandType.EMOTION_TRIGGER:
            self.check_emotion_event(command, detections_per_frame, emotions_per_frame, labels_per_frame)

    def check_emotion_event(self, command: Command, objects_detections, emotion_detections, labels_per_frame):
        # emotions_per_frame format - [((start_point, end_point), (emotion, prob)), ...]
        # check whether there's main object
        if command.attached_character_class in labels_per_frame:
            # check whether there's expected emotion
            expected_emotions = [emotion for emotion in emotion_detections if emotion[1][0] == command.emotion]
            # check whether an emotion box is inside main object
            main_object_box = self.get_coords(command, objects_detections, labels_per_frame)
            main_object_box = (main_object_box[:2]), (main_object_box[2:])
            emotion = [emotion for emotion in expected_emotions if self.is_rect_inside_rect((emotion[0][0], emotion[0][1]), main_object_box)]
            assert len(emotion) <= 1
            if emotion:
                print(emotion)
                coords = *emotion[0][0][0], *emotion[0][0][1]
                self.update_state(True, command, objects_detections, labels_per_frame, coords=coords)




    def is_rect_inside_rect(self, in_rect: tuple, out_rect: tuple):
        lt_in_box_point_inside_out_box = all([out_rect[0][i] <= in_rect[0][i] <= out_rect[1][i] for i in range(2)])
        rb_in_box_point_inside_out_box = all([out_rect[0][i] <= in_rect[0][i] <= out_rect[1][i] for i in range(2)])
        return lt_in_box_point_inside_out_box and rb_in_box_point_inside_out_box


    def check_reactions_chain_event(self, command: Command, detections_per_frame, labels_per_frame):
        # there's main object
        if command.attached_character_class in labels_per_frame:
            # check whether triggered command is active

            active_command_names = [command.name for command in self.commands if
                                    command.cur_state == command.State.EXECUTING]
            event_happened = command.trigger_cmd_name in active_command_names
            self.update_state(event_happened, command, detections_per_frame, labels_per_frame)

    def check_object_on_the_screen_event(self, command: Command, detections_per_frame, labels_per_frame):

        desired_classes = {command.attached_character_class, command.relation_class}
        # we found desired labels
        event_happened = desired_classes.issubset(labels_per_frame)
        self.update_state(event_happened, command, detections_per_frame, labels_per_frame)

    def update_state(self, event_happened, command, detections_per_frame, labels_per_frame, coords=None):
        if event_happened:
            if command.cur_state == command.State.WAITING:
                command.set_as_delaying(self.video_reader.one_frame_duration)
                return

            coords = self.get_coords(command, detections_per_frame, labels_per_frame) if not coords else coords
            if command.cur_state == command.State.EXECUTING:
                command.overlay.set_coords(coords)

            # extract later this part from update_commands method
            if command.cur_state == command.State.AFTER_DELAYING:
                if command.media.type == MediaType.VIDEO:
                    command.overlay = self.generate_video_overlay(command, coords)
                elif command.media.type == MediaType.IMAGE:
                    command.overlay = self.generate_image_overlay_object(command, coords)
                elif command.media.type == MediaType.TEXT:
                    command.overlay = self.generate_text_overlay_object(command, coords)
                command.set_as_executing()

        elif command.cur_state == command.cur_state.AFTER_DELAYING:
            command.set_as_waiting()

    @staticmethod
    def get_coords(command: Command, detections_per_frame, labels_per_frame):
        main_box = detections_per_frame[labels_per_frame.index(command.attached_character_class)][1]
        coords = main_box
        if command.centered:
            secondary_box = detections_per_frame[labels_per_frame.index(command.relation_class)][1]
            main_box_center = [(main_box[i + 2] + main_box[i]) // 2 for i in range(2)]
            secondary_box_center = [(secondary_box[i + 2] + secondary_box[i]) // 2 for i in range(2)]
            boxes_center = [(main_box_center[i] + secondary_box_center[i]) // 2 for i in range(2)]
            coords = boxes_center

        return coords

    def generate_video_overlay(self, command: Command, coords: tuple):
        video_cap = cv2.VideoCapture(command.media.file_name)
        duration = command.media.duration if command.duration == 0 else command.duration
        return VideoOverlay(video_cap, duration, coords, self.video_reader.one_frame_duration)

    def generate_image_overlay_object(self, command: Command, coords: tuple):
        image = cv2.imread(command.media.file_name)
        return ImageOverlay(image, command.duration, coords, self.video_reader.one_frame_duration)

    def generate_text_overlay_object(self, command: Command, coords: tuple):
        texts = self.read_text_from_file(command.media.file_name)
        ellipse, text_rect = generate_thought_balloon_by_text(texts)
        return TextOverlay((ellipse, text_rect), command.duration, coords, self.video_reader.one_frame_duration)

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
