import unittest

from rx import operators as ops
from rx.testing import ReactiveTest, TestScheduler

from time_tracker.rx_utils import merge_streams, monitor_activity, timestamp
from time_tracker.main_observer import MainObserver
from time_tracker.browser_event import BrowserEvent, BrowserEventOrigin
from time_tracker.reviewer_event import ReviewerEvent
from time_tracker.editor_event import EditorEvent
from time_tracker.deck_browser_event import DeckBrowserEvent

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestMultipleEventStreams(unittest.TestCase):
    """
    Tests merging multiple streams from different GUIs
    and resolving overlaps
    """
    def setUp(self):
        self.scheduler: TestScheduler = TestScheduler()

    def test_basic(self):
        events = [
            on_next(201, BrowserEvent("search")),
            on_next(202, BrowserEvent("search")),
            on_next(203, BrowserEvent("search")),
            on_next(204, EditorEvent("unfocus_field")),
            on_next(205, EditorEvent("unfocus_field")),
            on_next(206, DeckBrowserEvent("something")),
        ]
        xs = self.scheduler.create_hot_observable(events)

        def create():
            return xs.pipe(timestamp, monitor_activity,
                           ops.map(lambda x: type(x[0].value).condense(x)))

        res = self.scheduler.start(create)
        print(res.messages)
