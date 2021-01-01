from .rx.core.observable import Observable
import rx
from .rx import operators as ops


# [1, 2, 3, 4] => [[1, 2], [2, 3], [3, 4]]
def pairwise_buffer(obs: Observable) -> Observable:
    return obs.pipe(ops.buffer_with_count(2, 1))


# [[1,2,3],[1,2,3],[...]] => [1,1,2,2,3,3]
def merge_streams(*obs: Observable) -> Observable:
    return rx.merge(*obs).pipe(ops.share())


# Alias for filter
def emit_when(predicate):
    return ops.filter(predicate)


def timestamp(obs: Observable):
    return obs.pipe(ops.timestamp())


def shift_right(obs: Observable):
    return obs.pipe(pairwise_buffer, ops.map(lambda x: x[0]))
