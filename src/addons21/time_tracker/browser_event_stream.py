import aqt
from aqt import gui_hooks

from .browser_event import BrowserEvent, BrowserEventOrigin
from .event_stream_base import EventStreamBase
from .js_event_stream import JSEventStream
from .rx.subject import Subject
from .rx_utils import merge_streams, timestamp


def get_on_next_data(origin: str) -> BrowserEvent:
    return BrowserEvent(origin)


class BrowserEventStream(EventStreamBase):

    # GUI Hooks
    searched_subj = Subject()
    row_changed_subj = Subject()
    # TODO: Close event

    # JS Events
    js_event_stream: JSEventStream

    def __init__(self):
        self.js_event_stream = JSEventStream(aqt.browser.Browser,
                                             get_on_next_data)
        self.__subscribe_to_gui_hooks()
        self.__create_main_stream()

    def __create_main_stream(self):
        self.main_subj = merge_streams(self.js_event_stream.main_subj,
                                       timestamp(self.searched_subj),
                                       timestamp(self.row_changed_subj))

    def __subscribe_to_gui_hooks(self):
        gui_hooks.browser_did_search.append(self.on_search)
        gui_hooks.browser_did_change_row.append(self.on_row_changed)

    def on_search(self, context: aqt.browser.SearchContext):
        self.searched_subj.on_next(BrowserEvent(
            BrowserEventOrigin.search.name))

    def on_row_changed(self, browser: aqt.browser.Browser):
        self.row_changed_subj.on_next(
            BrowserEvent(BrowserEventOrigin.row_changed.name))
