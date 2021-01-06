import multiprocessing
from typing import Any, Optional
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
                         ReviewerEvent, AnsweredEvent, AnswerShownEvent,
                         ReviewEndEvent)
from .rx_utils import (merge_streams, timestamp, monitor_activity)
from .anki_event import AnkiEventPair
from .rx_debug import spy
from .js_event_stream import JSEventStream


class ReviewerEventStream:

    main_subj: Subject = Subject()

    ## Individual event streams
    # GUI Hooks
    question_shown: Subject = Subject()
    answer_shown: Subject = Subject()
    answered: Subject = Subject()
    review_ended: Subject = Subject()

    # JS Events
    js_event_stream: JSEventStream

    def __init__(self):
        self.js_event_stream = JSEventStream(aqt.reviewer.Reviewer,
                                             lambda: mw.reviewer.card.id)
        self.__subscribe_to_gui_hooks()
        self.__subscribe_to_event_stream()

    def __subscribe_to_gui_hooks(self):
        # Main GUI Hooks
        gui_hooks.reviewer_did_show_question.append(self.on_question_shown)
        gui_hooks.reviewer_did_show_answer.append(self.on_answer_shown)
        gui_hooks.reviewer_did_answer_card.append(self.on_answered)
        gui_hooks.reviewer_will_end.append(self.on_review_end)
        # JS Hooks
        gui_hooks.webview_will_set_content.append(self.on_setting_content)
        gui_hooks.webview_did_receive_js_message.append(self.handle_js_message)

    @staticmethod
    def is_reviewer(context: Any) -> bool:
        return isinstance(context, Reviewer)

    ##################
    # Event Handlers #
    ##################

    def on_answered(self, reviewer: Reviewer, card: Card, ease: int):
        self.answered.on_next(AnsweredEvent(card.id))

    def on_review_end(self) -> None:
        card_id = mw.reviewer.card.id
        self.review_ended.on_next(ReviewEndEvent(card_id))

    def on_question_shown(self, card: Card) -> None:
        self.question_shown.on_next(QuestionShownEvent(card.id))

    def on_answer_shown(self, card: Card) -> None:
        self.answer_shown.on_next(AnswerShownEvent(card.id))

    ######################
    # Create Main Stream #
    ######################

    def __subscribe_to_event_stream(self):
        """
        Create the merged event stream and subscribe to it.
        """

        self.main_subj = merge_streams(self.js_event_stream.main_subj,
                                       timestamp(self.question_shown),
                                       timestamp(self.answer_shown),
                                       timestamp(self.answered),
                                       timestamp(self.review_ended))
