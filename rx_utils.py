import rx
from typing import Callable, Optional, Any
import threading
from rx.core import Observer
from rx.core.observable import Observable
from rx.disposable import Disposable, CompositeDisposable
from rx.operators import do_action
from rx.scheduler.scheduler import Scheduler


def get_thread_id() -> int:
    return threading.current_thread().ident


class SubscriptionLambda:

    t: Any
    obs: Observer
    logger: Callable[[str], None] = lambda x: print(x)
    op_name: str

    def __init__(self, t: Any, obs: Observer, op_name: str = "Observable", logger: Callable[[str], None] = lambda x: print(x)):
        self.t = t
        self.obs = obs
        self.logger = logger
        self.op_name = op_name

    def create(self):
        try:
            self.obs.on_next(self.t)
        except Exception as ex:
            self.logger(f"{self.op_name}: Downstream exception ({ex}) on Thread: {get_thread_id()}")


class DisposableCreationLambda:

    logger: Callable[[str], None]
    op_name: str
    count: int = 0
    source: Observable
    i_lock = threading.Lock()

    def __init__(self, source: Observable, op_name: str = "Observable", logger: Callable[[str], None] = lambda x: print(x)):
        self.source = source
        self.op_name = op_name
        self.logger = logger

    def threadsafe_increment_count(self):
        self.i_lock.acquire()
        try:
            self.count += 1
        finally:
            self.i_lock.release()

    def threadsafe_decrement_count(self):
        self.i_lock.acquire()
        try:
            self.count -= 1
        finally:
            self.i_lock.release()

    def create(self, obs: Observer, scheduler: Optional[Scheduler] = None) -> CompositeDisposable:
        self.logger(f"{self.op_name}: Subscribed to on Thread: {get_thread_id()}")
        try:
            subscription = self.source.pipe(
                do_action(
                    on_next=lambda x: self.logger(f"{self.op_name}: OnNext({x}) on Thread: {get_thread_id()}"),
                    on_error=lambda x: self.logger(f"{self.op_name}: OnError({x}) on Thread: {get_thread_id()}"),
                    on_completed=lambda: self.logger(f"{self.op_name}: OnCompleted() on Thread: {get_thread_id()}")
                )
            ).subscribe(
                on_next=lambda t: SubscriptionLambda(t, obs, self.op_name, self.logger).create(),
                on_error=lambda ex: obs.on_error(ex),
                on_completed=lambda: obs.on_completed(),
                scheduler=scheduler
            )

            return CompositeDisposable(
                Disposable(lambda: self.logger(f"{self.op_name}: Dispose (Unsubscribe or Observable finished) on Thread: {get_thread_id()}")),
                subscription,
                Disposable(lambda: self.threadsafe_decrement_count()),
                Disposable(lambda: self.logger(f"{self.op_name}: Dispose (Unsubscribe or Observable finished) completed, {self.count} subscriptions"))
            )
        finally:
            self.threadsafe_increment_count()
            self.logger(f"{self.op_name}: Subscription completed, {self.count} subscriptions.")


def spy(source: Observable, operation_name: str = "Observable", logger: Callable[[str], None] = lambda x: print(x)) -> Observable:
    """
    Allows you to log what a reactive extensions operation is doing.
    Helpful when debugging.
    translated to python from: https://stackoverflow.com/questions/20220755/how-can-i-see-what-my-reactive-extensions-query-is-doing
    TODO: Had to swap out the multiline lambdas for classes, v. ugly, refactor

    :param source: The source observable.
    :param operation_name: Human readable name of the operation, or "Observable".
    :param logger: Optional logger, or print.
    :return: Returns the observable.
    """

    logger(f"{operation_name}: Observable obtained on Thread: {get_thread_id()}")
    return rx.create(DisposableCreationLambda(source, operation_name, logger).create)
