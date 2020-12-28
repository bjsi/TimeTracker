from rx.testing import (TestScheduler, ReactiveTest)
import unittest
from rx import operators as ops
from rx_utils import pairwise_buffer, merge_streams
from rx_debug import spy

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSample(unittest.TestCase):
    # def test_pairwise_buffer(self):
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

    #     res = scheduler.start(create)
    #     assert res.messages == [
    #         on_next(240, str([2, 3])),
    #         on_next(280, str([3, 4])),
    #         on_next(320, str([4, 5])),
    #         on_next(350, str([5, 6])),
    #     ]

    def test_merged_pairwise_buffer(self):
        scheduler: TestScheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(100, 1),
            on_next(210, 2),
            on_next(240, 3),
            on_next(280, 4),
            on_next(320, 5),
            on_next(350, 6),
            on_completed(3),
        )

        ys = scheduler.create_hot_observable(
            on_next(101, 1),
            on_next(211, 2),
            on_next(241, 3),
            on_next(281, 4),
            on_next(321, 5),
            on_next(351, 6),
            on_completed(3),
        )

        def create():
            return merge_streams(xs, ys).pipe(spy)

        scheduler.start(create)

    # def test_spy(self):
    #     """
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
    #         return xs.pipe(pairwise_buffer, ops.map(lambda x: str(x)), spy)

    #     scheduler.start(create)
