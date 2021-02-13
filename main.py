from Parameters.CoefCalculator import CoefCalculator
from QueueService.Generator import Generator
from QueueService.EventQueue import EventQueue
from QueueService.Emitter import Emitter
from QueueService.Processor import Processor
from Statistics.TheoryCalc import TheoryCalc
from Parameters.Params import Parameters
from Statistics.StatisticalAnalyzis import StatisticalAnalysis
import pandas as pd
import numpy as np
import math

pd.set_option("display.max_rows", 9999, "display.max_columns", 9999)
pd.set_option('expand_frame_repr', False)

RHOS = [0.45, 0.85]
NS = [1750, 47500]
PTYPES = ['uni', 'exp', 'trg']
QUEUE_SIZES_EXP = []
QUEUE_SIZES_TEOR = []
QUEUE_SIZES_STAT = []
E = 1.8
params3 = Parameters([NS, RHOS, PTYPES]).combinations()

# For approaching to teoretical values
# E = CoefCalculator([0.01, 2, 0.05], 1000, RHOS[0], PTYPES[0], loops=100, gtype='points').calculate()['coef']

df = pd.DataFrame()

print('*' * 40,
      'Checking generators with Rhos <' + str(RHOS) + '> and Types <' + str(PTYPES) + '>',
      '*' * 40, sep='\n')

for num in [10 ** p for p in [i for i in range(2, 7, 2)]]:
    for params in Parameters([RHOS, PTYPES]).combinations():
        emitter_gen = Generator(E, num, ptype='exp')
        processor_gen = Generator(E, num, *params, gtype='rho')
        df = df.append(pd.DataFrame({'N': [num], 'Theoretical rho': [params[0]], 'Dist type': [params[1]],
                                     'Experimental rho': [
                                         np.mean(processor_gen.values()) / np.mean(emitter_gen.values())]}),
                       ignore_index=True)
print(df)

print('###############################################################################################################')
print('################################################ INFINITE QUEUE ###############################################')
print('###############################################################################################################')

df = pd.DataFrame()

Ns_sz = 2
Ns_step = 1000
Ns_ar = [Ns_step * i for i in range(1, Ns_sz)]
Rho = 0.55
Eps = 0.05

# print('*' * 40,
#       'Ns to approach the static point with epsilon <' + str(Eps) + '>',
#       '*' * 40, sep='\n')
#
# for ptype in PTYPES:
#     ldf = pd.DataFrame()
#     for N in Ns_ar:
#         # print('Iteration ' + str(N))
#         q = EventQueue(Emitter(Generator(E, n=N, rho=Rho, ptype=ptype)),
#                        Processor(Generator(E, n=N, rho=Rho, ptype=ptype, gtype='rho')))
#         q.process()
#         ldf = ldf.append(q.parameters(), ignore_index=True)
#     teor_num = TheoryCalc(Generator(E, n=1000, rho=Rho, ptype=ptype, gtype='rho')).parameters()['QT'].values[0]
#     req_num = StatisticalAnalysis(ldf).transientResponse('QT', teor_num, eps=Eps)
#     df = df.append(pd.DataFrame({'Type': ptype, 'Teoretical point': [teor_num], 'Epsilon (%)': [Eps],
#                                  'N to approach': [req_num]}), ignore_index=True)
# print(df)

df = pd.DataFrame()
dft = pd.DataFrame()

print('*' * 40,
      'Getting queue parameters for Rhos <' + str(RHOS) + '>, Ns <' + str(NS) + '> and Types <' + str(PTYPES) + '>',
      '*' * 40, sep='\n')

for index, combination in enumerate(params3):
    # print('Parameters combimation:', index + 1)
    q = EventQueue(Emitter(Generator(E, combination[0], ptype='exp')),
                   Processor(Generator(E, *combination, gtype='rho')))
    if index < len(params3) / 2:
        t = TheoryCalc(Generator(E, *combination, gtype='rho'))
    q.process()
    df = df.append(q.parameters(), ignore_index=True)
    QUEUE_SIZES_EXP.append(int(math.ceil(q.parameters()['QA'].values[0])))
    if index < len(params3) / 2:
        dft = dft.append(t.parameters(), ignore_index=True)
        QUEUE_SIZES_TEOR.append(int(math.ceil(t.parameters()['QA'].values[0])))

# print(df['QA'])
# print(np.ceil(df['QA'].values, dtype=int))

print('*' * 40,
      'Experimental values',
      '*' * 40, sep='\n')
print(df)

print('*' * 40,
      'Theoretical values',
      '*' * 40, sep='\n')
print(dft)

CONFIDENCE = 0.95
FREEDOM = 1

print('*' * 40,
      'Statistcal analysis with confidence <' + str(CONFIDENCE) + '> and freedom <' + str(FREEDOM) + '>',
      '*' * 40, sep='\n')
df = pd.DataFrame()

for i in range(10):
    q = EventQueue(Emitter(Generator(E, n=50000, rho=0.45, ptype='exp')),
                   Processor(Generator(E, n=50000, rho=0.45, ptype='exp', gtype='rho')))
    q.process()
    df = df.append(q.parameters(), ignore_index=True)
    QUEUE_SIZES_STAT.append(int(math.ceil(q.parameters()['QA'].values[0])))

df = df[['QA', 'QM', 'QZ', 'QT', 'QX', 'FR', 'FT']]
print(df)
print()

print(QUEUE_SIZES_STAT)

sdf = StatisticalAnalysis(df, CONFIDENCE, FREEDOM).process()
print(sdf)

print('###############################################################################################################')
print('################################################# FINITE QUEUE ################################################')
print('###############################################################################################################')

df = pd.DataFrame()

Ns_sz = 20
Ns_step = 1000
Ns_ar = [Ns_step * i for i in range(1, Ns_sz)]
Rho = 0.55
Eps = 0.05

df = pd.DataFrame()
dft = pd.DataFrame()

print('*' * 40,
      'Getting queue parameters for Rhos <' + str(RHOS) + '>, Ns <' + str(NS) + '> and Types <' + str(PTYPES) + '>',
      '*' * 40, sep='\n')

for index, combination in enumerate(params3):
    # print('Parameters combimation:', index + 1)
    q = EventQueue(Emitter(Generator(E, combination[0], ptype='exp')),
                   Processor(Generator(E, *combination, gtype='rho')), size=QUEUE_SIZES_EXP[index])
    if index < len(params3) / 2:
        t = TheoryCalc(Generator(E, *combination, gtype='rho'), size=QUEUE_SIZES_TEOR[index])
    q.process()
    df = df.append(q.parameters(), ignore_index=True)
    if index < len(params3) / 2:
        dft = dft.append(t.parameters(), ignore_index=True)

print('*' * 40,
      'Experimental values',
      '*' * 40, sep='\n')
print(df)

print('*' * 40,
      'Theoretical values',
      '*' * 40, sep='\n')
print(dft)

CONFIDENCE = 0.95
FREEDOM = 1

print('*' * 40,
      'Statistcal analysis with confidence <' + str(CONFIDENCE) + '> and freedom <' + str(FREEDOM) + '>',
      '*' * 40, sep='\n')
df = pd.DataFrame()

for i in range(10):
    q = EventQueue(Emitter(Generator(E, n=50000, rho=0.45, ptype='exp')),
                   Processor(Generator(E, n=50000, rho=0.45, ptype='exp', gtype='rho')), size=QUEUE_SIZES_STAT)
    q.process()
    df = df.append(q.parameters(), ignore_index=True)

df = df[['QA', 'QM', 'QZ', 'QT', 'QD', 'QX', 'FR', 'FT']]
print(df)
print()

sdf = StatisticalAnalysis(df, CONFIDENCE, FREEDOM).process()
print(sdf)