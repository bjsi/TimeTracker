from rx.testing import (TestScheduler, ReactiveTest)
import unittest
from rx import operators as ops
from rx_utils import pairwise_buffer, merge_streams
from rx_debug import spy
from rx.core.observable import Observable
from anki_event import AnkiEvent, EventOrigin

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestAnkiEvents(unittest.TestCase):
    def test_basic(self):
        scheduler: TestScheduler = TestScheduler()
        fst = AnkiEvent(1, EventOrigin.KEYBOARD_PRESSED)
        snd = AnkiEvent(1, EventOrigin.KEYBOARD_PRESSED)
        xs: Observable[AnkiEvent] = scheduler.create_hot_observable(
            on_next(201, fst),
            on_next(202, snd),
            on_completed(3),
        )

        res = scheduler.start(lambda: xs)
        assert res.messages == [on_next(201, str(fst)), on_next(202, str(snd))]
