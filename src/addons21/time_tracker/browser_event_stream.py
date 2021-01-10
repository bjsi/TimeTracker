import aqt
from aqt import gui_hooks

from .browser_event import BrowserEvent, BrowserEventOrigin
from .event_stream_base import EventStreamBase
from .js_event_stream import JSEventStream
from .rx.subject import Subject
from .rx_utils import merge_streams, timestamp
from .qt_window_hooks import monkey_patch_close_event


def get_on_next_data(origin: str) -> BrowserEvent:
    return BrowserEvent(origin)


class BrowserEventStream(EventStreamBase):

    # GUI Hooks
    opened_subj = Subject()
    searched_subj = Subject()
    row_changed_subj = Subject()
    closed = Subject()

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
                                       timestamp(self.opened_subj),
                                       timestamp(self.closed),
                                       timestamp(self.row_changed_subj))

    def __subscribe_to_gui_hooks(self):
        gui_hooks.browser_did_search.append(self.on_search)
        gui_hooks.browser_did_change_row.append(self.on_row_changed)
        gui_hooks.browser_will_show.append(self.on_show)
        monkey_patch_close_event(aqt.browser.Browser, self.on_closed)

    #################
    # Even Handlers #
    #################

    def on_closed(self, _):
        self.closed.on_next(BrowserEvent(BrowserEventOrigin.closed.name))

    def on_search(self, _: aqt.browser.SearchContext):
        self.searched_subj.on_next(BrowserEvent(
            BrowserEventOrigin.search.name))

    def on_show(self, _: aqt.browser.Browser):
        self.opened_subj.on_next(BrowserEvent(BrowserEventOrigin.opened.name))

    def on_row_changed(self, _: aqt.browser.Browser):
        self.row_changed_subj.on_next(
            BrowserEvent(BrowserEventOrigin.row_changed.name))
