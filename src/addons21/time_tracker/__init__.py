from .main_observer import MainObserver
from .rx_utils import merge_streams
from .rx import operators as ops

from .reviewer_event_stream import ReviewerEventStream
from .browser_event_stream import BrowserEventStream
from .card_adder_event_stream import CardAdderEventStream
from .deck_browser_event_stream import DeckBrowserEventStream
from .editor_event_stream import EditorEventStream
from .main_window_event_stream import MainWindowEventStream

streams = merge_streams(ReviewerEventStream().main_subj,
                        BrowserEventStream().main_subj,
                        CardAdderEventStream().main_subj,
                        EditorEventStream().main_subj,
                        MainWindowEventStream().main_subj,
                        DeckBrowserEventStream().main_subj).pipe(ops.share())
observer = MainObserver(streams)
