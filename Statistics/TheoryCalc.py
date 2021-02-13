from typing import Union
import numpy as np
from QueueService.Generator import Generator
import pandas as pd


class TheoryCalc:

    def __init__(self, generator: Generator, size: Union[type(None), int] = None):
        self.__gen = generator
        self.__size = size
        self.__var_coefs = {'uni': np.sqrt(3) / 2, 'exp': 1, 'trg': np.sqrt(2) / 2}
        self.__QA = None
        self.__QT = None
        self.__QD = None
        self.__FT = None
        self.__processCalc()

    def __calcFT(self):
        if self.__gen.type() == 'uni':
            self.__FT = self.__gen.coef() / 2
        elif self.__gen.type() == 'exp':
            self.__FT = 1 / self.__gen.coef()
        elif self.__gen.type() == 'trg':
            self.__FT = self.__gen.coef() / 3

    def __calcQA(self):
        assert self.__gen.rho()
        if self.__size:
            self.__QA = self.__gen.rho() ** 2 * (1 - self.__gen.rho() ** self.__size *
                                                 (self.__size - self.__size * self.__gen.rho() + 1)) * (
                                1 + self.__var_coefs[self.__gen.type()] ** 2) / (
                                2 * (1 - self.__gen.rho() ** (self.__size + 2)) * (1 - self.__gen.rho()))
        else:
            self.__QA = self.__gen.rho() ** 2 * (1 + self.__var_coefs[self.__gen.type()] ** 2) / (
                    2 * (1 - self.__gen.rho()))

    def __calcQT(self):
        assert self.__gen.rho(), self.__FT
        if self.__size:
            self.__QT = self.__gen.rho() * self.__FT * (1 - self.__gen.rho() ** self.__size *
                                                        (self.__size - self.__size * self.__gen.rho() + 1)) * (
                                1 + self.__var_coefs[self.__gen.type()] ** 2) / (
                                2 * (1 - self.__gen.rho() ** (self.__size + 2)) * (1 - self.__gen.rho()))
        else:
            self.__QT = self.__gen.rho() * self.__FT * (1 + self.__var_coefs[self.__gen.type()] ** 2) / (
                    2 * (1 - self.__gen.rho()))

    def __calcQD(self):
        if self.__size:
            self.__QD = (1 - self.__gen.rho()) * self.__gen.rho() ** (self.__size + 1) / (
                        1 - self.__gen.rho() ** (self.__size + 2))

    def __processCalc(self):
        self.__calcFT()
        self.__calcQA()
        self.__calcQT()
        self.__calcQD()

    def printResults(self):
        if self.__size:
            print('****** THEORY START ********')
            print('QA', self.__QA, 'QT', self.__QT)
            print('QD', self.__QD, 'FT', self.__FT)
            print('******* THEORY END *********')
        else:
            print('****** THEORY START ********')
            print('QA', self.__QA, 'QT', self.__QT)
            print('QD', self.__QD, 'FT', self.__FT)
            print('******* THEORY END *********')

    def parameters(self):
        if self.__size:
            return pd.DataFrame({'Generator type': [self.__gen.type()],
                                 'Generator parameter': [self.__gen.coef()],
                                 'Generator RHO': [self.__gen.rho()],
                                 'QA': [self.__QA], 'QT': [self.__QT], 'QD': [self.__QD], 'FT': [self.__FT]})
        else:
            return pd.DataFrame({'Generator type': [self.__gen.type()],
                                 'Generator parameter': [self.__gen.coef()],
                                 'Generator RHO': [self.__gen.rho()],
                                 'QA': [self.__QA], 'QT': [self.__QT], 'FT': [self.__FT]})
