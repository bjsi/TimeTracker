from typing import List, Dict
from enum import Enum

import anki

from .event_base import EventBase
from .rx.core.operators.timestamp import Timestamp
from .condensed_event import CondensedEvent


class CardAdderEventOrigin(Enum):

    opened_card_adder = 1
    added_note = 2


class CardAdderEvent(EventBase):

    added_note: bool = False
    note: anki.notes.Note

    def __init__(self, origin: str, note: anki.notes.Note = None):
        super().__init__(origin)
        if note:
            self.added_note = True
            self.note = note

    @classmethod
    def condense(cls, events: List[Timestamp]) -> Dict:
        fst = events[0]
        lst = events[-1]
        data = {"added_note": lst.value.added_note}
        return CondensedEvent(fst.timestamp, lst.timestamp, data).to_dict()

    @classmethod
    def custom_window_condition(cls, fst: Timestamp, snd: Timestamp):
        return fst.value.added_note

    def __repr__(self):
        return "<CardAdderEvent>"
