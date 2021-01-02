import multiprocessing
from typing import Any, Optional, Tuple, List
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
import anki
from js_event_stream import JSEventStream


class AddingCardsEvent:

    added_note: bool = True
    note: anki.notes.Note

    def __init__(self, note: anki.notes.Note = None):
        if note:
            self.added_note = True
            self.note = note

    def __repr__(self):
        return f"<AddingCardsEvent: added?: {self.added_note}>"


class AddCardsEventStream:

    main_subj: Subject = Subject()

    ## Individual event streams
    # GUI Hooks
    on_init_subj: Subject = Subject()
    added_note: Subject = Subject()
    # TODO: On closed event?

    # JS Events
    js_event_stream: JSEventStream

    def __init__(self):
        self.subscribe_to_hooks()
        self.js_event_stream = JSEventStream(aqt.addcards.AddCards,
                                             AddingCardsEvent)
        self.create_main_stream()

    def create_main_stream(self):
        self.main_subj = merge_streams(self.js_event_stream,
                                       timestamp(self.added_note),
                                       timestamp(self.on_init_subj))

    def subscribe_to_hooks(self):
        gui_hooks.add_cards_did_add_note.append(self.on_note_added)
        gui_hooks.add_cards_did_init.append(self.on_add_cards_init)

    def on_add_cards_init(self, addcards: aqt.addcards.AddCards):
        self.on_init_subj.on_next(AddingCardsEvent())

    def on_note_added(self, note: anki.notes.Note):
        self.added_note.on_next(note)
