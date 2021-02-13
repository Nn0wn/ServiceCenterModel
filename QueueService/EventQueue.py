from typing import Union
from QueueService.Emitter import Emitter
from QueueService.Processor import Processor
from collections import deque
from QueueService.StateEvent import State, Event
import numpy as np
import pandas as pd


class EventQueue:

    def __init__(self, emitter: Emitter, processor: Processor, size: Union[type(None), int] = None, log=False):
        self.__processor = processor
        self.__emitter = emitter
        self.__size = size
        self.__log = log
        self.__states, self.__processed, self.__skipped, self.__queue = deque(), deque(), deque(), deque()
        self.__cur_event = None
        self.__cur_proc_time = None
        self.__QA = None
        self.__QM = None
        self.__QZ = None
        self.__QT = None
        self.__QX = None
        self.__QD = None
        self.__FR = None
        self.__FT = None

    def process(self):
        self.__updateStates(self.__emitter.time())
        self.__emitter.updateTime()
        while len(self.__emitter.values()) > 0 and len(self.__processor.values()) > 0:
            self.__cur_event = self.__emitter.popleft()
            self.__cur_proc_time = self.__processor.popleft()
            self.__step()
        if len(self.__states) > 0:
            self.__states[-1].time_end = self.__processor.time()
        self._makeCalcs()

    def __step(self):
        self.__updateQueue()
        self.__updateProcessor()

    def __updateProcessor(self):
        while len(self.__queue) > 0:
            if not self.__processor.processing() and len(self.__queue) > 0:
                event = self.__queue.popleft()
                self.__processor.setProcessing(event)
                if event.time_in > self.__processor.time():
                    self.__processor.setTime(event.time_in)
                event.time_to_proc = self.__processor.time()
                if self.__log:
                    print('Item with PROC TIME [', self.__processor.processing().time_in_proc,
                          '] < START PROCESSING >  at [',
                          self.__processor.processing().time_to_proc, '] \tQUEUE LENGTH', len(self.__queue))
                self.__processor.updateTime(event)
                self.__updateStates(self.__processor.processing().time_to_proc)
            if self.__processor.processing() and (
                    not self.__emitter.time() or self.__emitter.time() >= self.__processor.time()):
                self.__processor.processing().time_out = self.__processor.time()
                self.__processed.append(self.__processor.processing())
                if self.__log:
                    print('Item with PROC TIME [', self.__processor.processing().time_in_proc,
                          '] < FINISHED PROCESSING >  at [',
                          self.__processor.processing().time_out, '] \tQUEUE LENGTH', len(self.__queue))
                self.__processor.setProcessing(None)
            else:
                break

    def __updateQueue(self):
        if self.__processor.time() > self.__emitter.time() or not self.__processor.processing():
            if self.__size and len(self.__queue) >= self.__size:
                self.__skipped.append(Event(Event(time_in=self.__emitter.time(), time_in_proc=self.__cur_proc_time)))
                if self.__log:
                    print('Item with PROC TIME [', self.__cur_proc_time, '] < SKIPPED > at [', self.__emitter.time(),
                          '] \tQUEUE LENGTH', len(self.__queue))
                self.__emitter.updateTime()
            else:
                self.__queue.append(Event(time_in=self.__emitter.time(), time_in_proc=self.__cur_proc_time))
                if self.__log:
                    print('Item with PROC TIME [', self.__cur_proc_time, '] < ADDED TO QUEUE > at [', self.__emitter.time(),
                          '] \tQUEUE LENGTH', len(self.__queue))
                self.__updateStates(self.__emitter.time())
                self.__emitter.updateTime()

    def __updateStates(self, time):
        if len(self.__states) > 0:
            self.__states[-1].time_end = time
        self.__states.append(State(size=len(self.__queue), time_start=time))

    def _makeCalcs(self):
        self.__QM = max([elem.size for elem in self.__states])
        self.__QA = sum([elem.size * (elem.time_end - elem.time_start) /
                         (self.__states[-1].time_end - self.__states[0].time_start)
                         for elem in self.__states if elem.time_start != elem.time_end])
        self.__QZ = len([elem for elem in self.__states if elem.time_start == elem.time_end])
        self.__QT = np.mean([elem.time_to_proc - elem.time_in for elem in self.__processed])
        self.__QX = np.mean([elem.time_to_proc - elem.time_in
                             for elem in self.__processed if elem.time_to_proc != elem.time_in])
        self.__QD = len(self.__skipped) / (len(self.__skipped) + len(self.__processed))
        self.__FR = sum([elem.time_end - elem.time_start for elem in self.__states
                         if elem.size > 0]) / (self.__states[-1].time_end - self.__states[0].time_start)
        self.__FT = np.mean([elem.time_out - elem.time_to_proc for elem in self.__processed])

    def parameters(self):
        if self.__size:
            return pd.DataFrame({'Emitter type':        [self.__emitter.generator().type()],
                                 'Emitter parameter':   [self.__emitter.generator().coef()],
                                 'Emitter RHO':         [self.__emitter.generator().rho()],
                                 'Processor type':      [self.__processor.generator().type()],
                                 'Processor parameter': [self.__processor.generator().coef()],
                                 'Processor RHO':       [self.__processor.generator().rho()],
                                 'N': [min(self.__emitter.generator().n(), self.__processor.generator().n())],
                                 'QA': [self.__QA], 'QM': [self.__QM], 'QZ': [self.__QZ], 'QT': [self.__QT],
                                 'QX': [self.__QX], 'QD': [self.__QD], 'FR': [self.__FR], 'FT': [self.__FT]})
        else:
            return pd.DataFrame({'Emitter type': [self.__emitter.generator().type()],
                                 'Emitter parameter': [self.__emitter.generator().coef()],
                                 'Emitter RHO': [self.__emitter.generator().rho()],
                                 'Processor type': [self.__processor.generator().type()],
                                 'Processor parameter': [self.__processor.generator().coef()],
                                 'Processor RHO': [self.__processor.generator().rho()],
                                 'N': [min(self.__emitter.generator().n(), self.__processor.generator().n())],
                                 'QA': [self.__QA], 'QM': [self.__QM], 'QZ': [self.__QZ], 'QT': [self.__QT],
                                 'QX': [self.__QX], 'FR': [self.__FR], 'FT': [self.__FT]})

    def printResults(self):
        if self.__size:
            print('****** EXPERIMENTAL RESULTS START ********')
            print('Emitter type:', '< ' + self.__emitter.generator().type() + ' >',
                  'PARAM:', self.__emitter.generator().coef(), 'RHO:',
                  self.__emitter.generator().rho())
            print('Processor type:', '< ' + self.__processor.generator().type() + ' >',
                  'PARAM:', self.__processor.generator().coef(), 'RHO:',
                  self.__processor.generator().rho())
            print('QA', self.__QA, 'QM', self.__QM, 'QZ', self.__QZ,
                  'QT', self.__QT, 'QX', self.__QX, 'QD', self.__QD)
            print('FR', self.__FR, 'FT', self.__FT)
            print('******* EXPERIMENTAL RESULTS END *********')
        else:
            print('****** EXPERIMENTAL RESULTS START ********')
            print('Emitter type:', '< ' + self.__emitter.generator().type() + ' >',
                  'PARAM:', self.__emitter.generator().coef(), 'RHO:',
                  self.__emitter.generator().rho())
            print('Processor type:', '< ' + self.__processor.generator().type() + ' >',
                  'PARAM:', self.__processor.generator().coef(), 'RHO:',
                  self.__processor.generator().rho())
            print('QA', self.__QA, 'QM', self.__QM, 'QZ', self.__QZ,
                  'QT', self.__QT, 'QX', self.__QX, 'QD', self.__QD)
            print('FR', self.__FR, 'FT', self.__FT)
            print('******* EXPERIMENTAL RESULTS END *********')
