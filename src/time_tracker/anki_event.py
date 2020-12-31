from typing import List
from abc import ABC
from rx.core.operators.timestamp import Timestamp


class AnkiEvent(ABC):

    card_id: int
    question: str
    answer: str
    deck_path: List[str]

    def __init__(self, card_id: int):
        self.card_id = card_id

    def __repr__(self):
        return f"<AE: id: {self.card_id}>"


class KeyboardEvent(AnkiEvent):
    """
    Represents a keyboard pressed event.
    """
    def __repr__(self):
        return (f"<KE: id: {self.card_id}>")


class MouseEvent(AnkiEvent):
    """
    Represents a mouse move, click or scroll event.
    """
    def __repr__(self):
        return (f"<ME: id: {self.card_id}>")


class QuestionShownEvent(AnkiEvent):
    """
    Represents a new card being shown to the user.
    """
    def __repr__(self):
        return (f"<QE: id: {self.card_id}>")


class AnkiEventPair:
    """
    Represents a pair of anki events to be compared.
    """

    fst: Timestamp
    snd: Timestamp

    def __init__(self, pair: List[Timestamp[AnkiEvent]]):
        assert len(pair) == 2
        fst = pair[0]
        snd = pair[1]
        assert snd.timestamp > fst.timestamp
        self.fst = fst
        self.snd = snd

    def different_cards(self) -> bool:
        return self.fst.value.card_id != self.snd.value.card_id

    def afk_timeout(self) -> bool:
        return (self.snd.timestamp - self.fst.timestamp).total_seconds() > 30

    def __repr__(self):
        return "<P: fst: {self.fst.value} snd: {self.snd.value}>"
