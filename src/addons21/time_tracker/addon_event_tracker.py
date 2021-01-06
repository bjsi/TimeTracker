from .event_base import EventBase
from typing import Dict, List


class AddonEventStream:
    """
    Added to mw as a global variable.
    Can be accessed from other plugins.
    """

    __main_subj: Subject()
    events: List[Dict]

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
