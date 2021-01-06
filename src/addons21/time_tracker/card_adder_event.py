from typing import List
from enum import Enum

import anki

from .event_base import EventBase
from .rx.core.operators.timestamp import Timestamp


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
    def condense(cls, events: List[Timestamp]):
        fst = events[0]
        lst = events[-1]
        return {
            "duration": lst.timestamp - fst.timestamp,
            "added_note": lst.value.added_note,
            # TODO: include note data
        }

    def custom_window_condition(cls, fst: Timestamp, snd: Timestamp):
        return fst.value.added_note

    def __repr__(self):
        return "<CardAdderEvent>"
