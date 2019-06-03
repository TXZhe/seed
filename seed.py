import multiprocessing as mp
import random
import numpy as np

class NetWork():
    def __init__(self):
        self.step = {}
        self.net = []

    def add(self, u, v, t):
        if not t in self.step:
            self.step[t] = len(self.net)
            self.net.append({})
        nowt = self.step[t]
        if not u in self.net[nowt]:
            self.net[nowt][u]=set()
            self.net[nowt][u].add(v)
        if not v in self.net[nowt]:
            self.net[nowt][v]=set()
            self.net[nowt][v].add(u)

    def check(self, u, t):
        if not t in self.step:
            print("there is no %d in step"%(t))
            return False
        return u in self.net[self.step[t]]

    def get_neighbor(self, u, t):
        if not t in self.step:
            print("1 there is no %d in step"%(t))
            return False
        return self.net[self.step[t]][u]

    def get_steps(self):
        return list(self.step.keys())

    def get_real_st(self, st):
        return self.step[st]


net_work = NetWork()
beta = 0.0
alpha = 0
theta = 0.0
avg = 0
usrnum = 0
x = 0

def action(param):
    seed, cd = param
    global net_work
    global beta
    global alpha
    global theta
    global avg
    global usrnum
    global x
    r_num_avg = 0.0
    steps = net_work.get_steps()
    fp = open("%d_%d.txt"%(seed, cd),"w")
    for i in range(avg):
        infected = set()
        recover = set()
        info = {}
        start = False
        seed_last_st = -1
        seed_times = 0
        for st in steps:
            if seed_times >= x and len(infected) == 0:
                break
            #SEED
            if net_work.check(seed, st):
                real_st = net_work.get_real_st(st)
                if seed_times < x and ((not start) or (start and real_st - seed_last_st >= cd)):
                    start = True
                    seed_last_st = real_st
                    seed_times += 1
                    ne = net_work.get_neighbor(seed, st)
                    for j in ne:
                        if not j in infected and not j in recover:
                            if not j in info:
                                info[j] = 0
                            info[j] += 1
                            if info[j] >= alpha:
                                infected.add(j)
                                info.pop(j)
            #Infected
            recoverd_i = set()
            for i_node in infected:
                if net_work.check(i_node, st):
                    ne = net_work.get_neighbor(i_node, st)
                    for j in ne:
                        if j!=seed and random.uniform(0,1) < beta and\
                            not j in infected and not j in recover:
                            if not j in info:
                                info[j] = 0
                            info[j] += 1
                            if info[j] >= alpha:
                                infected.add(j)
                                info.pop(j)
                #Recover
                if random.uniform(0,1) < theta:
                    recoverd_i.add(i_node)
                    recover.add(i_node)
                infected = infected - recoverd_i
                if len(infected) + len(recover) >= usrnum:
                    break
        print("%d"%(len(infected)+len(recover)), file=fp)
        r_num_avg += float(len(infected)+len(recover)) / avg
    fp.close()
    return r_num_avg

if __name__ == "__main__":
    global net_work
    global beta
    global alpha
    global theta
    global avg
    global usrnum
    global x
    beta = 0.1
    theta = 0.09
    alpha = 3
    avg = 100
    usrnum = 10145
    x = 3

    #input NetWork
    ## TODO: build...
    with open("",'r') as fin:
        for line in readlines():
            pass

    seed = np.random.choice(usrnum, 10, replace=False)
    param = []
    for i in seed:
        param.append([i, 0])
        param.append([i, 8])
        param.append([i, 56])
    resluts = list(mp.Pool(mp.cpu_count()).imap(action, param))
    with open("results.tsv",'w') as fout:
        for indx, se in enumerate(param):
            print("%d\t%d\t%f"%(se[0],se[1],resluts[indx]), file=fout)
