from typing import Any, List, Optional, Tuple
from enum import Enum

from .rx.core.operators.timestamp import Timestamp
from .event_base import EventBase


class EditorEventOrigin(Enum):
    pass


class EditorEvent(EventBase):
    def __init__(self, origin: str):
        super().__init__(origin)

    @classmethod
    def condense(cls, events: List[Timestamp]):
        pass

    @classmethod
    def custom_window_condition(cls, fst: Timestamp, snd: Timestamp):
        pass
