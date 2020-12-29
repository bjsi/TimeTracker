from rx.core.observable import Observable
import rx
import rx.operators as ops
import functools


# [1, 2, 3, 4] => [[1, 2], [2, 3], [3, 4]]
def pairwise_buffer(obs: Observable) -> Observable:
    return obs.pipe(ops.buffer_with_count(2, 1))


# [[1,2,3],[1,2,3],[...]] => [1,1,2,2,3,3]
def merge_streams(*obs: Observable) -> Observable:
    return rx.merge(*obs).pipe(ops.share())
