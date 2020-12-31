import threading
from typing import Any, Callable, Optional

import rx
from rx.core import Observer
from rx.core.observable import Observable
from rx.disposable import CompositeDisposable, Disposable
from rx.operators import do_action
from rx.scheduler.scheduler import Scheduler

# log messages
NEXT = "{}: OnNext({}) on thread {}"
ERROR = "{}: OnError({}) on thread {}"
COMPLETED = "{}: OnComplete() on thread {}"
OBTAINED = "{}: Obtained on thread {}"
SUBSCRIBED = "{}: Subscribed to on thread {}"
EXCEPTION = "{}: Downstream exception {} on thread {}"
DISPOSE = "{}: Dispose (Unsub or Observable finished) on thread: {}"
DISPOSE_COMPLETE = "{}: Dispose (Unsub or Observable finished) completed, {} subscriptions"


def thrd_id():
    return threading.current_thread().ident


def spy(source: Observable,
        name: str = "Observable",
        logger: Callable[[str], None] = print):

    count = 0
    logger(OBTAINED.format(name, thrd_id()))
    i_lock = threading.Lock()

    def deccnt():
        i_lock.acquire()
        try:
            nonlocal count
            count -= 1
        finally:
            i_lock.release()

    def inccnt():
        i_lock.acquire()
        try:
            nonlocal count
            count += 1
        finally:
            i_lock.release()

    def subscribe(obs: Observable, scheduler: Optional[Scheduler] = None):
        def on_next(t: Any):
            try:
                obs.on_next(t)
            except Exception as e:
                logger(EXCEPTION.format(name, e))
                raise

        logger(SUBSCRIBED.format(name, thrd_id()))
        try:
            subscription = source.pipe(
                do_action(
                    on_next=lambda x: logger(NEXT.format(name, x, thrd_id())),
                    on_error=lambda ex: logger(
                        ERROR.format(name, ex, thrd_id())),
                    on_completed=lambda: logger(
                        COMPLETED.format(name, thrd_id())))).subscribe(
                            on_next=lambda x: on_next(x),
                            on_error=lambda x: obs.on_error(x),
                            on_completed=lambda: obs.on_completed())
            return CompositeDisposable(
                Disposable(lambda: logger(DISPOSE.format(name, thrd_id()))),
                subscription, Disposable(lambda: deccnt()),
                Disposable(
                    lambda: logger(DISPOSE_COMPLETE.format(name, count))))
        finally:
            inccnt()
            logger("{}: Subscription completed with {} subscriptions".format(
                name, count))

    return rx.create(subscribe)
