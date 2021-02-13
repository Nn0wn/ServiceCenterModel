from typing import Union
from QueueService.Generator import Generator
from QueueService.EventQueue import EventQueue
from QueueService.Emitter import Emitter
from QueueService.Processor import Processor
from Statistics.TheoryCalc import TheoryCalc
import numpy as np


class CoefCalculator:

    def __init__(self, coef: Union[list, int, float], n: int, rho: Union[list, int, float],
                 ptypes, loops=1, gtype='points'):
        assert (gtype in ['list', 'points'])
        self.__coef = coef
        self.__n = n
        self.__rho = rho if type(rho) == list else [rho]
        self.__ptypes = ptypes if type(ptypes) == list else [ptypes]
        for p in self.__ptypes:
            assert (p in ['uni', 'exp', 'trg'])
        self.__loops = range(loops)
        self.__gtype = gtype
        self.__results = []
        self.__min = {'coef': None, 'min': float('inf')}

    def calculate(self):
        self.__getStats()
        self.__getMin()
        return self.__min

    def __getStats(self):
        coefs = self.__coef if self.__gtype == 'list' else np.arange(self.__coef[0], self.__coef[1], self.__coef[2]) \
            if len(self.__coef) > 2 else np.arange(self.__coef[0], self.__coef[1]) if len(self.__coef) == 2 else []
        for coef in coefs:
            print(coef)
            rho_grous = []
            for rho in self.__rho:
                em_gen = Generator(coef, self.__n, ptype='exp')
                means = {}
                for ptype in self.__ptypes:
                    pr_gen = Generator(coef, self.__n, rho, gtype='rho', ptype=ptype)
                    teor = TheoryCalc(pr_gen)
                    qms = []
                    for i in self.__loops:
                        q = EventQueue(Emitter(em_gen), Processor(pr_gen))
                        q.process()
                        qms.append((q.parameters()['QT'] - teor.parameters()['QT']) ** 2)
                    means[ptype] = np.sqrt(np.mean(qms))
                rho_grous.append({'rho': rho, 'vals': means})
            self.__results.append({'coef': coef, 'vals': rho_grous})

    def __getMin(self):
        for coef_el in self.__results:
            new_min = 0
            for rho_el in coef_el['vals']:
                if 'uni' not in rho_el['vals']:
                    rho_el['vals']['uni'] = 0
                if 'exp' not in rho_el['vals']:
                    rho_el['vals']['exp'] = 0
                if 'trg' not in rho_el['vals']:
                    rho_el['vals']['trg'] = 0
                new_min += rho_el['vals']['uni'] + rho_el['vals']['exp'] + rho_el['vals']['trg']
            if self.__min['min'] > new_min:
                self.__min['min'] = new_min
                self.__min['coef'] = coef_el['coef']
