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


class BrowserEventStream:

    ## Individual event streams
    # GUI Hooks
    searched_subj = Subject()
    row_changed_subj = Subject()

    # JS Events
    js_event_stream: JSEventStream

    # Main
    main_subj: Subject = Subject()

    def __init__(self):
        self.js_event_stream = JSEventStream(aqt.browser.Browser,
                lambda: mw.browser.?)
        self.__subscribe_to_gui_hooks()
        self.create_main_stream()

    def create_main_stream():
        self.main_subj = merge_streams(
                self.js_event_stream.main_subj,
                timestamp(self.searched_subj),
                timestamp(self.row_changed_subj))

    def __subscribe_to_gui_hooks(self):
        # GUI Hooks
        gui_hooks.browser_did_search.append(self.on_search)
        gui_hooks.browser_did_change_row.append(self.on_row_changed)

    @staticmethod
    def is_browser(context: Any):
        return isinstance(context, aqt.browser.Browser)

    def on_search(self, context: aqt.browser.SearchContext):
        self.searched.on_next()

    def on_row_changed(self, browser: aqt.browser.Browser):
        self.row_changed.on_next()
