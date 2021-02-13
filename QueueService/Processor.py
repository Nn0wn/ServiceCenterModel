from QueueService.Generator import Generator
from collections import deque
from QueueService.StateEvent import Event


class Processor:

    def __init__(self, generator: Generator):
        self.__generator = generator
        self.__processed_time = None
        self.__proc_times = deque(self.__generator.values())
        self.__processing = None
        self.__time = 0

    def pop(self):
        return self.__proc_times.pop()

    def popleft(self):
        return self.__proc_times.popleft()

    def append(self, val):
        self.__proc_times.append(val)

    def appendleft(self, val):
        self.__proc_times.appendleft(val)

    def values(self):
        return self.__proc_times

    def setProcessing(self, val):
        self.__processing = val

    def clearProcessing(self):
        self.__processing = None

    def setProcessedTime(self, val):
        self.__processed_time = val

    def clearProcessedTime(self):
        self.__processed_time = None

    def processing(self):
        return self.__processing

    def time(self):
        return self.__time

    def updateTime(self, event: Event):
        self.__time += event.time_in_proc

    def setTime(self, val):
        self.__time = val

    def generator(self):
        return self.__generator
