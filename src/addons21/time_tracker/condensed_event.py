import datetime as dt
from typing import Dict

from .rx.core.operators.timestamp import Timestamp


class CondensedEvent:

    start: dt.datetime
    duration: dt.timedelta
    data: Dict

    def __init__(self, start: dt.datetime, end: dt.datetime, data: Dict):
        self.start = start
        self.duration = end - start
        self.data = data

    def to_dict(self):
        return {
            "start": self.start,
            "duration": self.duration,
            "data": self.data
        }
