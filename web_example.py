from random import expovariate, seed

import simpy
from simpy.core import BaseEnvironment
from simpy.util import start_delayed


## Model components -----------------------------

def visit(env, timeInBank, name, resource):
    """ Customer arrives, looks around and leaves """
    arrive = env.now
    print(arrive, name," Here I am")
    req = resource.request()
    yield req
    wait = env.now - arrive  # waiting time
    print(env.now, name, 'waited :', wait)
    yield env.timeout(timeInBank)
    resource.release(req)
    print (env.now, name, " Finished")


def generate(number, meanTBA, resource):
    """ Source generates customers regularly """
    for i in range(number):
        env.process(visit(env, timeInBank=12,
                          name='customer_' + str(i),
                          resource=resource))
        t = expovariate(1.0/meanTBA)
        yield env.timeout(t)


## Experiment data ------------------------------

maxNumber = 5
maxTime = 400.0     # minutes
# timeInBank = 10.0   # minutes
meanTBA = 1.5   # average time between arrivals, minutes
# meanTBA = 10

## Model/Experiment ------------------------------

seed(0)
env = simpy.Environment()
counter = simpy.Resource(env, capacity=1)
env.process(generate(number=maxNumber, meanTBA=meanTBA,
                     resource=counter))
env.run(until=maxTime)
