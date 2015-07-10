from random import random, randint, choice
from copy import deepcopy
from math import log

class func_wrapper(object):
    def __init__(self, function, childcount, name):
        self.function = function
        self.childcount = childcount
        self.name = name

class node(object):
    def __init__(self, fw, children):
        self.function = fw.function
        self.name = fw.name
        self.children = children

    def evaluate(self, inp):
        results = [child.evaluate(inp) for child in self.children]
        return self.function(results)

    def display(self, indent=0):
        print (' ' * indent) + self.name
        for c in self.children:
            c.display(indent + 1)

class param_node(object):
    def __init__(self, idx):
        self.idx = idx

    def evaluate(self, inp):
        return inp[self.idx]

    def display(self, indent=0):
        print '%sp[%d]' % (' ' * indent, self.idx)

class const_node(object):
    def __init__(self, v):
        self.v = v

    def evaluate(self, inp):
        return self.v

    def display(self, indent=0):
        print '%s%d' % (' ' * indent, self.v)

addw = func_wrapper(lambda l : l[0] + l[1], 2, 'add')
subw = func_wrapper(lambda l : l[0] - l[1], 2, 'subtract')
mulw = func_wrapper(lambda l : l[0] * l[1], 2, 'multiply')

def iffunc(l):
    return l[1] if l[0] > 0 else l[2]
ifw = func_wrapper(iffunc, 3, 'if')

def isgreater(l):
    return 1 if l[0] > l[1] else 0
gtw = func_wrapper(isgreater, 2, 'isgreater')

flist = [addw, mulw, subw, ifw, gtw]

def example_tree():
    return node(ifw, [node(gtw, [param_node(0), const_node(3)]),
            node(addw, [param_node(1), const_node(2)]),
            const_node(3)])

def test_example_tree():
    tree = example_tree()
    print tree.evaluate([1, 2])
    print tree.evaluate([10, 2])

    tree.display()

def make_random_tree(param_cnt, maxdepth=4, func_p=0.5, param_p=0.3):
    round_p = random()
    if round_p < func_p and maxdepth > 0:
        f = choice(flist)
        children = [make_random_tree(param_cnt, maxdepth - 1)
            for i in range(f.childcount)]
        return node(f, children)
    elif round_p < func_p + param_p:
        return param_node(randint(0, param_cnt - 1))
    else:
        return const_node(randint(0, 10))

def score_func(tree, data_set):
    return sum([abs(tree.evaluate(data[0:2]) - data[2]) for data in data_set])

def hidden_func(x, y):
    return x * y if x > y else y * y

def build_hidden_func_set():
    rows = []
    for num in xrange(200):
        a = randint(0, 40)
        b = randint(0, 40)
        rows.append([a, b, hidden_func(a, b)])
    return rows

def mutate(tree, param_cnt, depth=4, prob_change=0.1):
    if random() < prob_change:
        return make_random_tree(param_cnt, depth)
    else:
        result = deepcopy(tree)
        if isinstance(tree, node):
            result.children = [mutate(ch_tree, param_cnt, depth - 1, prob_change) for ch_tree in tree.children]
        return result

def cross_over(t1, t2, prob_swap=0.7, top=True):
    if random() < prob_swap and not top:
        return deepcopy(t2)
    else:
        result = deepcopy(t1)
        if isinstance(t1, node) and isinstance(t2, node):
            result.children = [cross_over(ch_tree, choice(t2.children), prob_swap, False) for ch_tree in t1.children]
        return result

def evolove(param_cnt, popsize, rankfunc, maxgen=500, mutationrate=0.1, breedingrate=0.4,
        pexp=0.7, pnew=0.05):
    def selectindex():
        return int(log(random()) / log(pexp))

    population = [make_random_tree(param_cnt) for i in xrange(popsize)]
    for i in xrange(maxgen):
        scores = rankfunc(population)
        print 'Best score:', scores[0][0]
        if scores[0][0] == 0: break

        newpop = [scores[0][1], scores[1][1]]
        while len(newpop) < popsize:
            if random() > pnew:
                newpop.append(mutate(cross_over(
                    scores[selectindex()][1],
                    scores[selectindex()][1],
                    prob_swap=breedingrate),
                param_cnt, prob_change=mutationrate))
            else:
                newpop.append(make_random_tree(param_cnt))
        population = newpop

    scores[0][1].display()
    return scores[0][1]

def rank_function(data_set):
    def rank_func(population):
        scores = [(score_func(pop, data_set), pop) for pop in population]
        scores.sort()
        return scores
    return rank_func

def test_random_tree():
    test_set = build_hidden_func_set()
    rt_1 = make_random_tree(2, 4, 0.99)
    rt_1.display()
    print score_func(rt_1, test_set)

    rt_2 = make_random_tree(2, 4, 0.99)
    rt_2.display()
    print score_func(rt_2, test_set)

    rt_3 = cross_over(rt_1, rt_2)
    rt_3.display()
    print score_func(rt_3, test_set)

def test_evolution():
    rf = rank_function(build_hidden_func_set())
    evolove(2, 500, rf, mutationrate=0.2, breedingrate=0.1, pexp=0.7, pnew=0.1)

if __name__ == '__main__':
    test_evolution()
