import multiprocessing
import os
from typing import Any, List, Optional, Tuple
from aqt import gui_hooks
from aqt.deckbrowser import DeckBrowser

from .deck_browser_event import DeckBrowserEvent, DeckBrowserEventOrigin
from .rx.subject import Subject
from .rx_utils import merge_streams, timestamp
from .event_stream_base import EventStreamBase
from .js_event_stream import JSEventStream


def get_on_next_data(origin: str):
    return DeckBrowserEvent(origin)


class DeckBrowserEventStream(EventStreamBase):

    browser_rendered: Subject = Subject()

    js_event_stream: JSEventStream

    def __init__(self):
        self.__subscribe_to_hooks()
        self.js_event_stream = JSEventStream(DeckBrowser, get_on_next_data)
        self.__create_main_stream()

    def __create_main_stream(self):
        self.main_subj = merge_streams(self.js_event_stream.main_subj,
                                       timestamp(self.browser_rendered))

    def __subscribe_to_hooks(self):
        gui_hooks.deck_browser_did_render.append(self.on_deck_browser_rendered)

    ##################
    # Event Handlers #
    ##################

    def on_deck_browser_rendered(self, _):
        self.browser_rendered.on_next(
            DeckBrowserEvent(DeckBrowserEventOrigin.opened_browser.name))
