from Media import Media
from Types import CommandType

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
        self.left_duration = duration
        self.executing = False
        self.media_cache = None

    def mark_as_executing(self):
        self.executing = True

    def mark_as_not_executing(self):
        self.executing = False
