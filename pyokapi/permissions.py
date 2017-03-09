from enum import Enum, auto


class Permissions(Enum):
    SET_STATUS = auto()
    VALUABLE_ACCESS = auto()
    LONG_ACCESS_TOKEN = auto()
    PHOTO_CONTENT = auto()
    VIDEO_CONTENT = auto()
    APP_INVITE = auto()
    GET_EMAIL = auto()
