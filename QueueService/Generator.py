from typing import Union, Optional
import numpy as np


class Generator:

    def __init__(self, const: Union[float, int], n: int, rho: Optional[float] = None, ptype='uni', gtype='coef'):
        assert (ptype in ['uni', 'exp', 'trg'])
        assert (gtype in ['coef', 'rho'])
        self.__gtype = gtype
        self.__ptype = ptype
        self.__const = const
        self.__rho = rho
        self.__n = n
        if self.__gtype == 'coef':
            self.__coef = const
            self.__values = self.__getValues()
        elif self.__gtype == 'rho':
            self.__coef = self.__getPrime()
            assert self.__rho, self.__coef
            self.__values = self.__getValues()

    def __make_uniform(self):
        return np.random.uniform(0, self.__coef, self.__n)

    def __make_exp(self):
        return [- np.log(1 - np.random.random()) / self.__coef for _ in range(self.__n)]

    def __make_triangle(self):
        return [self.__coef * (1 - np.sqrt(1 - np.random.random())) for _ in range(self.__n)]

    def __uniform_alpha(self):
        return 2 * self.__rho / self.__const

    def __exp_lambda(self):
        return self.__const / self.__rho

    def __triangle_a(self):
        return 3 * self.__rho / self.__const

    def __getPrime(self):
        if self.type() == 'uni':
            return self.__uniform_alpha()
        elif self.type() == 'exp':
            return self.__exp_lambda()
        elif self.type() == 'trg':
            return self.__triangle_a()

    def __getValues(self):
        if self.type() == 'uni':
            return self.__make_uniform()
        elif self.type() == 'exp':
            return self.__make_exp()
        elif self.type() == 'trg':
            return self.__make_triangle()

    def values(self):
        return self.__values

    def type(self):
        return self.__ptype

    def coef(self):
        return self.__coef

    def rho(self):
        return self.__rho

    def n(self):
        return self.__n
