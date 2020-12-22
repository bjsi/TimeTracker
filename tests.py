from rx.testing import TestScheduler, ReactiveTest
import unittest
from rx import operators as op
from rx_utils import spy


on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSample(unittest.TestCase):

    def test_hello_word(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(
            220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
        i = [0]
        sum = [2 + 3 + 4 + 5]
        completed = [False]

        def create():
            def on_next(x):
                i[0] += 1
                sum[0] -= x

            def on_completed():
                completed[0] = True
            return xs.pipe(
                op.do_action(on_next=on_next, on_completed=on_completed),
            )

        scheduler.start(create)

        self.assertEqual(4, i[0])
        self.assertEqual(0, sum[0])
        assert(completed[0])
