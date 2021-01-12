from typing import List, Callable, Dict
import anki


class TimeTrackerAddonEventHook:
    _hooks: List[Callable[[Dict], None]] = []

    def append(self, cb: Callable[[Dict], None]) -> None:
        self._hooks.append(cb)

    def remove(self, cb: Callable[[Dict], None]):
        if cb in self._hooks:
            self._hooks.remove(cb)

    def count(self) -> int:
        return len(self._hooks)

    def __call__(self, data: Dict) -> None:
        for hook in self._hooks:
            try:
                hook(data)
            except:
                # if the hook fails, remove it
                self._hooks.remove(hook)
                raise
