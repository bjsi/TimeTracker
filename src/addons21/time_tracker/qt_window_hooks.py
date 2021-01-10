from anki.hooks import wrap


def money_patch_close_event(window, event_handler):
    window._closeWindow = wrap(window._closeWindow, event_handler)
