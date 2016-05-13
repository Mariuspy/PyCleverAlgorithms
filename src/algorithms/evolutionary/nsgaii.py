#!/usr/bin/env python

"""
Non-dominated Sorting Genetic Algorithm II (NSGA II)

Encoding approach: binary

"""


def iif(condition, true_part, false_part):
    return (condition and [true_part] or [false_part])[0]


def objective1(v):
    return sum(map(lambda x: x ** 2, v))


def objective2(v):
    return sum(map(lambda x: (x - 2.0) ** 2, v))


def decode(bitstring, search_space, bits_per_param):
    vector = []
    for i, bounds in enumerate(search_space):
        off, sum_v = i*bits_per_param, 0.0
        param = bitstring[off:(off+bits_per_param)][::-1]
        for j in xrange(len(param)):
            sum_v += iif(param[j] == '1', 1.0, 0.0) * (2.0 ** float(j))

        min_v, max_v = bounds
        vector.append(min_v + ((max_v-min_v)/((2.0**float(bits_per_param))-1.0)) * sum_v)
    return vector


def random_bitstring(num_bits):
    from random import sample
    return map(lambda x: iif(x < 50, '1', '0'), sample(range(100), num_bits))


def point_mutation(bitstring, rate):
    from random import random
    child = ""
    for i in xrange(0, len(bitstring)):
        bit = bitstring[i]
        child = child + iif(random() < rate, iif(bit == '1', '0', '1'), bit)
    return child


def crossover(parent1, parent2, rate):
    from random import random
    if random() >= rate:
        return parent1
    child = ""
    for i in xrange(len(parent1)):
        child += iif(random() < 0.5, parent1[i], parent2[i])
    return child


def reproduce(selected, pop_size, p_cross):
    children = []
    for i, p1 in enumerate(selected):
        p2 = None
        if i == len(selected)-1:
            p2 = selected[0]
        else:
            p2 = iif(i % 2 == 0, selected[i+1], selected[i-1])
        child = {}
        child['bitstring'] = crossover(p1['bitstring'], p2['bitstring'], p_cross)
        child['bitstring'] = point_mutation(child['bitstring'], 1.0/len(child['bitstring']))
        children.append(child)
        if len(children) >= pop_size:
            break
    return children


def calculate_objectives(pop, search_space, bits_per_param):
    for p in pop:
        p['vector'] = decode(p['bitstring'], search_space, bits_per_param)
        p['objectives'] = [objective1(p['vector']), objective2(p['vector'])]


def dominates(p1, p2):
    for i in xrange(len(p1['objectives'])):
        if p1['objectives'][i] > p2['objectives'][i]:
            return False
    return True


def fast_nondominated_sort(pop):
    fronts = []
    first_front = []
    count = 0
    for p1 in pop:
        count += 1
        p1['dom_count'] = 0
        p1['dom_set'] = []
        for p2 in pop:
            if dominates(p1, p2):
                p1['dom_set'].append(p2)
            elif dominates(p2, p1):
                p1['dom_count'] += 1
        if p1['dom_count'] == 0:
            p1['rank'] = 0
            first_front.append(p1)
    fronts.append(first_front)
    curr = 0
    while True:
        next_front = []
        for p1 in fronts[curr]:
            for p2 in p1['dom_set']:
                p2['dom_count'] -= 1
                if p2['dom_count'] == 0:
                    p2['rank'] = curr + 1
                    next_front.append(p2)
        curr += 1
        if len(next_front) > 0:
            fronts.append(next_front)
        if curr >= len(fronts):
            break
    return fronts


def calculate_crowding_distance(pop):
    for p in pop:
        p['dist'] = 0.0
    num_obs = len(pop[0]['objectives'])
    for i in xrange(num_obs):
        min_v = min(pop, key=lambda x: x['objectives'][i])
        max_v = max(pop, key=lambda x: x['objectives'][i])
        rge = max_v['objectives'][i] - min_v['objectives'][i]
        # pop[0]['dist'], pop[-1]['dist'] = 1.0/0.0, 1.0/0.0
        if rge == 0.0:
            continue
        for j in xrange(1, len(pop)-1):
            pop[j]['dist'] += (pop[j+1]['objectives'][i]-pop[j-1]['objectives'][i])/rge


def crowded_comparison_operator(x, y):
    return iif(x['rank'] == y['rank'], cmp(y['dist'], x['dist']), cmp(x['rank'], y['rank']))


def better(x, y):
    if 'dist' in x and x['rank'] == y['rank']:
        return iif(x['dist'] > y['dist'], x, y)
    return iif(x['rank'] < y['rank'], x, y)


def select_parents(fronts, pop_size):
    for f in fronts:
        calculate_crowding_distance(f)
    offspring = []
    last_front = 0
    for front in fronts:
        if len(offspring) + len(front) > pop_size:
            break
        for p in front:
            offspring.append(p)
        last_front += 1
    remaining = pop_size-len(offspring)
    if remaining > 0:
        fronts[last_front].sort(cmp=crowded_comparison_operator)
        for i in range(remaining):
            offspring.append(fronts[last_front][i])
    return offspring


def weighted_sum(x):
    return sum(x['objectives'])


def search(search_space, max_gens, pop_size, p_cross, bits_per_param=16):
    from random import randint
    pop = [{'bitstring': random_bitstring(len(search_space)*bits_per_param)} for i in xrange(pop_size)]
    calculate_objectives(pop, search_space, bits_per_param)
    fast_nondominated_sort(pop)
    selected = []
    for i in xrange(pop_size):
        selected.append(better(pop[randint(0, pop_size-1)], pop[randint(0, pop_size-1)]))
    children = reproduce(selected, pop_size, p_cross)
    calculate_objectives(children, search_space, bits_per_param)
    for gen in xrange(max_gens):
        union = pop + children
        fronts = fast_nondominated_sort(union)
        parents = select_parents(fronts, pop_size)
        selected = []
        #print len(parents)
        for i in xrange(pop_size):
            selected.append(better(parents[randint(0, pop_size-1)], parents[randint(0, pop_size-1)]))
        pop = children
        children = reproduce(selected, pop_size, p_cross)
        calculate_objectives(children, search_space, bits_per_param)
        parents.sort(key=lambda x: weighted_sum(x))
        best = parents[0]
        print "> gen=%d, fronts=%d, best=%s" % (gen, len(fronts), best["objectives"])

    union = pop + children
    fronts = fast_nondominated_sort(union)
    parents = select_parents(fronts, pop_size)
    return parents


def main():
    # problem configuration
    problem_size = 1
    search_space = [[-10, 10]] * problem_size
    # algorithm configuration
    max_gens = 100
    pop_size = 100
    p_cross = 0.98
    # execute the algorithm
    pop = search(search_space, max_gens, pop_size, p_cross)
    print "done!"


if __name__ == "__main__":
    main()
