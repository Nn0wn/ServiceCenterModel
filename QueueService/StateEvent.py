class Event:

    def __init__(self, time_in=None, time_to_proc=None, time_in_proc=None, time_out=None):
        self.time_in = time_in
        self.time_to_proc = time_to_proc
        self.time_in_proc = time_in_proc
        self.time_out = time_out


class State:

    def __init__(self, size=None, time_start=None, time_end=None):
        self.size = size
        self.time_start = time_start
        self.time_end = time_end
