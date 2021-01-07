import time
from typing import Callable

from aqt import mw


def wait_until(predicate: Callable[[], bool],
               timeout_secs: float,
               period_secs=0.25) -> bool:
    mustend = time.time() + timeout_secs
    while time.time() < mustend:
        if predicate():
            return True
        time.sleep(period_secs)
    return False


def time_tracker_loaded() -> bool:
    return hasattr(mw, "addon_time_tracker")


if wait_until(time_tracker_loaded, 20):
    print("Loaded!")
else:
    print("Error!")
