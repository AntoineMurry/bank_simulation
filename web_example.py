from random import expovariate, triangular, seed

import simpy
from simpy.core import BaseEnvironment
from simpy.util import start_delayed


## Model functions


def otr_clts_in_res(res):
    """ number of clients waiting for or with resource res"""
    return (len(res.queue)+len(res.users))


def visit_cntr(env, tell_l_m_r, name, counters):
    """
    Customer arrives, stands in line, goes to teller and leaves
    :input:
        env: environment of simulation (simpy object)
        tell_l_m_r: tuple that contains triangular law parameters
        name: name of customer
        counters: list of teller resources in the simulation
    """
    # time when customer arrives
    arrive = env.now
    num_counters = len(counters)
    # list the queues of all other tellers (counters)
    # then choose the teller with the shortest queue
    queues_len = [otr_clts_in_res(counters[i]) for i in range(num_counters)]
    for i in range(num_counters):
        if (queues_len[i] == 0) or (queues_len[i] == min(queues_len)):
            choice = i
            break
    # request a teller resource
    req = counters[choice].request()
    yield req # wait till resource can be allocated

    # count time of use of teller
    start_use_ctr = env.now

    # draw teller tile from triangular law
    low, high, mode = tell_l_m_r
    tib = triangular(low, high, mode)
    yield env.timeout(tib) # wait till teller time is over

    # count time client spend in line plus with teller
    wait = env.now - arrive
    WAIT_TIMES_ctrs.append(wait)
    # release teller resource
    counters[choice].release(req)
    CTR_TIME.append(env.now - start_use_ctr)


def visit_atm(env, atm_l_m_r, name, atms):
    """
    Customer arrives, stands in line, goes to atm and leaves
    :input:
        env: environment of simulation (simpy object)
        atm_l_m_r: tuple that contains triangular law parameters
        name: name of customer
        atms: list of atm resources in the simulation
    """
    # time when customer arrives
    arrive_atm = env.now
    num_atms = len(atms)
    # list the queues of all other atms
    # then choose the atm with the shortest queue
    queues_len = [otr_clts_in_res(atms[i]) for i in range(num_atms)]
    for i in range(num_atms):
        if (queues_len[i] == 0) or (queues_len[i] == min(queues_len)):
            choice = i
            break
    # request an atm resource
    req = atms[choice].request()
    yield req

    # count time of use of atm
    start_use_atm = env.now
    # save time spend in atm line
    wait = env.now - arrive_atm
    WAIT_TIMES_ATM.append(wait)

    # draw teller tile from triangular law
    low, high, mode = atm_l_m_r
    tib = triangular(low, high, mode)
    yield env.timeout(tib)
    atms[choice].release(req)
    # release ATM resource
    ATM_TIME.append(env.now - start_use_atm)


def visit_atm_ctr(env, tell_l_m_r, name, counters, atm_l_m_r, atms):
    """
    Customer arrives, stands in line, goes to atm, then teller and leaves
    :input:
        env: environment of simulation (simpy object)
        atm_l_m_r: tuple that contains triangular law parameters for atm
        tell_l_m_r: tuple that contains triangular law parameters for teller
        name: name of customer
        atms: list of atm resources in the simulation
        counters: list of counter resources in the simulation
    """
    # atm part (same principle as visit_atm function)
    arrive_atm = env.now
    num_atms = len(atms)
    queues_len = [otr_clts_in_res(atms[i]) for i in range(num_atms)]
    for i in range(num_atms):
        if (queues_len[i] == 0) or (queues_len[i] == min(queues_len)):
            choice = i
            break
    req = atms[choice].request()
    yield req
    start_use_atm = env.now
    wait = env.now - arrive_atm
    WAIT_TIMES_ATM.append(wait)

    low, high, mode = atm_l_m_r
    tib = triangular(low, high, mode)
    yield env.timeout(tib)
    atms[choice].release(req)
    ATM_TIME.append(env.now - start_use_atm)

    # teller part (same principle as visit_cntr function)
    arrive_ctr = env.now
    num_counters = len(counters)
    queues_len = [otr_clts_in_res(counters[i]) for i in range(num_counters)]
    for i in range(num_counters):
        if (queues_len[i] == 0) or (queues_len[i] == min(queues_len)):
            choice = i
            break
    req = counters[choice].request()
    yield req
    start_use_ctr = env.now

    low, high, mode = tell_l_m_r
    tib = triangular(low, high, mode)
    yield env.timeout(tib)
    wait = env.now - arrive_ctr
    WAIT_TIMES_ctrs.append(wait)
    counters[choice].release(req)
    CTR_TIME.append(env.now - start_use_ctr)


def generate(number, meanTBA, counters, tell_l_m_r, atms, atm_l_m_r):
    """ Source generates customers regularly """
    for i in range(0, number, 3):
        env.process(visit_cntr(env, tell_l_m_r=tell_l_m_r,
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


## Model/Experiment

maxNumber = 50000
maxTime = 72000.0     # minutes
tell_l_m_r = (3, 30, 10)   # average time at counter, minutes
atm_l_m_r = (2, 10, 20) # average time at atm, minutes
meanTBA = 1.5   # average time between arrivals, minutes

# seed(0)

avgs_wait_atm = []
avgs_wait_ctrs = []

for i in range(5):
    WAIT_TIMES_ctrs = []
    WAIT_TIMES_ATM = []
    CTR_TIME = []
    ATM_TIME = []
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
                simpy.Resource(env, capacity=1)]
    atms = [simpy.Resource(env, capacity=1),
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

    env.process(generate(number=maxNumber, meanTBA=meanTBA,
                         counters=counters, tell_l_m_r=tell_l_m_r,
                         atms=atms, atm_l_m_r=atm_l_m_r))
    env.run(until=maxTime)
    avg_atm = sum(WAIT_TIMES_ATM) / len(WAIT_TIMES_ATM)
    avg_ctrs = sum(WAIT_TIMES_ctrs) / len(WAIT_TIMES_ctrs)
    print('average time for ATM line: ', avg_atm)
    print('average time for counters: ', avg_ctrs)
    avgs_wait_atm.append(avg_atm)
    avgs_wait_ctrs.append(avg_ctrs)
    print(env.now, ': time')

print(sum(avgs_wait_atm)/len(avgs_wait_atm), ': average wait atm')
print(sum(avgs_wait_ctrs)/len(avgs_wait_ctrs), ': average wait counters')
