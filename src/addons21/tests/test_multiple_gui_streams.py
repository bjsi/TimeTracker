import unittest
from typing import List, Sequence

from rx import operators as ops
from rx.core.observable import Observable
from rx.testing import ReactiveTest, TestScheduler

from time_tracker.anki_event import (AnkiEventPair, KeyboardEvent, MouseEvent,
                                     QuestionShownEvent)
from time_tracker.rx_utils import emit_when, merge_streams, pairwise_buffer
from time_tracker.main_observer import MainObserver

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class ReviewerEvent:
    id: int

    def __init__(self, id: int):
        self.id = id


class NoteAdderEvent:
    added_note: bool

    def __init__(self, added: bool):
        self.added_note = added


class TestMultipleGuiEventStreams(unittest.TestCase):
    """
    Tests merging multiple streams from different GUIs
    and resolving overlaps
    """
    def setUp(self):
        self.scheduler: TestScheduler = TestScheduler()

    def test_main_observer(self):
        xs = self.scheduler.create_hot_observable(
            on_next(201, NoteAdderEvent(True)),
            on_next(202, NoteAdderEvent(False)),
            on_next(203, ReviewerEvent(1)),
            on_next(204, ReviewerEvent(1)),
            on_next(205, ReviewerEvent(2)),
            on_next(205, ReviewerEvent(2)))
        main_obs = MainObserver(xs)
        main_obs.
