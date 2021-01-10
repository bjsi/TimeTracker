import datetime as dt
from typing import Dict


class CondensedEvent:

    start: dt.datetime
    duration: dt.timedelta
    data: Dict
    name: str

    def __init__(self, name: str, start: dt.datetime, end: dt.datetime,
                 data: Dict):
        self.start = start
        self.duration = end - start
        self.data = data
        self.name = name

    def to_dict(self):
        return {
            "start": self.start,
            "duration": self.duration,
            "name": self.name,
            "data": self.data
        }
