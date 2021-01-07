from typing import Any, List, Optional, Tuple
from enum import Enum

from .rx.core.operators.timestamp import Timestamp
from .event_base import EventBase


class EditorEventOrigin(Enum):

    editor_opened = 1,
    field_focused = 2
    field_unfocused = 3


class EditorEvent(EventBase):
    def __init__(self, origin: str):
        super().__init__(origin)

    @classmethod
    def condense(cls, events: List[Timestamp]):
        fst = events[0]
        lst = events[-1]
        return {"duration": lst.timestamp - fst.timestamp}

    @classmethod
    def custom_window_condition(cls, fst: Timestamp, snd: Timestamp):
        return False
