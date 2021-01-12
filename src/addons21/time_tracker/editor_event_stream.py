import aqt
from aqt import gui_hooks
import anki

from .rx_utils import merge_streams, timestamp
from .event_stream_base import EventStreamBase
from .js_event_stream import JSEventStream
from .editor_event import EditorEvent, EditorEventOrigin
from .rx.subject import Subject


def on_next_data(origin: str) -> EditorEvent:
    return EditorEvent(origin)


class EditorEventStream(EventStreamBase):

    # GUI Hooks
    editor_did_focus_field: Subject = Subject()
    editor_did_init: Subject = Subject()
    editor_did_unfocus_field: Subject = Subject()

    # JS
    js_event_stream: JSEventStream

    def __init__(self):
        self.js_event_stream = JSEventStream(aqt.editor.Editor, on_next_data)
        self.__subscribe_to_gui_hooks()
        self.__create_main_stream()

    def __subscribe_to_gui_hooks(self):
        gui_hooks.editor_did_init.append(self.editor_opened)
        gui_hooks.editor_did_focus_field.append(self.field_focused)
        gui_hooks.editor_did_unfocus_field.append(self.field_unfocused)

    def __create_main_stream(self):
        self.main_subj = merge_streams(
            self.js_event_stream.main_subj,
            timestamp(self.editor_did_focus_field),
            timestamp(self.editor_did_init),
            timestamp(self.editor_did_unfocus_field))

    #################
    # Event Handler #
    #################

    def field_focused(self, note: anki.notes.Note, current_field_idx: int):
        self.editor_did_focus_field.on_next(
            EditorEvent(EditorEventOrigin.field_focused.name))

    def field_unfocused(self, changed: bool, note: anki.notes.Note,
                        current_field_idx: int):
        self.editor_did_unfocus_field.on_next(
            EditorEvent(EditorEventOrigin.field_unfocused.name))

    def editor_opened(self, editor: aqt.editor.Editor):
        self.editor_did_init.on_next(
            EditorEvent(EditorEventOrigin.editor_opened.name))
