import multiprocessing
from typing import List

from anki.cards import Card
import aqt
from aqt import mw
from aqt import gui_hooks
from aqt.reviewer import Reviewer

from .rx import operators as ops
from .rx.scheduler import ThreadPoolScheduler
from .rx_utils import merge_streams, monitor_activity
from .rx.core.observable import Observable
from .addon_event_tracker import AddonEventStream


class MainObserver:

    # Sheduler
    optimal_thread_count = multiprocessing.cpu_count()
    pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

    # Global

    def __init__(self, *args):
        self.subscribe_to_merged_stream()
        mw.addon_time_tracker = AddonEventStream()

    def publish_data(self) -> Observable:
        pass

    def subscribe_to_merged_stream(self, *args):
        merged = merge_streams(*args)
        (merged.pipe(monitor_activity, ops.observe_on(
            self.pool_scheduler)).subscribe(self.publish_data))
