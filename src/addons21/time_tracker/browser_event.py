from enum import Enum
from typing import List

from .event_base import EventBase
from .rx.core.operators.timestamp import Timestamp


class BrowserEventOrigin(Enum):
    row_changed = 1,
    search = 2,


# TODO: Split on search and include search term?
class BrowserEvent(EventBase):
    def __init__(self, origin: str):
        super().__init__(origin)

    @classmethod
    def custom_window_condition(cls, fst: Timestamp, snd: Timestamp):
        return False

    @classmethod
    def condense(cls, events: List[Timestamp]):
        fst = events[0]
        lst = events[-1]
        return {
            "duration": lst.timestamp - fst.timestamp,
        }
