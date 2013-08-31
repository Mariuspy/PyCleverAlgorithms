#!/usr/bin/env python

def objective_function(v):
    return sum(map(lambda x : x**2, v))

def random_vector(minmax):
    import random
    return map(lambda x : x[0] + (x[1]-x[0]) * random.random(), minmax)

def search(search_space, max_iter):
    best = None
    for iter in range(0, max_iter):
        candidate = {}
        candidate['vector'] = random_vector(search_space)
        candidate['cost']   = objective_function(candidate['vector'])
        if best is None or candidate['cost'] < best['cost']:
            best = candidate
        print ' > iteration=%d, best=%f' % (iter+1, best['cost'])
    return best

def main():
    #
    problem_size = 2
    search_space = [[-5,5]] * problem_size
    #
    max_iter = 100
    #
    best = search(search_space, max_iter)
    print 'Done. Best Solution: c=%f, v=%s' % (best['cost'], str(best['vector']))

if __name__ == "__main__":
    main()