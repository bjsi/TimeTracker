import multiprocessing
from typing import Dict, List
import sys

from aqt import mw

from .event_stream_base import EventStreamBase
from .rx import operators as ops
from .rx.core.operators.timestamp import Timestamp
from .rx.scheduler import ThreadPoolScheduler
from .rx_utils import merge_streams, monitor_activity
from .addon_event_tracker import AddonEventStream
from .rx.core.observable import Observable


class MainObserver:

    pool_scheduler = ThreadPoolScheduler(multiprocessing.cpu_count())
    merged: Observable

    def __init__(self, merged):
        self.merged = merged
        self.subscribe()

    def subscribe(self):
        (self.merged.pipe(
            monitor_activity,
            ops.map(lambda x: type(x[0].value).condense(x))).subscribe(print))
