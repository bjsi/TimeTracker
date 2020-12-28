import multiprocessing
from typing import Any, Optional, Tuple

import aqt
from anki.cards import Card
from aqt import gui_hooks
from aqt.reviewer import Reviewer
from rx import operators as op
from rx.core.observable import observable
from rx.scheduler import ThreadPoolScheduler
from rx.subject import Subject

# CONSTANTS
ADDON_NAME = "TimeTracker"
JS_FILE = f"_addons/{ADDON_NAME}/send_events_to_python.js"

# from aqt.qt import debug; debug()


class Events:

    # Individual event streams
    question_shown: Subject = Subject()
    mouse_moved: Subject = Subject()
    keyboard_pressed: Subject = Subject()
    mouse_click: Subject = Subject()

    # Merged event stream
    merged_stream: observable

    # Sheduler
    optimal_thread_count = multiprocessing.cpu_count()
    pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

    # constants
    TIMEOUT: int = 1000  # 1 second

    def __init__(self):
        self.__subscribe_to_gui_hooks()
        self.__create_event_stream()

    def __subscribe_to_gui_hooks(self):
        gui_hooks.webview_will_set_content(self.on_setting_content)
        gui_hooks.reviewer_did_show_question(self.on_question_shown)
        gui_hooks.webview_did_receive_js_message(self.on_mouse_moved)
        gui_hooks.webview_did_receive_js_message(self.on_keyboard_pressed)

    def on_setting_content(self, web_content: aqt.webview.WebContent,
                           context: Optional[Any]) -> None:
        if not self.is_reviewer(context):
            return

    def __create_event_stream(self):
        self.merged_stream = self.question_shown.pipe(
            op.merge(self.throttled(self.mouse_moved, self.TIMEOUT),
                     self.throttled(self.keyboard_pressed, self.TIMEOUT)), )

    @staticmethod
    def throttled(obs: observable,
                  timeout_ms: int,
                  scheduler=None) -> observable:
        return obs.pipe(
            op.throttle_with_timeout(timeout_ms, scheduler),
            op.map(lambda _: Reviewer.card)  # TODO: how to make this testable?
        )

    @staticmethod
    def is_reviewer(context: Any) -> bool:
        return isinstance(context, Reviewer)

    def on_question_shown(self, card: Card) -> None:
        self.question_shown.on_next(card)

    def on_mouse_moved(self, handled: Tuple[bool, Any], message: str,
                       context: Any) -> Tuple[bool, Any]:
        if message == "mousemove" and self.is_reviewer(context):
            self.mouse_moved.on_next()  # TODO args?
        return handled

    def on_keyboard_pressed(self, handled: Tuple[bool, Any], message: str,
                            context: Any) -> Tuple[bool, Any]:
        if message == "keydown" and self.is_reviewer(context):
            self.keyboard_pressed.on_next()  # TODO args?
        return handled

    def on_mouse_click(self, handled: Tuple[bool, Any], message: str,
                       context: Any):
        if message == "click" and self.is_reviewer(context):
            self.mouse_click.on_next()
        return handled


e = Events()
