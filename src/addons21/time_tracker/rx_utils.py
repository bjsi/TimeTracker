from typing import List

import rx

from .rx import operators as ops
from .rx.core.operators.timestamp import Timestamp
from .rx.core.observable import Observable


# 1122334|
# pairwise_buffer()
# ([1, 1])([1, 2])([2, 2])([2, 3])([3, 3])([3])|
def pairwise_buffer(obs: Observable) -> Observable:
    return obs.pipe(ops.buffer_with_count(2, 1))


# 1-3-5-7
# -2-4-6-
# merge_streams()
# 1234567
def merge_streams(*obs) -> Observable:
    return rx.merge(*obs).pipe(ops.share())


# 0011011
# emit_when(lambda x: x == 0)
# 00--0--
# (alias for filter to make complex window operation more readable)
def emit_when(predicate):
    return ops.filter(predicate)


# Wraps the object in a timestamp
def timestamp(obs):
    return obs.pipe(ops.timestamp())


# 1-2-3-4-5
# -1-2-3-4-5
# shifts the event stream once to the right
def shift_right(obs):
    return obs.pipe(pairwise_buffer, ops.map(lambda x: x[0]))


def window_border_condition_met(pair: List[Timestamp]):
    assert len(pair) == 2
    return type(pair[0].value).should_window(pair)


def monitor_activity(merged):
    # Simply shift each event right by one time step
    # 1-2-3-4-5
    # shift_right()
    # -1-2-3-4-5
    shifted = merged.pipe(shift_right)

    # pairwise iteration over the original stream, each time
    # there is a pair for which the window_border_condition_met
    # returns true, the window emits an item, splitting the shifted stream, closing the last window and opening a new one
    windowed = shifted.pipe(
        ops.window(
            merged.pipe(pairwise_buffer,
                        emit_when(window_border_condition_met)))).pipe(
                            ops.flat_map(lambda x: x.pipe(ops.to_list())),
                            ops.filter(lambda x: len(x) > 1))

    return windowed
