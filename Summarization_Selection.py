
def __solve_hitting_set_problem(T, S):
    '''
    Solves the Hitting Set Problem for a universe T and subsets S in an IP.
    :param T: The universe of all instances
    :type T: list
    :param S: The subsets over the instances of T
    :type S: dict
    :return: A list containing all selected instances in T
    :rtype: list
    '''
    import gurobipy
    model = gurobipy.Model("hittingSet")
    x = {}
    for elem in T:
        x[elem[1][0]]=model.addVar(name="x_%s" % str(elem[0]), vtype = gurobipy.GRB.BINARY)

    model.update()

    for key in S.keys():
        model.addConstr(sum(x[elem[1][0]] for elem in S[key]) == 1)
    
    model.setObjective(sum(x[elem[1][0]] for elem in T))
    model.modelSense = gurobipy.GRB.MINIMIZE
    model.optimize()
    print('\n Objective value: %g\n' % model.ObjVal)
    print('\n Variable values: \n')
    solution = []
    for elem in T:
        print(str(elem[0]) + ": " + str(x[elem[1][0]].X))
        if(x[elem[1][0]].X == 1.0):
            solution.append(elem)
    print("-----------------------------")
    return solution


def intra_variant_summarization_selection(all_summarizations, summarizations_per_variant, summarizations_per_encoding):
    '''
    The initial set of Super Variants is selected using the Hitting Set Problem based on given Intra-Variant-Summarizations.
    :param all_summarizations: A list of all unique_summarizations
    :type all_summarizations: list
    :param summarizations_per_variant: A dictionary mapping variant to it's set of summarizations
    :type summarizations_per_variant: dict
    :param summarizations_per_encoding: A dictionary mapping unique summarizations to their SummarizedVariant instances
    :type summarizations_per_encoding: dict
    :return: A list containing all selected Intra-Variant Summarizations
    :rtype: dict
    '''
    solution = __solve_hitting_set_problem(all_summarizations, summarizations_per_variant)

    result = {}
    for key in summarizations_per_encoding.keys():
        if ([elem for elem in solution if elem[1][0] == key]):
            result[key] = summarizations_per_encoding[key]
    
    print(str(len(result)) + "/" + str(len(summarizations_per_encoding)) + " unique summarizations have been selected for the Between-Lane Summarizatation.")

    initial_set_of_super_variants = []
    
    for key in result.keys():

        frequency = 0
        for summarization in  result[key][1]:
            frequency += summarization.frequency

        initial_set_of_super_variants.append(result[key][1][0].to_super_variant(tuple(result[key][0])))
        initial_set_of_super_variants[-1].frequency = frequency

    return initial_set_of_super_variants



