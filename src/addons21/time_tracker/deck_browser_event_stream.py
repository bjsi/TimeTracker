import multiprocessing
from typing import Any, Optional, Tuple, List
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


class DeckBrowserEventStream:

    main_subj: Subject = Subject()

    ## Individual event streams
    # GUI Hooks

    browser_rendered: Subject = Subject()
    # JS
    js_event_stream: JSEventStream

    def __init__(self):
        self.subscribe_to_hooks()
        self.js_event_stream = JSEventStream()
        self.create_main_stream()

    def create_main_stream(self):
        self.main_subj = merge_streams(self.js_event_stream.main_subj,
                                       timestamp(self.browser_rendered))

    def subscribe_to_hooks(self):
        gui_hooks.deck_browser_did_render.append()

    def on_deck_browser_rendered(self):
        self.browser_rendered.on_next(?)
