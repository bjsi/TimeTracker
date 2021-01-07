import multiprocessing
from typing import Dict, List

from aqt import mw

from .rx import operators as ops
from .rx.core.operators.timestamp import Timestamp
from .rx.scheduler import ThreadPoolScheduler
from .rx_utils import merge_streams, monitor_activity
from .addon_event_tracker import AddonEventStream


class MainObserver:

    # Sheduler
    optimal_thread_count = multiprocessing.cpu_count()
    pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

    def __init__(self, *args):
        self.subscribe_to_merged_stream(*args)
        mw.addon_time_tracker = AddonEventStream()

    @staticmethod
    def publish_data(events: List[Timestamp]):
        data: Dict = type(events[0].value).condense(events)
        mw.addon_time_tracker.raise_event(data)

    def subscribe_to_merged_stream(self, *args):
        merged = merge_streams(*args)
        (merged.pipe(monitor_activity, ops.observe_on(
            self.pool_scheduler)).subscribe(self.publish_data))
