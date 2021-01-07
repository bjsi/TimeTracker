from typing import List
from .rx.core.operators.timestamp import Timestamp
from .event_base import EventBase
from anki.cards import Card
from enum import Enum


class ReviewerEventOrigin(Enum):

    question_shown = 1,
    answer_shown = 2,
    answered = 3,
    review_ended = 4


class ReviewerEvent(EventBase):

    card_id: int
    question: str
    answer: str
    deck_path: List[str]

    def __init__(self, origin: str, card: Card):
        super().__init__(origin)
        self.card_id = card.id
        self.question = card.question()
        self.answer = card.answer()
        # TODO
        # self.deck_path

    @classmethod
    def custom_window_condition(cls, fst: Timestamp, snd: Timestamp) -> bool:
        # TODO: Split on answered? Include ease?
        return fst.value.card_id != snd.value.card_id

    @classmethod
    def condense(cls, events: List[Timestamp]):
        fst = events[0]
        lst = events[-1]
        return {
            "duration": lst.timestamp - fst.timestamp,
            "card_id": fst.value.card_id,
            # TODO: Can this change? If so, diff question and answer
            "question": fst.value.question,
            "answer": fst.value.answer,
            # TODO
            "deck_path": []
        }

    def __repr__(self):
        return f"<ReviewerEvent: id: {self.card_id}>"
