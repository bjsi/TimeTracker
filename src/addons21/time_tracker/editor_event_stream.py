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


class EditorEventStream:

    ## Individual event streams
    # GUI Hooks

    # JS


    def __init__(self):
        self.subscribe_to_gui_hooks()

