from scipy.stats import t
import pandas as pd


class StatisticalAnalysis:

    def __init__(self, data: pd.DataFrame, conf_coef: float = 0.95, freedom: float = 1):
        self.__data = data
        self.__coef = conf_coef
        self.__freedom = freedom
        self.__df = pd.DataFrame()

    def process(self):
        for column in self.__data.columns:
            sa_mean = self.__data[column].mean()
            sa_sem = self.__data[column].sem()
            sa_t = t.interval(self.__coef, self.__freedom, sa_mean, sa_sem)
            self.__df = self.__df.append(
                pd.DataFrame({'Trait': [column], 'Mean': [sa_mean], 'MSE': [sa_sem],
                              'Confidence interval': ['{:.3} {} {:.3}'.format(sa_t[0], '-', sa_t[1])],
                              'Result': ['{:.3} {} {:.3}'.format(sa_mean, '+-', sa_t[1] - sa_mean)]}),
                ignore_index=True)
        return self.__df

    def transientResponse(self, column, steady_val, eps: float = 0.05):
        for index, val in enumerate(reversed(self.__data[column].values), start=1):
            if abs(val - steady_val) > abs(steady_val * eps):
                return len(self.__data[column].values) - index
        return 0


