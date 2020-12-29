from rx.testing import (TestScheduler, ReactiveTest)
import unittest
from rx import operators as ops
from rx_utils import pairwise_buffer, merge_streams
from rx_debug import spy
from rx.core.observable import Observable
from anki_event import AnkiEvent, EventOrigin
from typing import List

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestAnkiEvents(unittest.TestCase):
    # def test_basic(self):
    #     scheduler: TestScheduler = TestScheduler()
    #     fst = AnkiEvent(1, EventOrigin.KEYBOARD_PRESSED)
    #     snd = AnkiEvent(1, EventOrigin.KEYBOARD_PRESSED)
    #     xs: Observable[AnkiEvent] = scheduler.create_hot_observable(
    #         on_next(201, fst),
    #         on_next(202, snd),
    #         on_completed(3),
    #     )

    #     res = scheduler.start(lambda: xs)
    #     assert res.messages == [on_next(201, str(fst)), on_next(202, str(snd))]

    def test_merged_pairwise_window(self):
        scheduler: TestScheduler = TestScheduler()
        # Mouse moved observable
        m_fst = AnkiEvent(1, EventOrigin.MOUSE_MOVED)
        m_snd = AnkiEvent(2, EventOrigin.MOUSE_MOVED)
        m_thd = AnkiEvent(1, EventOrigin.MOUSE_MOVED)
        ms: Observable[AnkiEvent] = scheduler.create_hot_observable(
            on_next(201, m_fst),
            on_next(203, m_snd),
            on_next(205, m_thd),
            on_completed(3),
        )

        # Keyboard pressed observable
        k_fst = AnkiEvent(1, EventOrigin.KEYBOARD_PRESSED)
        k_snd = AnkiEvent(2, EventOrigin.KEYBOARD_PRESSED)
        k_thd = AnkiEvent(1, EventOrigin.KEYBOARD_PRESSED)
        ks: Observable[AnkiEvent] = scheduler.create_hot_observable(
            on_next(202, k_fst),
            on_next(204, k_snd),
            on_next(206, k_thd),
            on_completed(3),
        )

        def filter_condition(pair: List[AnkiEvent]):
            fst = pair[0]
            snd = pair[1]
            return (fst.card_id != snd.card_id)

        def create():
            m = merge_streams(ms, ks)
            s = m.pipe(pairwise_buffer, ops.map(lambda x: x[0]))
            return s.pipe(
                ops.window(
                    m.pipe(pairwise_buffer, ops.filter(filter_condition))))

        res = scheduler.start(create)
        print(res.messages)
