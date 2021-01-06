import unittest
from typing import List, Sequence

from rx import operators as ops
from rx.core.observable import Observable
from rx.testing import ReactiveTest, TestScheduler

from time_tracker.anki_event import (AnkiEventPair, KeyboardEvent, MouseEvent,
                                     QuestionShownEvent)
from time_tracker.rx_utils import emit_when, merge_streams, pairwise_buffer

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestAnkiEvents(unittest.TestCase):
    """
    Tests merging multiple streams of events and applying operators accross
    the merged stream.
    """
    @staticmethod
    def typename(obj):
        return type(obj).__name__

    @staticmethod
    def head(seq: Sequence):
        return seq[0]

    def setUp(self):
        self.scheduler: TestScheduler = TestScheduler()

    def test_basic_merge(self):
        # Mouse events
        ms = self.scheduler.create_hot_observable(on_next(201, MouseEvent(1)),
                                                  on_next(203, MouseEvent(1)))

        # Keyboard events
        ks = self.scheduler.create_hot_observable(
            on_next(202, KeyboardEvent(1)), on_next(204, KeyboardEvent(1)))

        def create():
            return merge_streams(ms, ks).pipe(ops.map(self.typename))

        res = self.scheduler.start(create)
        assert res.messages == [
            on_next(201, "MouseEvent"),
            on_next(202, "KeyboardEvent"),
            on_next(203, "MouseEvent"),
            on_next(204, "KeyboardEvent"),
        ]

    def test_merged_pairwise(self):
        # Mouse events
        ms = self.scheduler.create_hot_observable(on_next(201, MouseEvent(1)),
                                                  on_next(203, MouseEvent(1)))

        # Keyboard events
        ks = self.scheduler.create_hot_observable(
            on_next(202, KeyboardEvent(1)), on_next(204, KeyboardEvent(1)))

        def create():
            return merge_streams(ms, ks).pipe(ops.map(self.typename),
                                              pairwise_buffer, ops.map(str))

        res = self.scheduler.start(create)
        assert res.messages == [
            on_next(202, "['MouseEvent', 'KeyboardEvent']"),
            on_next(203, "['KeyboardEvent', 'MouseEvent']"),
            on_next(204, "['MouseEvent', 'KeyboardEvent']"),
        ]

    def test_merged_pairwise_head(self):
        # Mouse events
        ms = self.scheduler.create_hot_observable(on_next(201, MouseEvent(1)),
                                                  on_next(203, MouseEvent(1)))

        # Keyboard events
        ks = self.scheduler.create_hot_observable(
            on_next(202, KeyboardEvent(1)), on_next(204, KeyboardEvent(1)))

        def create():
            return merge_streams(ms, ks).pipe(ops.map(self.typename),
                                              pairwise_buffer,
                                              ops.map(lambda x: x[0]),
                                              ops.map(str))

        res = self.scheduler.start(create)
        assert res.messages == [
            on_next(202, 'MouseEvent'),
            on_next(203, 'KeyboardEvent'),
            on_next(204, 'MouseEvent'),
        ]

    def test_merged_pairwise_filtered(self):
        # Mouse events
        ms = self.scheduler.create_hot_observable(
            on_next(201, MouseEvent(1)),
            on_next(203, MouseEvent(2)),
            on_next(206, MouseEvent(1)),
        )

        # Keyboard events
        ks = self.scheduler.create_hot_observable(
            on_next(202, KeyboardEvent(1)), on_next(204, KeyboardEvent(2)),
            on_next(207, KeyboardEvent(2)))

        def create():
            return merge_streams(ms,
                                 ks).pipe(ops.map(lambda x: x.card_id),
                                          pairwise_buffer,
                                          ops.filter(lambda x: x[0] != x[1]),
                                          ops.map(str))

        res = self.scheduler.start(create)
        assert res.messages == [
            on_next(203, str([1, 2])),
            on_next(206, str([2, 1])),
            on_next(207, str([1, 2])),
        ]

    def test_complex_window(self):
        # Mouse events
        ms = self.scheduler.create_hot_observable(on_next(201, MouseEvent(1)),
                                                  on_next(203, MouseEvent(2)),
                                                  on_next(205, MouseEvent(3)))

        # Keyboard events
        ks = self.scheduler.create_hot_observable(
            on_next(202, KeyboardEvent(1)), on_next(204, KeyboardEvent(2)),
            on_next(206, KeyboardEvent(3)), on_next(208, KeyboardEvent(4)))

        def create():
            # Each event in each stream is timestamped
            kst = ks.pipe(ops.timestamp())
            mst = ms.pipe(ops.timestamp())
            # Streams merged
            m = merge_streams(mst, kst)
            ph = m.pipe(pairwise_buffer, ops.map(self.head))
            w = ph.pipe(
                ops.window(
                    m.pipe(
                        pairwise_buffer, ops.map(AnkiEventPair),
                        emit_when(lambda x: x.different_cards() or x.
                                  afk_timeout()))))
            return w.pipe(ops.flat_map(lambda x: x.pipe(ops.to_list())))

        res = self.scheduler.start(create)
        print(res.messages)
        # TODO:


if __name__ == "__main__":
    unittest.main()
