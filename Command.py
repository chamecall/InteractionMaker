from Media import Media
from Types import CommandType
from ImageProcessing import overlay_image_on_frame
from Types import CommandType, MediaType
import cv2
from ImageOverlay import ImageOverlay

class Command:

    def __init__(self, name, type, trigger_event, attached_character_class, relation_class, command_type: CommandType, media: Media, duration):

        self.name = name
        self.type = type
        self.trigger_event = trigger_event
        self.attached_character_class = attached_character_class
        self.relation_class = relation_class
        self.command_type = command_type
        self.media = media
        self.duration = duration
        self.executing = False
        self.overlay = None

    def mark_as_executing(self):
        self.executing = True

    def mark_as_not_executing(self):
        self.executing = False

    def exec(self, frame):
        command_executing = self.overlay.overlay(frame)
        if not command_executing:
            self.mark_as_not_executing()