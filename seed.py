import multiprocessing as mp
import random
import numpy as np
import tqdm
import argparse
from collections import defaultdict

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
alpha = 5
avg = 100
x = 6
usrnum = 10145


def action(seed, cd):
    '''
    Doing OSIR simulation
    return differencial sequences
    '''
    steps = net_work.get_steps()
    s_record = [[0 for j in range(steps)] for i in range(alpha)]
    i_record = [0 for j in range(steps)]
    r_record = [0 for j in range(steps)]
    time_record = [0 for j in range(steps)]
    for ii in range(avg):
        infected = set()
        recover = set()
        info = defaultdict(int)
        start = False
        seed_last_st = -1
        seed_times = 0
        for st in steps:
            seed_in = 0
            if seed_times >= x and len(infected) == 0:
                #print("%d_%d out in %d : %d"%(seed, cd, st, seed_times))
                break
            time_record[st] += 1
            #SEED
            if seed_times < x and net_work.check(seed, st):
                real_st = net_work.get_real_st(st)
                if ((not start) or (start and real_st - seed_last_st >= cd)):
                    seed_last_st = real_st
                    seed_in = 1
                    start = True
                    seed_times += 1
                    ne = net_work.get_neighbor(seed, st)
                    for j in ne:
                        if ((not j in infected) and (not j in recover)):
                            s_record[info[j]][st][0] -= 1
                            s_record[info[j]][st][1] += 1
                            info[j] += 1
                            if info[j] >= alpha:
                                infected.add(j)
                                i_record[st][0] += 1
                                i_record[st][1] += 1
                                info.pop(j)
                            else:
                                s_record[info[j]][st][0] += 1
                                s_record[info[j]][st][0] += 1
            #Infected
            recoverd_i = set()
            new_i = set()
            for i_node in infected:
                if net_work.check(i_node, st):
                    ne = net_work.get_neighbor(i_node, st)
                    for j in ne:
                        if j!=seed and random.uniform(0,1) < beta and\
                            not j in infected and not j in recover and not j in new_i:
                            s_record[info[j]][st] -= 1
                            info[j] += 1
                            if info[j] >= alpha:
                                new_i.add(j)
                                i_record[st] += 1
                                info.pop(j)
                            else:
                                s_record[info[j]][st] += 1
                #Recover
                if random.uniform(0,1) < theta:
                    recoverd_i.add(i_node)
                    i_record[st] -= 1
                    recover.add(i_node)
                    r_record[st] += 1
            infected = infected - recoverd_i
            infected = infected | new_i
            if len(infected) + len(recover) >= usrnum:
                break
        print("Round(%d/%d): Final %d"%(ii, avg, len(infected) + len(recover)))
    return s_record, i_record, r_record, time_record


parser = argparse.ArgumentParser()
parser.add_argument("--p", type=int, default=0, help="Interval of source join the net work")
parser.add_argument("--seed_num", type=int, default=50, help="Seeds number of this simulation")
args = parser.parse_args()

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
    seeds = np.random.choice(usrnum, args.seed_num), replace=False)
    #seed = [4]

    print("Start simulation--------")
    for one_seed in seeds:
        s_record, i_record, r_record, time_record = action(one_seed, args.p)

        x = [0]
        y_s = [[] in range(alpha)]
        y_i = [0]
        y_r = [0]
        y_s[0].append(usrnum)
        for i in range(1, alpha):
            y_s[0].append(0)
        for indx, ts in enumerate(time_record):
            if ts == 0:
                break
            i = indx + 1
            for j in range(alpha):
                y_s[j].append(y_s[j][-1] + s_record[j][indx])
            y_i.append(y_i[-1] + i_record[indx])
            y_r.append(y_r[-1] + r_record[indx])

        #output to file
        fp = open("result_%d_%d.txt"%(one_seed, args.p),'w')
        for i in y_s:
            tmp = [str(j) for j in i]
            print(' '.join(tmp), file = fp)
        tmp = [str(j) for j in y_i]
        print(' '.join(tmp), file = fp)
        tmp = [str(j) for j in y_r]
        print(' '.join(tmp), file = fp)

        #plot
        s_color = [(55,126,184),(77,175,74),(152,78,163),(225,225,51),(166,86,40)]
        s_color = [(i[0]/256,i[1]/256,i[2]/256) for i in s_color]
        s_mk = ['o','v','^','<','>']
        i_color = (228/256,26/256,28/256)
        i_mk = 's'
        r_color = (247/256,129/256,191/256)
        r_mk = 'p'
        for indx, y in enumerate(y_s):
            plt.plot(x, y, label="S_"+str(indx), marker=s_mk[indx%(len(s_color))], color=s_color[indx%(len(s_color))])
        plt.plot(x, self.r_I, label="I", marker=i_mk, color=i_color)
        plt.plot(x, self.r_R, label="R", marker=r_mk, color=r_color)
        #ax.plot(x, self.r_sum, label="SUM", marker='o')
        plt.xlabel("time step")
        plt.ylabel("the number of nodes")
        plt.legend(loc=2, bbox_to_anchor=(1.05,1.0),borderaxespad = 0.)
        plt.savefig("pic_%d_%d.png"%(one_seed, args.p))
        plt.close()
