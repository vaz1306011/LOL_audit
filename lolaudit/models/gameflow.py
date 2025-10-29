from enum import Enum, auto


class Gameflow(Enum):
    LOADING = auto()
    NONE = auto()
    LOBBY = auto()
    PENALTY = auto()
    MATCHMAKING = auto()
    READY_CHECK = auto()
    WAITING_ACCEPT = auto()
    DECLINED = auto()
    ACCEPTED = auto()
    CHAMP_SELECT = auto()
    IN_PROGRESS = auto()
    RECONNECT = auto()
    PRE_END_OF_GAME = auto()
    END_OF_GAME = auto()
    UNKNOWN = auto()
