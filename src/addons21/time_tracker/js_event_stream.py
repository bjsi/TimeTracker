from typing import Any, Optional, Tuple, List, Callable
import os
import aqt
from aqt import mw
from anki.cards import Card
from aqt import gui_hooks
from aqt.reviewer import Reviewer
from .rx import operators as ops
from .rx.core.observable import observable
from .rx.scheduler import ThreadPoolScheduler
from .rx.subject import Subject
from .anki_event import (MouseEvent, KeyboardEvent, QuestionShownEvent,
                         AnkiEvent, AnsweredEvent, AnswerShownEvent,
                         ReviewEndEvent)
from .rx_utils import (merge_streams, timestamp, emit_when, pairwise_buffer,
                       shift_right)
from .anki_event import AnkiEventPair
from .rx_debug import spy


class JSEventStream:

    # Main event stream
    main_subj = Subject()
    typ: Any
    get_on_next_data: Callable[[], Any]

    # Individual event streams
    mouse_moved: Subject = Subject()
    mouse_scroll: Subject = Subject()
    mouse_click: Subject = Subject()
    keyboard_pressed: Subject = Subject()

    def __init__(self, typ: Any, get_on_next_data: Callable[[...], Any]):
        self.typ = typ
        self.get_on_next_data = get_on_next_data
        self.subscribe_to_gui_hooks()
        self.create_main_stream()

    def create_main_stream(self):
        self.main_subj = merge_streams(timestamp(self.mouse_moved),
                                       timestamp(self.mouse_scroll),
                                       timestamp(self.mouse_click),
                                       timestamp(self.keyboard_pressed))

    def subscribe_to_gui_hooks(self):
        gui_hooks.webview_will_set_content.append(self.on_setting_content)
        gui_hooks.webview_did_receive_js_message.append(self.handle_js_message)

    def on_setting_content(self, web_content: aqt.webview.WebContent,
                           context: Optional[Any]) -> None:
        if not self.is_type(context):
            return
        # TODO:
        # addon_package = mw.addonManager.addonFromModule(__name__)
        # js_file = f"/_addons/{addon_package}/web/send_events_to_python.js"
        # web_content.js.append(js_file)
        web_content.head += ("""<script>
const throttle = (func, limit) => {
  let lastFunc
  let lastRan
  return function() {
    const context = this
    const args = arguments
    if (!lastRan) {
      func.apply(context, args)
      lastRan = Date.now()
    } else {
      clearTimeout(lastFunc)
      lastFunc = setTimeout(function() {
        if ((Date.now() - lastRan) >= limit) {
          func.apply(context, args)
          lastRan = Date.now()
        }
      }, limit - (Date.now() - lastRan))
    }
  }
}

document.addEventListener('click', throttle(function() {
  return pycmd('click')
}, 500));

document.addEventListener('keydown', throttle(function() {
  return pycmd('keydown')
}, 500));

document.addEventListener('mousemove', throttle(function() {
  return pycmd('mousemove')
}, 500));

document.addEventListener('scroll', throttle(function() {
    return pycmd('scroll')
}), 500);
</script>
                """)

    def handle_js_message(self, handled: Tuple[bool, Any], message: str,
                          context: Any) -> Tuple[bool, Any]:
        if self.is_type(context):
            if message == "mousemove":
                self.mouse_moved.on_next(self.get_on_next_data())
            elif message == "keydown":
                self.keyboard_pressed.on_next()
            elif message == "scroll":
                self.mouse_scroll.on_next()
            elif message == "click":
                self.mouse_click.on_next()
        return handled

    def is_type(self, context: Any) -> bool:
        return isinstance(context, self.typ)
