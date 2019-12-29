from random import expovariate, triangular, seed

import simpy
from simpy.core import BaseEnvironment
from simpy.util import start_delayed


## Model components -----------------------------

def otr_clts_in_res(res):
    """ number of clients waiting for or with resource res"""
    return (len(res.queue)+len(res.users))


def visit(env, tell_l_m_r, name, counters):
    """ Customer arrives, looks around and leaves """
    arrive = env.now
    # print(arrive, name," Here I am")
    # req = counters.request()
    # yield req

    num_counters = len(counters)
    queues_len = [otr_clts_in_res(counters[i]) for i in range(num_counters)]
    print('Here I am: ', env.now, name, queues_len)
    for i in range(num_counters):
        if (queues_len[i] == 0) or (queues_len[i] == min(queues_len)):
            choice = i  # the chosen queue number
            break
    # yield request,self,counters[choice]
    req = counters[choice].request()
    yield req

    wait = env.now - arrive  # waiting time
    print(env.now, name, 'waited :', wait)
    # tib = expovariate(1.0/timeInBank)
    low, high, mode = tell_l_m_r
    tib = triangular(low, high, mode)
    yield env.timeout(tib)
    counters[choice].release(req)
    print (env.now, name, " Finished")


def generate(number, meanTBA, counters, tell_l_m_r):
    """ Source generates customers regularly """
    for i in range(number):
        env.process(visit(env, tell_l_m_r=tell_l_m_r,
                          name='customer_' + str(i),
                          counters=counters))
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
counters = [simpy.Resource(env, capacity=1),
            simpy.Resource(env, capacity=1),
            simpy.Resource(env, capacity=1)]
env.process(generate(number=maxNumber, meanTBA=meanTBA,
                     counters=counters, tell_l_m_r=tell_l_m_r))
env.run(until=maxTime)
