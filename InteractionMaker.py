from DetectionReader import DetectionReader
from DB import DB
from Command import Command
from VideoReader import VideoReader
import cv2
from Media import Media
from Types import CommandType, MediaType
from VideoMaker import overlay_image_on_frame

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
        self.check_event = {CommandType.OBJECT_ON_THE_SCREEN: self.exec_object_on_the_screen_command}



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
            detections_per_frame = self.detection_reader.get_detections_per_specified_frame(cur_frame_num)
            labels_per_frame = [detection[0] for detection in detections_per_frame]

            for command in [command for command in self.commands if not command.executing]:
                self.process_not_executing_command(command, frame, detections_per_frame, labels_per_frame)

            for command in [command for command in self.commands if command.executing]:
                self.process_executing_command(command, frame, detections_per_frame, labels_per_frame)

            cv2.imshow('frame', frame)
            cv2.waitKey(1)


    def process_executing_command(self, command, frame, detections_per_frame, labels_per_frame):
        self.exec_object_on_the_screen_command(command, frame, detections_per_frame, labels_per_frame)

    def process_not_executing_command(self, command, frame, detections_per_frame, labels_per_frame):
        self.check_event[command.command_type](command, frame, detections_per_frame, labels_per_frame)



    def exec_object_on_the_screen_command(self, command, frame, detections_per_frame, labels_per_frame):
        desired_classes = {command.attached_character_class, command.relation_class}
        if desired_classes.issubset(labels_per_frame):
            main_character_box = \
                detections_per_frame[list(labels_per_frame).index(command.attached_character_class)][2]
            main_character_box = list(map(int, main_character_box))
            if command.media.type == MediaType.IMAGE:
                command.media_cache = cv2.imread(command.media.file_name)
                overlay_image_on_frame(frame, command.media_cache, (main_character_box[0], main_character_box[1]))

            if not command.executing:
                command.mark_as_executing()

            command.left_duration -= self.video_reader.one_frame_duration
            if command.left_duration <= 0:
                command.mark_as_not_executing()

interation_maker = InteractionMaker()
interation_maker.process_commands()
