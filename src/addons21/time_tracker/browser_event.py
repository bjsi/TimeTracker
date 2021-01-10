from enum import Enum
from typing import List, Dict

from .event_base import EventBase
from .rx.core.operators.timestamp import Timestamp
from .condensed_event import CondensedEvent


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
    def condense(cls, events: List[Timestamp]) -> Dict:
        fst = events[0]
        lst = events[-1]
        data = {}
        return CondensedEvent(fst.timestamp, lst.timestamp, data).to_dict()
