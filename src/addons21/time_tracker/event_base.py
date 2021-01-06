from abc import ABC, abstractmethod, abstractclassmethod
from .rx.core.operators.timestamp import Timestamp
from typing import List


class EventBase(ABC):
    """
    Base class for tracked events.
    NOTE: Each value attribute of Timestamp will be derived from EventBase
    """

    # The origin of the event eg. keypress
    origin: str = "unknown"

    def __init__(self, origin: str):
        self.origin = origin

    @staticmethod
    def __types_are_different(fst: Timestamp, snd: Timestamp) -> bool:
        return type(fst.value) is not type(snd.value)

    @staticmethod
    def __validate_pair(pair: List[Timestamp]) -> None:
        assert len(pair) == 2
        assert pair[0].timestamp <= pair[1].timestamp

    @abstractclassmethod
    def condense(cls, events: List[Timestamp]):
        """
        Takes a list of events and returns a single activity snapshot for
        the period.
        """
        pass

    @classmethod
    def should_window(cls, pair: List[Timestamp]) -> bool:
        cls.__validate_pair(pair)
        fst = pair[1]
        snd = pair[2]
        return (cls.__types_are_different(fst, snd)
                or cls.custom_window_condition(fst, snd))

    @abstractclassmethod
    def custom_window_condition(cls, fst: Timestamp, snd: Timestamp) -> bool:
        """
        Override this to implement custom event stream splitting logic.
        """
        pass
