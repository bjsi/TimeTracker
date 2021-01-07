from typing import Dict, List, Callable

from .event_base import EventBase
from .rx.subject import Subject


class AddonEventStream:
    """
    Added to mw as a global variable.
    Can be accessed from other plugins.
    """
    __main_subj: Subject = Subject()
    events: List[Dict]
    on_event: List[Callable[[Dict], None]] = []

    def raise_event(self, event: Dict):
        self.events.append(event)
        for func in self.on_event:
            try:
                func(event)
            except Exception:
                pass

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
