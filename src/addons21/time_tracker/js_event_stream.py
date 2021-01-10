from typing import Any, Optional, Tuple, Callable, List
import aqt
from aqt import gui_hooks
from .rx.subject import Subject
from .rx_utils import merge_streams, timestamp
from .event_stream_base import EventStreamBase
from enum import Enum
from .event_base import EventBase


class JSEventOrigin(Enum):

    mouse_move = 1,
    mouse_scroll = 2,
    mouse_click = 3,
    keyboard_pressed = 4,


mouse_move = JSEventOrigin.mouse_move.name
keyboard_pressed = JSEventOrigin.keyboard_pressed.name
mouse_scroll = JSEventOrigin.mouse_scroll.name
mouse_click = JSEventOrigin.mouse_click.name


class JSEventStream(EventStreamBase):

    target_context: Any
    # prevent binding the function to the class
    next_data_func: List[Callable[[str], EventBase]]

    mouse_moved: Subject = Subject()
    mouse_scroll: Subject = Subject()
    mouse_click: Subject = Subject()
    keyboard_pressed: Subject = Subject()

    def __init__(self, context: Any, next_data_func: Callable[[str],
                                                              EventBase]):
        self.target_context = context
        self.next_data_func = [next_data_func]
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
        if not isinstance(context, self.target_context):
            return

        web_content.head += (f"""<script>
const throttle = (func, limit) => {{
  let lastFunc
  let lastRan
  return function() {{
    const context = this
    const args = arguments
    if (!lastRan) {{
      func.apply(context, args)
      lastRan = Date.now()
    }} else {{
      clearTimeout(lastFunc)
      lastFunc = setTimeout(function() {{
        if ((Date.now() - lastRan) >= limit) {{
          func.apply(context, args)
          lastRan = Date.now()
        }}
      }}, limit - (Date.now() - lastRan))
    }}
  }}
}}

document.addEventListener('click', throttle(function() {{
  return pycmd('{mouse_click}')
}}, 500));

document.addEventListener('keydown', throttle(function() {{
  return pycmd('{keyboard_pressed}')
}}, 500));

document.addEventListener('mousemove', throttle(function() {{
  return pycmd('{mouse_move}')
}}, 500));

document.addEventListener('scroll', throttle(function() {{
    return pycmd('{mouse_scroll}')
}}), 500);
</script>
                """)

    def get_next_data(self, origin: str):
        data = self.next_data_func[0](origin)
        return data

    def handle_js_message(self, handled: Tuple[bool, Any], message: str,
                          context: Any) -> Tuple[bool, Any]:
        if not isinstance(context, self.target_context):
            return handled

        if message == mouse_move:
            self.mouse_moved.on_next(self.get_next_data(mouse_move))
        elif message == keyboard_pressed:
            self.keyboard_pressed.on_next(self.get_next_data(keyboard_pressed))
        elif message == mouse_scroll:
            self.mouse_scroll.on_next(self.get_next_data(mouse_scroll))
        elif message == mouse_click:
            self.mouse_click.on_next(self.get_next_data(mouse_click))
        return handled
