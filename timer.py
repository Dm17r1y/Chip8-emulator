#!/usr/bin/python3


def empty_func():
    pass


class Timer:

    def __init__(self, end_timer_func=empty_func, start_ticks=0):
        self._ticks = start_ticks
        self._end_timer_func = end_timer_func

    @property
    def ticks(self):
        return self._ticks

    @ticks.setter
    def ticks(self, value):
        self._ticks = value

    def tick(self):
        if self.ticks > 0:
            self.ticks -= 1
            if self.ticks == 0:
                self._end_timer_func()
