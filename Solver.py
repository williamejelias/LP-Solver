from ortools.linear_solver import pywraplp
import networkx as nx
import sys
from itertools import chain, combinations, permutations
from fractions import Fraction


def main():
    g, g_string = read_argument_graph()
    fcg = fractional_clique_cover(g)
    se = shannon_entropy(g)
    solution = g_string + "\n\n" + fcg + "\n\n" + se
    try:
        filename = sys.argv[2]
        save_to_file(filename, solution)
    except Exception as msg:
        # filename not given
        pass
    print(solution)
    subsets(g)


def read_argument_graph():
    try:
        result_string = "*** INPUT GRAPH ***\n"
        filename = sys.argv[1]
        with open(filename) as f:
            content = f.readlines()

        g = nx.Graph()
        i = 0
        while i < len(content):
            line = content[i].strip()
            x, *y = line.split()
            string = "Node: " + str(x) + " Connected to: " + str(y) + "\n"
            result_string += string
            for n in y:
                g.add_edge(x, n)
            i += 1
        return g, result_string
    except Exception as msg:
        print(msg)
        print("Error reading from file")
        exit()


def subsets(graph):
    s = sorted(list(graph.nodes))
    s_sets = list(chain.from_iterable(combinations(s, r) for r in range(len(s) + 1)))
    return s_sets


def is_clique(sub_graph):
    num_nodes = len(sub_graph.nodes())
    num_edges = len(sub_graph.edges())
    # 0 or 1 nodes is a clique
    if num_nodes == 0 or num_nodes == 1:
        return True
    else:
        if num_nodes == 2:
            return num_edges == 1
        else:
            return num_edges == (1 / 2 * num_nodes * (num_nodes - 1))


def fractional_clique_cover(graph):
    solver = pywraplp.Solver('FractionalCliqueCoverNumber',
                             pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

    objective = solver.Objective()

    num_nodes = len(graph.nodes)
    g_nodes = list(graph.nodes)
    s_sets = subsets(graph)

    cliques = []
    variables = {}
    # objective
    for i in range(0, len(s_sets)):
        subset = s_sets[i]
        nodes = list(subset)
        s_sets[i] = nodes
        sgraph = graph.subgraph(nodes)
        name = "".join(nodes)
        c = is_clique(sgraph)
        # is clique
        if c:
            cliques.append(nodes)
            variables[name] = [solver.NumVar(0.0, solver.infinity(), name), nodes]

            # add to objective function
            objective.SetCoefficient(variables[name][0], 1)

    # constraints
    constraints = [0] * num_nodes
    for i in range(0, num_nodes):
        node = g_nodes[i]
        cliques_containing_node = [x for x in cliques if node in x]
        constraints[i] = solver.Constraint(1.0, solver.infinity())

        # variables in objective need to be subjected to this constraint
        for c in cliques_containing_node:
            name = "".join(c)
            constraints[i].SetCoefficient(variables[name][0], 1)

    # minimise
    objective.SetMinimization()

    # Solve!
    status = solver.Solve()

    result_string = "*** Fractional Clique Cover Number ***\n"

    if status == solver.OPTIMAL:
        sum = 0
        for k in variables:
            v = Fraction(variables[k][0].solution_value()).limit_denominator()
            sum += v
            string = "Clique with nodes:" + str(variables[k][1]) + " has x_s value " + str(v) + "\n"
            result_string += string
        string = "Optimal Fractional Clique Cover Number " + u'\u03C0' + "*(G): " + str(
            Fraction(sum).limit_denominator())
        result_string += string
    else:  # No optimal solution was found.
        if status == solver.FEASIBLE:
            string = "A potentially suboptimal solution was found for the Fraction Clique Cover Number.\n"
            result_string += string
        else:
            string = "The solver could not solve the Fractional Clique Cover Number for this graph.\n"
            result_string += string
    return result_string


def neighbourhood_of(graph, list, neighbours):
    if len(list) == 1:
        node = list[0]
        ns = [x[1] for x in graph.edges(node)]
        return neighbours == ns
    return False


def subset_of(list, neighbours):
    return set(list) <= set(neighbours)


def shannon_entropy(graph):
    solver = pywraplp.Solver('FractionalCliqueCoverNumber',
                             pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

    objective = solver.Objective()

    g_nodes = sorted(list(graph.nodes))
    s_sets = subsets(graph)
    v_name = "".join(g_nodes)

    variables = {}
    # variables in objective
    for i in range(0, len(s_sets)):
        subset = s_sets[i]
        nodes = list(subset)
        s_sets[i] = nodes
        name = "".join(nodes)

        # entropy of a single node is greater than zero and less than 1
        if len(nodes) == 1:
            variables[name] = [solver.NumVar(0.0, 1.0, name), nodes]

        # entropy of a subset is greater than zero
        elif len(nodes) > 1:
            variables[name] = [solver.NumVar(0.0, solver.infinity(), name), nodes]
            # add to objective function
            if len(nodes) == len(g_nodes):
                objective.SetCoefficient(variables[name][0], 1)

    # constraints
    # all pairs of subsets
    pairs = [x for x in permutations(s_sets, r=2) if len(x[0]) <= len(x[1])]
    for p in pairs:
        s1, s2 = p[0], p[1]
        s1_name = "".join(s1)
        s2_name = "".join(s2)

        # for any two sets
        # if one set is the neighbourhood of another single node set
        if neighbourhood_of(graph, s1, s2):
            union = sorted(list(set(s1).union(set(s2))))
            union_name = "".join(union)
            # print("CONSTRAINT 1: ", s1, " has neighbourhood ", s2, " union of: ", union, " ---> x(",union,") - x(",
            # s2,") = 0")
            constraint = solver.Constraint(0.0, 0.0)
            constraint.SetCoefficient(variables[union_name][0], 1)
            constraint.SetCoefficient(variables[s2_name][0], -1)

        # if one s1 is a subset of s2
        if subset_of(s1, s2):
            # print("CONSTRAINT 2: ", s1, " is subset of ", s2, " ---> x(",s2,") - x(",s1,") >= 0")
            constraint = solver.Constraint(0.0, solver.infinity())
            constraint.SetCoefficient(variables[s2_name][0], 1)
            if s1_name != '':
                constraint.SetCoefficient(variables[s1_name][0], -1)
        # pairs that satisfy constraint 2 make constraint 3 trivial
        else:
            # all other sets follow last constraint
            constraint = solver.Constraint(0.0, solver.infinity())
            common_list = sorted(list(set(s1) & set(s2)))
            total_list = sorted(list(set(s1).union(set(s2))))
            common_name = "".join(common_list)
            total_name = "".join(total_list)

            # 1 * s1
            if s1_name != '':
                constraint.SetCoefficient(variables[s1_name][0], 1)
            # 1 * s2
            constraint.SetCoefficient(variables[s2_name][0], 1)
            # -1 * total
            constraint.SetCoefficient(variables[total_name][0], -1)
            # -1 * common
            if common_name != '':
                constraint.SetCoefficient(variables[common_name][0], -1)

            # print("CONSTRAINT 3: ", s1, s2, " total: ", total_list, " common: ", common_list, " ---> x(",s1,
            # ") + x(",s2,") - x(",total_list,") - x(",common_list,") >= 0 ")
    # maximise
    objective.SetMaximization()

    # Solve!
    status = solver.Solve()

    # handle result
    result_string = "*** Shannon Entropy ***\n"
    if status == solver.OPTIMAL:
        sum = 0
        string = "Subset with nodes:[] has x_v value 0\n"
        result_string += string
        for k in variables:
            v = Fraction(variables[k][0].solution_value()).limit_denominator()
            sum += v
            string = "Subset with nodes:" + str(variables[k][1]) + " has x_v value " + str(v) + "\n"
            result_string += string
        string = "Optimal Shannon Entropy " + u'\u03B7' + "(G): " + str(
            Fraction(variables[v_name][0].solution_value()).limit_denominator())
        result_string += string
    else:  # No optimal solution was found.
        if status == solver.FEASIBLE:
            string = "A potentially suboptimal solution was found for the Shannon Entropy.\n"
            result_string += string
        else:
            string = "The solver could not solve the Shannon Entropy for this graph.\n"
            result_string += string
    return result_string


def save_to_file(filename, string):
    text_file = open(filename, "w")
    text_file.write(string)
    text_file.close()


if __name__ == '__main__':
    main()
