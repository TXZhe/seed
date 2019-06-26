import random

def ER_based(N, k_avg, T, M, mu):
    if N < 2 or k_avg >= N:
        print("params error")
        exit()
    def ER_net(n, p):
        ans = set()
        for i in range(n):
            for j in range(i+1, n):
                if random.uniform(0, 1) < p:
                    ans.add((i, j))
        return ans
    final_net = []
    #Generate first period
    basic_net = []
    for i in range(T):
        basic_net.append(ER_net(N, k_avg/(N-1)))
    final_net.append(basic_net)
    #Generate others
    for i in range(M-1):
        next_p = []
        for j, net in enumerate(basic_net):
            preserve_edge = int(len(net)*mu)
            preserve_net = random.sample(list(net), preserve_edge)
            preserve_net = set(preserve_net)
            while(len(preserve_net) < len(net)):
                a = random.randint(0, N-1)
                b = random.randint(0, N-1)
                if a > b:
                    a,b = b,a
                if a!=b and not (a, b) in preserve_net:
                    preserve_net.add((a, b))
            next_p.append(preserve_net)
        final_net.append(next_p)
    final_edge = []
    ts = 0
    for one_p in final_net:
        next_p = []
        #print("**************")
        for one_d in one_p:
            #print("-------------")
            for one_e in one_d:
                next_p.append((ts, one_e[0], one_e[1]))
            ts+=1
        final_edge.append(next_p)
    return final_edge

def Group_based(N, k_avg, T, M, mu):
    group_size = k_avg + 1
    if N < 2 or k_avg >= N or N // group_size * group_size != N:
        print("params error")
        exit()
    group_num = N // group_size
    preserve_num = int(group_size*mu)
    final_net = []
    #Generate first period
    basic_net = []
    for i in range(T):
        one_net = []
        rand_list = list(range(N))
        random.shuffle(rand_list)
        for j in range(group_num):
            one_net.append(rand_list[group_size*j : group_size*(j+1)])
        basic_net.append(one_net)
    final_net.append(basic_net)
    #Generate others
    for i in range(M-1):
        next_p = []
        for j, net in enumerate(basic_net):
            next_step = []
            tot_drop = set()
            for one_group in net:
                preserve = random.sample(one_group, preserve_num)
                drop = set(one_group)-set(preserve)
                tot_drop = tot_drop | drop
                next_step.append(preserve)
            rand_drop = list(tot_drop)
            random.shuffle(rand_drop)
            for z in range(group_num):
                next_step[z].extend(rand_drop[(group_size-preserve_num)*z : (group_size-preserve_num)*(z+1)])
            next_p.append(next_step)
        final_net.append(next_p)
    final_edge = []
    ts = 0
    for one_p in final_net:
        next_p = []
        #print("**************")
        for one_d in one_p:
            #print("-------------")
            for one_g in one_d:
                #print(one_g)
                for i in range(len(one_g)):
                    for j in range(i+1, len(one_g)):
                        next_p.append((ts, one_g[i], one_g[j]))
            ts+=1
        final_edge.append(next_p)
    return final_edge


if __name__ == "__main__":
    mu = 0.5
    net = Group_based(100, 9, 5, 100, mu)
    #net = ER_based(20, 4, 2, 3, 0.5)
    with open("edge_st_%.2f.csv"%(mu),'w') as fout:
        for indx, one_p in enumerate(net):
            for e in one_p:
                print("%d,%d,%d"%(e[0], e[1], e[2]), file=fout)
