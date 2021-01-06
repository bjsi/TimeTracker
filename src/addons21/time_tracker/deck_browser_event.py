from typing import List
from enum import Enum

from .event_base import EventBase
from .rx.core.operators.timestamp import Timestamp


class DeckBrowserEventOrigin(Enum):

    opened_browser = 1,


class DeckBrowserEvent(EventBase):
    def __init__(self, origin: str):
        super().__init__(origin)

    @classmethod
    def condense(cls, events: List[Timestamp]):
        fst = events[0]
        lst = events[-1]
        return {"duration": lst.timestamp - fst.timestamp}

    @classmethod
    def custom_window_condition(cls, fst: Timestamp, snd: Timestamp) -> bool:
        return False

    def __repr__(self):
        return "<DeckBrowserEvent>"