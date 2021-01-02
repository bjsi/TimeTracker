import multiprocessing
from typing import Any, Optional, List
import aqt
from aqt import mw
from anki.cards import Card
from aqt import gui_hooks
from aqt.reviewer import Reviewer
from .rx import operators as ops
from .rx.core.observable import Observable
from .rx.scheduler import ThreadPoolScheduler
from .rx.subject import Subject
from .anki_event import (MouseEvent, KeyboardEvent, QuestionShownEvent,
                         AnkiEvent, AnsweredEvent, AnswerShownEvent,
                         ReviewEndEvent)
from .rx_utils import (merge_streams, timestamp, emit_when, pairwise_buffer,
                       shift_right)
from .anki_event import AnkiEventPair
from .rx_debug import spy
from .js_event_stream import JSEventStream


class MainObserver:

    # Sheduler
    optimal_thread_count = multiprocessing.cpu_count()
    pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

    def __init__(self, *args: Observable):
        self.create_main_stream(*args)

    def create_main_stream(self, *args):
        merged = merge_streams(*args)
        merged.pipe(ops.observe_on(self.pool_scheduler)).subscribe()

    @staticmethod
    def condense_events(lis: List[Timestamp]):
        assert len(lis) > 1
        fst = lis[0]
        lst = lis[-1]
        duration = (lst.timestamp - fst.timestamp).total_seconds()
        print(f"Event: duration: {duration}")
