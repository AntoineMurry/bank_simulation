from random import expovariate, triangular, seed

import simpy
from simpy.core import BaseEnvironment
from simpy.util import start_delayed


## Model components -----------------------------

def visit(env, tell_l_m_r, name, resource):
    """ Customer arrives, looks around and leaves """
    arrive = env.now
    print(arrive, name," Here I am")
    req = resource.request()
    yield req
    wait = env.now - arrive  # waiting time
    print(env.now, name, 'waited :', wait)
    # tib = expovariate(1.0/timeInBank)
    low, high, mode = tell_l_m_r
    tib = triangular(low, high, mode)
    yield env.timeout(tib)
    resource.release(req)
    print (env.now, name, " Finished")


def generate(number, meanTBA, resource, tell_l_m_r):
    """ Source generates customers regularly """
    for i in range(number):
        env.process(visit(env, tell_l_m_r=tell_l_m_r,
                          name='customer_' + str(i),
                          resource=resource))
        t = expovariate(1.0/meanTBA)
        yield env.timeout(t)


## Experiment data ------------------------------

maxNumber = 5
maxTime = 400.0     # minutes
tell_l_m_r = (3, 30, 10)   # average time at counter, minutes
meanTBA = 1.5   # average time between arrivals, minutes
# meanTBA = 10

## Model/Experiment ------------------------------

seed(0)
env = simpy.Environment()
counter = simpy.Resource(env, capacity=1)
env.process(generate(number=maxNumber, meanTBA=meanTBA,
                     resource=counter, tell_l_m_r=tell_l_m_r))
env.run(until=maxTime)
