from typing import Dict, List

from .event_base import EventBase
from .rx.subject import Subject
from .addon_event_hook import TimeTrackerAddonEventHook


class AddonEventStream:
    """
    Added to mw as a global variable.
    Can be accessed from other plugins.
    """
    __main_subj: Subject = Subject()
    events: List[Dict]  # TODO is this threadsafe? does it need to be?
    addon_event_hook: TimeTrackerAddonEventHook = TimeTrackerAddonEventHook()

    def raise_event(self, event: Dict):
        self.events.append(event)
        self.addon_event_hook(event)

    def record_event(self, event: EventBase) -> Dict:
        """
        Returns a dict:
        {"result": "success"} on success.
        {"result": "failed", "message": "..."} on failed
        """
        if not event:
            return {"result": "failed", "message": "event cannot be None"}
        self.__main_subj.on_next(event)
        return {"result": "success"}
