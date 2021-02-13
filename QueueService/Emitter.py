from QueueService.Generator import Generator
from collections import deque


class Emitter:

    def __init__(self, generator: Generator):
        self.__generator = generator
        self.__requests = deque(self.__generator.values())
        self.__time = 0

    def pop(self):
        return self.__requests.pop()

    def popleft(self):
        return self.__requests.popleft()

    def append(self, val):
        self.__requests.append(val)

    def appendleft(self, val):
        self.__requests.appendleft(val)

    def values(self):
        return self.__requests

    def updateTime(self):
        if len(self.__requests) > 0:
            self.__time += self.__requests[0]
        else:
            self.__time = None

    def time(self):
        return self.__time

    def generator(self):
        return self.__generator
