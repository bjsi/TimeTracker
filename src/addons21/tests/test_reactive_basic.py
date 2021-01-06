from rx.testing import (TestScheduler, ReactiveTest)
from time_tracker.anki_event import ReviewerEvent
import unittest
from rx import operators as ops
from time_tracker.rx_utils import pairwise_buffer, merge_streams
from rx.core.observable import Observable

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class BasicReactiveTests(unittest.TestCase):
    def setUp(self):
        self.scheduler = TestScheduler()
        self.test_obs = self.scheduler.create_hot_observable(
            on_next(201, 1), on_next(202, 1), on_next(203, 2), on_next(204, 2),
            on_next(205, 3), on_next(206, 3), on_next(207, 4))

    def test_basic(self):
        def create():
            return self.test_obs

        res = self.scheduler.start(create)
        assert res.messages == [
            on_next(201, 1),
            on_next(202, 1),
            on_next(203, 2),
            on_next(204, 2),
            on_next(205, 3),
            on_next(206, 3),
            on_next(207, 4),
        ]

    def test_pairwise(self):
        def create():
            return self.test_obs.pipe(pairwise_buffer,
                                      ops.map(lambda x: str(x)))

        res = self.scheduler.start(create)
        assert res.messages == [
            on_next(202, str([1, 1])),
            on_next(203, str([1, 2])),
            on_next(204, str([2, 2])),
            on_next(205, str([2, 3])),
            on_next(206, str([3, 3])),
            on_next(207, str([3, 4])),
        ]

    def test_pairwise_head(self):
        def create():
            return self.test_obs.pipe(pairwise_buffer, ops.map(lambda x: x[0]))

        res = self.scheduler.start(create)
        assert res.messages == [
            on_next(202, 1),
            on_next(203, 1),
            on_next(204, 2),
            on_next(205, 2),
            on_next(206, 3),
            on_next(207, 3),
        ]

    def test_pairwise_filtered(self):
        def create():
            return self.test_obs.pipe(pairwise_buffer,
                                      ops.filter(lambda x: x[0] != x[1]))

        res = self.scheduler.start(create)
        assert res.messages == [
            on_next(203, str([1, 2])),
            on_next(205, str([2, 3])),
            on_next(207, str([3, 4])),
        ]

    def test_complex_window(self):
        def create():
            pfh = self.test_obs.pipe(pairwise_buffer, ops.map(lambda x: x[0]))
            w = pfh.pipe(
                ops.window(
                    self.test_obs.pipe(pairwise_buffer,
                                       ops.filter(lambda x: x[0] != x[1]))))
            return w.pipe(ops.flat_map(lambda x: x.pipe(ops.to_list())))

        res = self.scheduler.start(create)
        assert res.messages == [
            on_next(203, str([1, 1])),
            on_next(205, str([2, 2])),
            on_next(207, str([3, 3])),
        ]


if __name__ == "__main__":
    unittest.main()
