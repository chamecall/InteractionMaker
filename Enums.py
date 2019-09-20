from enum import Enum, auto

class MediaType(Enum):
    TEXT = auto()
    IMAGE = auto()
    AUDIO = auto()
    VIDEO = auto()

class CommandType(Enum):
    OBJECTS_TRIGGER = 0
    REACTION_CHAIN_TRIGGER = 1
    EMOTION_TRIGGER = 2

