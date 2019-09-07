from enum import Enum, auto

class MediaType(Enum):
    TEXT = auto()
    IMAGE = auto()
    AUDIO = auto()
    VIDEO = auto()

class CommandType(Enum):
    OBJECT_ON_THE_SCREEN = 0
