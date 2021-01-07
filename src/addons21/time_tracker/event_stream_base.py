from .rx.core.observable import Observable
from abc import ABC


# TODO: Move subscription, stream creation into this
# just have one subject for gui, one for js in derived
# and merge into main
class EventStreamBase(ABC):
    main_subj: Observable  # TODO: change name, not a subject
