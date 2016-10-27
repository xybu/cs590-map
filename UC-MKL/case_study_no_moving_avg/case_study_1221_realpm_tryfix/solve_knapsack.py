with open('vwgts.txt', 'r') as f:
  weight = [int(v) for v in f.readlines()]

with open('1221.host', 'r') as f:
  cost = [int(v) for v in f.readlines()]

capacity = 80

assert(len(weight) == len(cost))

import numpy as num
 
def knapsack(v,w,W):
    n = len(v)
    c = num.zeros((n,W+1))
 
    for i in range(0,n):
        for j in range(0,W+1):
            if w[i]>j:
                c[i,j] = c[i-1,j]
            else:
                c[i,j] = max(c[i-1,j],v[i]+c[i-1,j-w[i]])
    return c 
 
def items(w,c):
    i = len(c)-1
    iterat = len(c[0,:])-1
 
    meh = []
 
    for i in range(i+1):
        meh.append(0)
    while(i>=0 and iterat>=0):
        if (i==0 and c[i,iterat]>0) or c[i,iterat] != c[i-1,iterat]:
            meh[i] = 1
            iterat = iterat-w[i]
        i -=1
    return meh 

c = knapsack(weight, cost, capacity)
sol = items(cost, c)

sum_weight = 0
sum_cost = 0
for i, v in enumerate(sol):
  if v == 1:
    print('Host {}: cpu={}, weight={}'.format(i, cost[i], weight[i]))
    sum_weight += weight[i]
    sum_cost += cost[i]

print('Total weight: %d' % sum_weight)
print('Total cost:   %d' % sum_cost)
