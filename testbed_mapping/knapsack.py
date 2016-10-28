import numpy as num


def knapsack(v, w, W):
    """
    Solve the knapsack matrix.
    :param list[int] v: An array that stores the value (profit) of each item.
    :param list[int] w: An array that stores the weight (cost) of each item.
    :param int W: Capacity of the knapsack.
    :return list[list[int]]: The knapsack matrix where first index is item and second index is capacity.
    """
    n = len(v)
    c = num.zeros((n, W+1))

    for i in range(0, n):
        for j in range(0, W+1):
            if w[i] > j:
                c[i, j] = c[i-1, j]
            else:
                c[i, j] = max(c[i-1, j], v[i]+c[i-1, j-w[i]])
    return c


def knapsack_max_value(c):
    """
    Return the max profit from knapsack solver.
    :param list[list[int]] c: The knapsack matrix returned by knapsack().
    :return int: The maximum profit of the knapsack problem.
    """
    return c[-1][-1]


def knapsack_items(w, c):
    """
    Reverse engineer the list of items chosen for the knapsack problem.
    :param list[int] w: An array that stores the weight (cost) of each item.
    :param list[list[int]] c: The knapsack matrix returned by knapsack().
    :return list[int]: The list of chosen items.
    """
    i = len(c)-1
    meh = [0] * (i + 1)
    iterat = len(c[0, :]) - 1

    while(i >= 0 and iterat >= 0):
        if (i == 0 and c[i, iterat] > 0) or c[i, iterat] != c[i-1, iterat]:
            meh[i] = 1
            iterat = iterat-w[i]
        i -= 1
    return meh


if __name__ == '__main__':

    with open('vwgts.txt', 'r') as f:
        weight = [int(v) for v in f.readlines()]

    with open('1221.host', 'r') as f:
        cost = [int(v) for v in f.readlines()]

    capacity = 80

    assert (len(weight) == len(cost))

    c = knapsack(weight, cost, capacity)
    sol = knapsack_items(cost, c)

    print(knapsack_max_value(c))

    sum_weight = 0
    sum_cost = 0
    for i, v in enumerate(sol):
        if v == 1:
            print('Host {}: cpu={}, weight={}'.format(i, cost[i], weight[i]))
            sum_weight += weight[i]
            sum_cost += cost[i]

    print('Total weight: %d' % sum_weight)
    print('Total cost:   %d' % sum_cost)
