import multiprocessing as mp
import random
import numpy as np
import tqdm

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
beta = 0.05
theta = 0.045
alpha = 3
avg = 20
usrnum = 10145
x = 3


def action(param):
    seed, cd = param
    r_num_avg = 0.0
    steps = net_work.get_steps()
    fp = open("result\\%d_%d.tsv"%(seed, cd),"w")
    for i in range(avg):
        infected = set()
        recover = set()
        info = {}
        start = False
        seed_last_st = -1
        seed_times = 0
        for st in steps:
            seed_in = 0
            if seed_times >= x and len(infected) == 0:
                #print("%d_%d out in %d : %d"%(seed, cd, st, seed_times))
                break
            #SEED
            if net_work.check(seed, st):
                real_st = net_work.get_real_st(st)
                if seed_times < x and ((not start) or (start and real_st - seed_last_st >= cd)):
                    seed_in = 1
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
            new_i = set()
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
                                new_i.add(j)
                                info.pop(j)
                #Recover
                if random.uniform(0,1) < theta:
                    recoverd_i.add(i_node)
                    recover.add(i_node)
            infected = infected - recoverd_i
            infected = infected | new_i
            if len(infected) + len(recover) >= usrnum:
                break
            print("%d\t%d\t%d\t%d"%(st, len(infected), len(recover), seed_in), file=fp)
        print("Final %d"%(len(infected) + len(recover)), file=fp)
        r_num_avg += float(len(infected)+len(recover)) / avg
    fp.close()
    return r_num_avg


if __name__ == "__main__":
    #input NetWork
    with open("E:\\data\\FDUwifi13\\FudanWiFi_train_MEET_st.csv","r") as fin:
    #with open("E:\\data\\FDUwifi13\\FudanWiFi_test_MEET_st.csv","r") as fin:
        for line in tqdm.tqdm(fin.readlines(), ncols=25, desc="read"):
            u,v,t,l,st = line.strip().split(',')
            u = int(u)
            v = int(v)
            t = int(t)
            l = int(l)
            st = int(st)
            net_work.add(u, v, t)
            net_work.add(v, u, t)
    #seed = np.random.choice(usrnum, 50, replace=False)
    seed = [i for i in range(usrnum)]
    #seed = [4]
    param = []
    for i in seed:
        param.append([i, 0])
        param.append([i, 8])
        param.append([i, 56])
    #resluts = list(tqdm.tqdm(mp.Pool(mp.cpu_count()).imap(action, param), ncols=25, desc="simu"))
    resluts = []
    for i in tqdm.tqdm(param, ncols=25):
        resluts.append(action(i))

    tots = {}
    totcal = {0:0.0, 8:0.0, 56:0.0}
    totnum = 0
    with open("results.tsv",'w') as fout:
        for indx, se in enumerate(param):
            print("%d\t%d\t%f"%(se[0],se[1],resluts[indx]), file=fout)
            if not se[0] in tots:
                tots[se[0]] = {0:0.0, 8:0.0, 56:0.0}
            tots[se[0]][se[1]] = resluts[indx]
        for i in tots:
            if tots[i][0]!=0 and tots[i][8]!=0 and tots[i][56]!=0:
                totnum+=1
                totcal[0]+=tots[i][0]
                totcal[8]+=tots[i][8]
                totcal[56]+=tots[i][56]
        print("tot:", file=fout)
        for i in totcal:
            totcal[i]/=totnum
            print("%d\t%f"%(i, totcal[i]), file=fout)
