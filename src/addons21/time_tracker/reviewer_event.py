from enum import Enum
from typing import Dict, List
import re

from anki.cards import Card

from .condensed_event import CondensedEvent
from .event_base import EventBase
from .rx.core.operators.timestamp import Timestamp


class ReviewerEventOrigin(Enum):

    question_shown = 1,
    answer_shown = 2,
    answered = 3,
    review_ended = 4


class ReviewEndedEvent(EventBase):
    def __init__(self):
        super().__init__(origin="review_ended")
        pass

    @classmethod
    def custom_window_condition(cls, fst: Timestamp, snd: Timestamp) -> bool:
        return False

    @classmethod
    def condense(cls, events: List[Timestamp]):
        # throw error, shouldn't ever get called
        pass


class ReviewerEvent(EventBase):

    card_id: int
    question: str
    answer: str
    deck_path: List[str]  # TODO

    def __init__(self, origin: str, card: Card):
        super().__init__(origin)
        self.card_id = card.id
        self.question = card.question()
        self.answer = card.answer()

    @classmethod
    def custom_window_condition(cls, fst: Timestamp, snd: Timestamp) -> bool:
        # TODO: Split on answered? Include ease?
        return fst.value.card_id != snd.value.card_id

    @staticmethod
    def strip_html(text: str):
        return re.sub('<[^<]+?>', '', text)

    @classmethod
    def condense(cls, events: List[Timestamp]) -> Dict:
        fst = events[0]
        lst = events[-1]
        data = {
            "card_id": fst.value.card_id,
            # TODO: Can this change? If so, diff question and answer
            "question": cls.strip_html(fst.value.question),
            "answer": cls.strip_html(fst.value.answer),
            "deck_path": []
        }
        return CondensedEvent("reviewer", fst.timestamp, lst.timestamp,
                              data).to_dict()

    def __repr__(self):
        return f"<ReviewerEvent: id: {self.card_id}>"
