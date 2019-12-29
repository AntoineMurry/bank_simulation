""" bank01: The single non-random Customer """
from random import expovariate, seed

import simpy
from simpy.core import BaseEnvironment
# from simpy.events import Initialize
# from simpy.events import Process
from simpy.util import start_delayed


## Model components -----------------------------

def visit(env, timeInBank, name):
    """ Customer arrives, looks around and leaves """
    print(env.now, name," Here I am")
    yield env.timeout(timeInBank)
    print (env.now, name," I must leave")


def generate(number, meanTBA):
    """ Source generates customers regularly """
    for i in range(number):
        # c = Customer(name = "Customer%02d"%(i,))
        env.process(visit(env, timeInBank=12,
                          name='customer_' + str(i)))
        t = expovariate(meanTBA)
        yield env.timeout(t)


## Experiment data ------------------------------

maxNumber = 5
maxTime = 100.0     # minutes
# timeInBank = 10.0   # minutes
meanTBA = 0.66667   # average time between arrivals, minutes

## Model/Experiment ------------------------------

RANDOM_SEED = 42
# seed(RANDOM_SEED)
env = simpy.Environment()
# c = Customer(name="Klaus")
# activate(c,c.visit(timeInBank),at=5.0)
# visit_1 = visit(env, timeInBank=timeInBank, name='Klaus')
# visit_2 = visit(env, timeInBank=timeInBank, name='Charls')
# visit_3 = visit(env, timeInBank=timeInBank, name='Bill')
# proc = env.process(visit(env, timeInBank=timeInBank,
#                          name='Klaus'))

# activate(s, s.generate(number=maxNumber,
#                        TBA=ARRint), at=0.0)
env.process(generate(number=maxNumber, meanTBA=meanTBA))

# proc1 = env.process(visit_1)
# proc2 = env.process(visit_2)
# proc3 = env.process(visit_3)

# t = expovariate(0.66667)
# proc = start_delayed(env, visit(env, timeInBank=timeInBank,
#                                 name='Klaus'), t)
env.run(until=maxTime)
