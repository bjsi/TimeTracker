from typing import List
from aqt import gui_hooks

from .event_stream_base import EventStreamBase
from .rx.subject import Subject
from .rx_utils import timestamp
from .event_base import EventBase
from .rx.core.operators.timestamp import Timestamp


class ProfileCloseEvent(EventBase):
    def __init__(self):
        super().__init__(origin="profile_closed")
        pass

    @classmethod
    def custom_window_condition(cls, fst: Timestamp, snd: Timestamp) -> bool:
        return False

    @classmethod
    def condense(cls, events: List[Timestamp]):
        # throw error, shouldn't ever get called
        pass


class MainWindowEventStream(EventStreamBase):

    closed = Subject()

    def __init__(self):
        self.__subscribe_to_gui_hooks()
        self.__create_main_stream()

    def __create_main_stream(self):
        self.main_subj = timestamp(self.closed)

    def __subscribe_to_gui_hooks(self):
        gui_hooks.profile_will_close.append(self.on_closed)

    def on_closed(self):
        self.closed.on_next(ProfileCloseEvent())
