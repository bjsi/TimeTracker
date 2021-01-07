from anki.cards import Card
import aqt
from aqt import mw
from aqt import gui_hooks
from aqt.reviewer import Reviewer
from typing import List, Any

from .js_event_stream import JSEventStream
from .rx.subject import Subject
from .rx_utils import merge_streams, timestamp
from .event_stream_base import EventStreamBase
from .reviewer_event import ReviewerEvent, ReviewerEventOrigin
from .event_base import EventBase


def get_on_next_data(origin: str) -> EventBase:
    return ReviewerEvent(origin, mw.reviewer.card)


class ReviewerEventStream(EventStreamBase):

    # GUI Hooks
    question_shown: Subject = Subject()
    answer_shown: Subject = Subject()
    answered: Subject = Subject()
    review_ended: Subject = Subject()

    # JS Events
    js_event_stream: JSEventStream

    def __init__(self):
        self.js_event_stream = JSEventStream(aqt.reviewer.Reviewer,
                                             get_on_next_data)
        self.__subscribe_to_gui_hooks()
        self.__create_event_stream()

    def __subscribe_to_gui_hooks(self) -> None:
        # Main GUI Hooks
        gui_hooks.reviewer_did_show_question.append(self.on_question_shown)
        gui_hooks.reviewer_did_show_answer.append(self.on_answer_shown)
        gui_hooks.reviewer_did_answer_card.append(self.on_answered)
        gui_hooks.reviewer_will_end.append(self.on_review_end)

    @staticmethod
    def is_reviewer(context: Any) -> bool:
        return isinstance(context, Reviewer)

    ##################
    # Event Handlers #
    ##################

    def on_answered(self, reviewer: Reviewer, card: Card, ease: int) -> None:
        origin = ReviewerEventOrigin.answered.name
        self.answered.on_next(ReviewerEvent(origin, card))

    def on_review_end(self) -> None:
        card = mw.reviewer.card
        origin = ReviewerEventOrigin.review_ended.name
        self.review_ended.on_next(ReviewerEvent(origin, card))

    def on_question_shown(self, card: Card) -> None:
        origin = ReviewerEventOrigin.question_shown.name
        self.question_shown.on_next(ReviewerEvent(origin, card))

    def on_answer_shown(self, card: Card) -> None:
        origin = ReviewerEventOrigin.answer_shown.name
        self.answer_shown.on_next(ReviewerEvent(origin, card))

    ######################
    # Create Main Stream #
    ######################

    def __create_event_stream(self):

        self.main_subj = merge_streams(self.js_event_stream.main_subj,
                                       timestamp(self.question_shown),
                                       timestamp(self.answer_shown),
                                       timestamp(self.answered),
                                       timestamp(self.review_ended))
