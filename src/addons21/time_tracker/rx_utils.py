from .rx.core.observable import Observable
import rx
from .rx import operators as ops


# 1122334|
# pairwise_buffer()
# ([1, 1])([1, 2])([2, 2])([2, 3])([3, 3])([3])|
def pairwise_buffer(obs: Observable) -> Observable:
    return obs.pipe(ops.buffer_with_count(2, 1))


# 1-3-5-7
# -2-4-6-
# merge_streams()
# 1234567
def merge_streams(*obs: Observable) -> Observable:
    return rx.merge(*obs).pipe(ops.share())


# 0011011
# emit_when(lambda x: x == 0)
# 00--0--
# (alias for filter to make complex window operation more readable)
def emit_when(predicate):
    return ops.filter(predicate)


# Wraps the object in a timestamp
def timestamp(obs: Observable):
    return obs.pipe(ops.timestamp())


# 1-2-3-4-5
# -1-2-3-4-5
# shifts the event stream once to the right
def shift_right(obs: Observable):
    return obs.pipe(pairwise_buffer, ops.map(lambda x: x[0]))
