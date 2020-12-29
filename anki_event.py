import datetime as dt
from enum import Enum
from typing import List


class EventOrigin(Enum):

    QUESTION_SHOWN = 0
    KEYBOARD_PRESSED = 1
    MOUSE_MOVED = 2
    MOUSE_CLICKED = 3


class AnkiEvent:

    timestamp: dt.datetime = dt.datetime.now()
    card_id: int
    question: str
    answer: str
    deck_path: List[str]
    origin: EventOrigin

    def __init__(self, card_id: int, origin: EventOrigin):
        self.card_id = card_id
        self.origin = origin

    def __repr__(self):
        return (f"<AE: id: {self.card_id} origin: {self.origin}")
