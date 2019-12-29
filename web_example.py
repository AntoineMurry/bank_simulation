from random import expovariate, triangular, seed

import simpy
from simpy.core import BaseEnvironment
from simpy.util import start_delayed


## Model components -----------------------------

WAIT_TIMES_ctrs = []
WAIT_TIMES_ATM = []

def otr_clts_in_res(res):
    """ number of clients waiting for or with resource res"""
    return (len(res.queue)+len(res.users))


def visit(env, tell_l_m_r, name, counters):
    """ Customer arrives, stands in line, goes to teller and leaves """
    arrive = env.now
    num_counters = len(counters)
    queues_len = [otr_clts_in_res(counters[i]) for i in range(num_counters)]
    print('Here I am: ', env.now, name, queues_len)
    for i in range(num_counters):
        if (queues_len[i] == 0) or (queues_len[i] == min(queues_len)):
            choice = i  # the chosen queue number
            break
    req = counters[choice].request()
    yield req

    low, high, mode = tell_l_m_r
    tib = triangular(low, high, mode)
    yield env.timeout(tib)
    wait = env.now - arrive  # waiting time
    WAIT_TIMES_ctrs.append(wait)
    print(env.now, name, ' finished total time at counter')
    counters[choice].release(req)
    print (env.now, name, " Finished")


def visit_atm(env, atm_l_m_r, name, atms):
    """ Customer arrives, stands in line, goes to atm and leaves """
    arrive_atm = env.now
    num_atms = len(atms)
    queues_len = [otr_clts_in_res(atms[i]) for i in range(num_atms)]
    print('Here I am: ', env.now, name, queues_len)
    for i in range(num_atms):
        if (queues_len[i] == 0) or (queues_len[i] == min(queues_len)):
            choice = i  # the chosen queue number
            break
    req = atms[choice].request()
    yield req
    wait = env.now - arrive_atm  # waiting time
    WAIT_TIMES_ATM.append(wait)
    print(env.now, name, 'finised atm line :', wait)
    print(env.now, name, " Finished atm line")

    low, high, mode = tell_l_m_r
    tib = triangular(low, high, mode)
    yield env.timeout(tib)
    atms[choice].release(req)
    print (env.now, name, " Finished")


def visit_atm_ctr(env, tell_l_m_r, name, counters, atm_l_m_r, atms):
    """
    Customer arrives, stands in line, goes to atm, then teller and leaves
    """
    arrive_atm = env.now
    num_atms = len(atms)
    queues_len = [otr_clts_in_res(atms[i]) for i in range(num_atms)]
    print('Here I am: ', env.now, name, queues_len)
    for i in range(num_atms):
        if (queues_len[i] == 0) or (queues_len[i] == min(queues_len)):
            choice = i  # the chosen queue number
            break
    req = atms[choice].request()
    yield req
    wait = env.now - arrive_atm  # waiting time
    WAIT_TIMES_ATM.append(wait)
    print(env.now, name, 'finised atm line :', wait)
    print(env.now, name, 'Finished ATM line')

    low, high, mode = tell_l_m_r
    tib = triangular(low, high, mode)
    yield env.timeout(tib)
    atms[choice].release(req)


    arrive_ctr = env.now
    num_counters = len(counters)
    queues_len = [otr_clts_in_res(counters[i]) for i in range(num_counters)]
    print('After atm, I am now going to teller: ', env.now, name, queues_len)
    for i in range(num_counters):
        if (queues_len[i] == 0) or (queues_len[i] == min(queues_len)):
            choice = i  # the chosen queue number
            break
    req = counters[choice].request()
    yield req

    low, high, mode = tell_l_m_r
    tib = triangular(low, high, mode)
    yield env.timeout(tib)
    wait = env.now - arrive_ctr  # waiting time
    WAIT_TIMES_ctrs.append(wait)
    print(env.now, name, 'total teller time :', wait)
    counters[choice].release(req)
    print (env.now, name, " Finished")




def generate(number, meanTBA, counters, tell_l_m_r, atms, atm_l_m_r):
    """ Source generates customers regularly """
    for i in range(0, number, 3):
        env.process(visit(env, tell_l_m_r=tell_l_m_r,
                          name='customer_' + str(i),
                          counters=counters))
        t = expovariate(1.0/meanTBA)
        yield env.timeout(t)
        env.process(visit_atm(env, atm_l_m_r=atm_l_m_r,
                              name='customer_' + str(i+1),
                              atms=atms))
        t = expovariate(1.0/meanTBA)
        yield env.timeout(t)
        env.process(visit_atm_ctr(env, atm_l_m_r=atm_l_m_r,
                                  name='customer_' + str(i+2),
                                  atms=atms, counters=counters,
                                  tell_l_m_r=tell_l_m_r))
        t = expovariate(1.0/meanTBA)
        yield env.timeout(t)


## Experiment data ------------------------------

maxNumber = 50000
maxTime = 72000.0     # minutes
tell_l_m_r = (3, 30, 10)   # average time at counter, minutes
atm_l_m_r = (2, 10, 20) # average time at atm, minutes
meanTBA = 1.5   # average time between arrivals, minutes
# meanTBA = 10

## Model/Experiment ------------------------------

# seed(0)
env = simpy.Environment()
counters = [simpy.Resource(env, capacity=1),
            simpy.Resource(env, capacity=1),
            simpy.Resource(env, capacity=1),
            simpy.Resource(env, capacity=1),
            simpy.Resource(env, capacity=1),
            simpy.Resource(env, capacity=1),
            simpy.Resource(env, capacity=1),
            simpy.Resource(env, capacity=1),
            simpy.Resource(env, capacity=1),
            simpy.Resource(env, capacity=1),
            simpy.Resource(env, capacity=1),
            simpy.Resource(env, capacity=1),
            simpy.Resource(env, capacity=1),
            simpy.Resource(env, capacity=1)]
atms = [simpy.Resource(env, capacity=1),
        simpy.Resource(env, capacity=1),
        simpy.Resource(env, capacity=1),
        simpy.Resource(env, capacity=1),
        simpy.Resource(env, capacity=1),
        simpy.Resource(env, capacity=1),
        simpy.Resource(env, capacity=1),
        simpy.Resource(env, capacity=1)]
env.process(generate(number=maxNumber, meanTBA=meanTBA,
                     counters=counters, tell_l_m_r=tell_l_m_r,
                     atms=atms, atm_l_m_r=atm_l_m_r))
env.run(until=maxTime)

print('average time for ATM line: ',
      sum(WAIT_TIMES_ATM) / len(WAIT_TIMES_ATM))

print('average time for counters: ',
      sum(WAIT_TIMES_ctrs) / len(WAIT_TIMES_ctrs))
