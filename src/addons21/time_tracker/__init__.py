from .main_observer import MainObserver
from .reviewer_event_stream import ReviewerEventStream
from .browser_event_stream import BrowserEventStream
from .card_adder_event_stream import CardAdderEventStream
from .deck_browser_event_stream import DeckBrowserEventStream
from .rx_utils import merge_streams
from .rx import operators as ops

streams = merge_streams(ReviewerEventStream().main_subj,
                        DeckBrowserEventStream().main_subj).pipe(ops.share())
observer = MainObserver(streams)
