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


class Events:

    # Individual event streams
    question_shown: Subject = Subject()
    answer_shown: Subject = Subject()
    answered: Subject = Subject()
    review_ended: Subject = Subject()
    mouse_moved: Subject = Subject()
    keyboard_pressed: Subject = Subject()
    mouse_click: Subject = Subject()
    mouse_scroll: Subject = Subject()

    # Sheduler
    optimal_thread_count = multiprocessing.cpu_count()
    pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

    def __init__(self):
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

    def on_answered(self, reviewer: Reviewer, card: Card, ease: int):
        self.answered.on_next(AnsweredEvent(card.id))

    def on_review_end(self) -> None:
        card_id = mw.reviewer.card.id
        self.review_ended.on_next(ReviewEndEvent(card_id))

    def on_setting_content(self, web_content: aqt.webview.WebContent,
                           context: Optional[Any]) -> None:
        if not self.is_reviewer(context):
            return
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
}, 1000));

document.addEventListener('keydown', throttle(function() {
  return pycmd('keydown')
}, 1000));

document.addEventListener('mousemove', throttle(function() {
  return pycmd('mousemove')
}, 1000));

document.addEventListener('scroll', throttle(function() {
    return pycmd('scroll')
}), 1000);
</script>
                """)

    def __subscribe_to_event_stream(self):
        """
        Create the merged event stream and subscribe to it.
        """

        # Timetamp each event from each stream and merge into
        # a master stream
        # -1-3-5-7
        # 0-2-4-6-
        # merge()
        # 1234567
        merged = merge_streams(timestamp(self.mouse_moved),
                               timestamp(self.mouse_scroll),
                               timestamp(self.mouse_click),
                               timestamp(self.keyboard_pressed),
                               timestamp(self.question_shown),
                               timestamp(self.answer_shown),
                               timestamp(self.answered),
                               timestamp(self.review_ended))

        # Simply shift each event right by one time step
        # 1-2-3-4-5
        # shift_right()
        # -1-2-3-4-5
        shifted = merged.pipe(shift_right)

        # Each new event is compared with the event before it.
        # If the card id is different, or the time between events
        # was greater than the afk timeout value, this closes the
        # previous stream of events, condenses them into an activity
        # snapshot, and sends them to the time tracking server.

        windowed = shifted.pipe(
            ops.window(
                merged.pipe(
                    pairwise_buffer, ops.map(AnkiEventPair),
                    emit_when(lambda x: x.different_cards() or x.afk_timeout())
                ))).pipe(ops.flat_map(lambda x: x.pipe(ops.to_list())),
                         ops.filter(lambda x: len(x) > 1))

        # condense events into an activity snapshot and
        # send to the server on a thread pool thread
        windowed.pipe(ops.observe_on(self.pool_scheduler)).subscribe(
            self.send_snapshot)

    def send_snapshot(self, events: List):
        fst = events[0]
        snd = events[-1]
        duration = (snd.timestamp - fst.timestamp).total_seconds()
        print(
            f"Event: cards: [{fst.value.card_id}, {snd.value.card_id}] duration: {duration}"
        )

    @staticmethod
    def is_reviewer(context: Any) -> bool:
        return isinstance(context, Reviewer)

    def on_question_shown(self, card: Card) -> None:
        self.question_shown.on_next(QuestionShownEvent(card.id))

    def on_answer_shown(self, card: Card) -> None:
        self.answer_shown.on_next(AnswerShownEvent(card.id))

    def handle_js_message(self, handled: Tuple[bool, Any], message: str,
                          context: Any) -> Tuple[bool, Any]:
        if self.is_reviewer(context):
            reviewer: Reviewer = context
            if message == "mousemove":
                self.mouse_moved.on_next(MouseEvent(reviewer.card.id))
            elif message == "keydown":
                self.keyboard_pressed.on_next(KeyboardEvent(reviewer.card.id))
            elif message == "scroll":
                self.mouse_scroll.on_next(MouseEvent(reviewer.card.id))
            elif message == "click":
                self.mouse_click.on_next(MouseEvent(reviewer.card.id))
        return handled
