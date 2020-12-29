from rx.testing import (TestScheduler, ReactiveTest)
import unittest
from rx import operators as ops
from rx_utils import pairwise_buffer, merge_streams
from rx_debug import spy
from rx.core.observable import Observable

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSample(unittest.TestCase):
    def test_pairwise_buffer(self):
        scheduler: TestScheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 2),
            on_next(240, 3),
            on_next(280, 4),
            on_next(320, 5),
            on_next(350, 6),
            on_completed(3),
        )

        def create():
            return xs.pipe(pairwise_buffer, ops.map(lambda x: str(x)))

        res = scheduler.start(create)
        assert res.messages == [
            on_next(240, str([2, 3])),
            on_next(280, str([3, 4])),
            on_next(320, str([4, 5])),
            on_next(350, str([5, 6])),
        ]

    def test_merge_streams(self):
        scheduler: TestScheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 2),
            on_next(240, 3),
            on_next(280, 4),
            on_next(320, 5),
            on_next(350, 6),
            on_completed(3),
        )

        ys = scheduler.create_hot_observable(
            on_next(211, 2),
            on_next(241, 3),
            on_next(281, 4),
            on_next(321, 5),
            on_next(351, 6),
            on_completed(3),
        )

        def create() -> Observable:
            return merge_streams(xs, ys)

        res = scheduler.start(create)
        assert res.messages == [
            on_next(210, str(2.0)),
            on_next(211, str(2.0)),
            on_next(240, str(3.0)),
            on_next(241, str(3.0)),
            on_next(280, str(4.0)),
            on_next(281, str(4.0)),
            on_next(320, str(5.0)),
            on_next(321, str(5.0)),
            on_next(350, str(6.0)),
            on_next(351, str(6.0)),
        ]

    def test_merged_pairwise_buffer(self):
        scheduler: TestScheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 2),
            on_next(240, 3),
            on_next(280, 4),
            on_completed(3),
        )

        ys = scheduler.create_hot_observable(
            on_next(211, 2),
            on_next(241, 3),
            on_next(281, 4),
            on_completed(3),
        )

        def create() -> Observable:
            return merge_streams(xs, ys).pipe(pairwise_buffer)

        res = scheduler.start(create)
        assert res.messages == [
            on_next(211, str([2, 2])),
            on_next(240, str([2, 3])),
            on_next(241, str([3, 3])),
            on_next(280, str([3, 4])),
            on_next(281, str([4, 4])),
        ]

    def test_merged_windowed_pairwise_buffer(self):
        scheduler: TestScheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 2),
            on_next(240, 3),
            on_next(280, 4),
            on_completed(3),
        )

        ys = scheduler.create_hot_observable(
            on_next(211, 2),
            on_next(241, 3),
            on_next(281, 4),
            on_completed(3),
        )

        def create() -> Observable:
            m = merge_streams(xs, ys)
            s = m.pipe(pairwise_buffer, ops.map(lambda x: x[0]))
            return s.pipe(ops.window(m), spy)

        scheduler.start(create)

        # def test_spy(self):
        #     "
        #     Run to test the spy function.
        #     """
        #     scheduler: TestScheduler = TestScheduler()
        #     xs = scheduler.create_hot_observable(
        #         on_next(100, 1),
        #         on_next(210, 2),
        #         on_next(240, 3),
        #         on_next(280, 4),
        #         on_next(320, 5),
        #         on_next(350, 6),
        #         on_completed(3),
        #     )

        #     def create():
        #         return xs.pipe(pairwise_buffer, ops.map(lambda x: str(x)))
