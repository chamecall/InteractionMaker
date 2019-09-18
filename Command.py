from Media import Media
from Types import CommandType
from ImageProcessing import overlay_image_on_frame_by_box
from Types import CommandType, MediaType
import cv2
from ImageOverlay import ImageOverlay
from enum import Enum, auto
from Timer import Timer

class Command:

    class State(str, Enum):
        WAITING = auto()
        EXECUTING = auto()
        DELAYING = auto()
        AFTER_DELAYING = auto()

    def __init__(self, name, centered, type, trigger_event, attached_character_class, relation_class,
                 command_type: CommandType, trigger_cmd_name, media: Media, duration, delay):
        self.centered = centered
        self.name = name
        self.type = type
        self.trigger_event = trigger_event
        self.attached_character_class = attached_character_class
        self.relation_class = relation_class
        self.command_type = command_type
        self.trigger_cmd_name = trigger_cmd_name
        self.media = media
        self.duration = duration
        self.delay = delay
        self.delay_timer = None
        self.cur_state = self.State.WAITING
        self.overlay = None


    def set_as_executing(self):
        self.cur_state = self.State.EXECUTING

    def set_as_waiting(self):
        self.cur_state = self.State.WAITING

    def set_as_after_delay(self):
        self.cur_state = self.State.AFTER_DELAYING

    def set_as_delaying(self, one_frame_duration):
        self.cur_state = self.State.DELAYING
        self.delay_timer = Timer(self.delay, one_frame_duration)

    def exec(self, frame):
        command_executing = self.overlay.overlay(frame)
        if not command_executing:
            self.set_as_waiting()

    def wait_out_delay(self):
        delay_is_over = self.delay_timer.ticktock()
        return delay_is_over


