import multiprocessing
from typing import Any, Optional, Tuple, List, Callable, Dict
import os
import aqt
from aqt import mw
from anki.cards import Card
from aqt import gui_hooks
from aqt.reviewer import Reviewer
from .rx import operators as ops
from .rx.core.observable import observable
from .rx.scheduler import ThreadPoolScheduler
from .rx.subject import Subject
from .anki_event import (MouseEvent, KeyboardEvent, QuestionShownEvent,
                         AnkiEvent, AnsweredEvent, AnswerShownEvent,
                         ReviewEndEvent)
from .rx_utils import (merge_streams, timestamp, emit_when, pairwise_buffer,
                       shift_right)
from .anki_event import AnkiEventPair
from .rx_debug import spy


class AddonEvent():

    addon_name: str
    data: Any

    def __init__(self, name: str, data: Any):
        self.name = name
        self.data = data


class AddonEventPair():

    fst: Timestamp[AddonEvent]
    snd: Timestamp[AddonEvent]

    def __init__(self, pair: List[AddonEvent]):
        assert len(pair) == 2
        fst = pair[0]
        snd = pair[1]
        assert fst.timestamp > snd.timestamp
        assert fst.value.addon_name == snd.value.addon_name

    def compare(self) -> bool:
        pass


class RegisteredAddon:

    addon_name: str
    comparer: Callable
    condenser: Callable

    def __init__(self, name: str, comparer: Callable, condenser: Callable):
        self.addon_name = name
        self.comparer = comparer
        self.condenser = condenser


class AddonEventTracker:
    """
    Added to mw as a global variable.
    Can be accessed from other plugins.
    """

    main_subj: Subject = Subject()
    registered_addons: Dict[str, RegisteredAddon] = {}

    def __init__(self):
        pass

    # TODO: data
    def record_event(self, addon_name: str, data: Any) -> Dict:
        """
        Addons must register using register_addon()
        before calling record_event()

        Returns a dict:
        {"result": "success"} on success.
        {"result": "failed", "message": "..."} on failed
        """
        if not addon_name:
            return {
                "result": "failed",
                "message": "addon_name must not be None or empty"
            }
        if not self.registered_addons.get(addon_name):
            return {
                "result": "failed",
                "message": f"addon {addon_name} has not been registered yet"
            }
        if not data:
            return {"result": "failed", "message": "data cannot be None"}
        self.main_subj.on_next(data)
        return {"result": "success"}

    def register_addon(self, addon_name: str, comparer: Callable,
                       condenser: Callable):
        """
        Returns a dict:
        {"result": "success"} on success.
        {"result": "failed", "message": "..."} on failed
        """
        if not addon_name:
            return {
                "result": "failed",
                "message": "addon_name must not be None or empty"
            }
        if self.registered_addons.get(addon_name):
            return {
                "result": "failed",
                "message": f"addon {addon_name} has already been registered"
            }
        if not comparer:
            return {"result": "failed", "message": ""}

        if not condenser:
            return {"result": "failed", "message": ""}

        self.registered_addons[addon_name] = RegisteredAddon(
            addon_name, comparer, condenser)
        return {"result": "success"}
