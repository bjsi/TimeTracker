import anki
import aqt
from aqt import gui_hooks

from .card_adder_event import CardAdderEvent, CardAdderEventOrigin
from .event_stream_base import EventStreamBase
from .js_event_stream import JSEventStream
from .rx.subject import Subject
from .rx_utils import merge_streams, timestamp


def get_on_next_data(origin: str):
    return CardAdderEvent(origin)


class CardAdderEventStream(EventStreamBase):

    # GUI Hooks
    on_init_subj: Subject = Subject()
    added_note: Subject = Subject()

    # JS Events
    js_event_stream: JSEventStream

    def __init__(self):
        self.__subscribe_to_hooks()
        self.js_event_stream = JSEventStream(aqt.addcards.AddCards,
                                             get_on_next_data)
        self.__create_main_stream()

    def __create_main_stream(self) -> None:
        self.main_subj = merge_streams(self.js_event_stream.main_subj,
                                       timestamp(self.added_note),
                                       timestamp(self.on_init_subj))

    def __subscribe_to_hooks(self) -> None:
        gui_hooks.add_cards_did_add_note.append(self.on_note_added)
        gui_hooks.add_cards_did_init.append(self.on_add_cards_init)

    def on_add_cards_init(self, addcards: aqt.addcards.AddCards):
        self.on_init_subj.on_next(
            CardAdderEvent(CardAdderEventOrigin.opened_card_adder.name))

    def on_note_added(self, note: anki.notes.Note):
        self.added_note.on_next(
            CardAdderEvent(CardAdderEventOrigin.added_note.name, note))
