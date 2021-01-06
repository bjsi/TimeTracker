from typing import List
from abc import ABC
from .rx.core.operators.timestamp import Timestamp
from .event_base import EventBase
from anki.cards import Card
from enum import Enum


class ReviewerEventOrigin(Enum):

    mouse = 1,
    keyboard = 2,


class ReviewerEvent(EventBase):

    card_id: int
    question: str
    answer: str
    deck_path: List[str]

    def __init__(self, origin: ReviewerEventOrigin, card: Card):
        super().__init__(origin.name)
        self.card_id = Card.id
        self.question = card.question()
        self.answer = card.answer()
        # TODO
        # self.deck_path

    @classmethod
    def custom_window_condition(cls, fst: Timestamp, snd: Timestamp) -> bool:
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
