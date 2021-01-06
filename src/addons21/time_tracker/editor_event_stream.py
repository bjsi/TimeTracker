from typing import Any, List, Optional, Tuple

from anki.cards import Card
import aqt
from aqt import mw
from aqt import gui_hooks
from aqt.reviewer import Reviewer
from .anki_event import AnkiEventPair

from .rx_utils import merge_streams
from .event_stream_base import EventStreamBase
from .js_event_stream import JSEventStream
from .editor_event import EditorEvent, EditorEventOrigin


def on_next_data(origin: str) -> EditorEvent:
    return EditorEvent(origin)


class EditorEventStream(EventStreamBase):

    ## Individual event streams
    # GUI Hooks

    # JS
    js_event_stream: JSEventStream

    def __init__(self):
        self.js_event_stream = JSEventStream(Editor, on_next_data)
        self.__subscribe_to_gui_hooks()
        self.__create_main_stream()

    def __subscribe_to_gui_hooks(self):
        pass

    def __create_main_stream(self):
        self.main_subj = merge_streams()
