import Input_Extraction_Definition as IED
import Within_Variant_Summarization as WVS
from ocpa.visualization.log.variants import factory as variants_visualization_factory

def get_unique_summarizations(process):
    variant_layouting = variants_visualization_factory.apply(process)
    all_unique_summarizations_dict = dict()
    all_unique_summarizations_set = []
    all_summarizations = []

    for i in range(len(process.variants)):
        print("Summarizing variant " + str(i) + " of the process...")
        extracted_variant = IED.extract_lanes(variant_layouting[process.variants[i]])
        extracted_summarizations = WVS.within_variant_summarization(extracted_variant, False)

        for summarization in extracted_summarizations:
            all_summarizations.append(summarization)
            encoding = summarization.encode_lexicographically()

            if(encoding in all_unique_summarizations_dict.keys()):
                all_unique_summarizations_dict[encoding][0].append(i)
            else:
                all_unique_summarizations_dict[encoding] = ([i], summarization)
                all_unique_summarizations_set.append((encoding, summarization))

    return all_unique_summarizations_set, all_unique_summarizations_dict


def determine_subsets(universe, unique_summarizations):
    universe_T = list(zip(range(len(universe)), universe))
    subsets_S = dict()
    for key in list(unique_summarizations.keys()):
        for variant in unique_summarizations[key][0]:
            if(variant in subsets_S.keys()):
                subsets_S[variant].extend([elem for elem in universe_T if elem[1][0] == key])
            else:
                subsets_S[variant] = [elem for elem in universe_T if elem[1][0] == key]

    return universe_T, subsets_S


def solve_hitting_set_problem(T, S):
    import gurobipy
    model = gurobipy.Model("hittingSet")
    x = {}
    for elem in T:
        x[elem]=model.addVar(name="x_%s" % str(elem[0]), vtype = gurobipy.GRB.BINARY)

    model.update()

    for key in S.keys():
        model.addConstr(sum(x[elem] for elem in S[key]) >= 1)
    
    model.setObjective(sum(x[elem] for elem in T))
    model.modelSense = gurobipy.GRB.MINIMIZE
    model.optimize()
    print('\n Objective value: %g\n' % model.ObjVal)
    print('\n Variable values: \n')
    solution = []
    for elem in T:
        print(str(elem[0]) + ": " + str(x[elem].X))
        if(x[elem].X == 1.0):
            solution.append(elem)
    print("-----------------------------")
    return model, solution

def within_variant_selection(process):

    universe, summarization_dictionary = get_unique_summarizations(process)
    T, S = determine_subsets(universe, summarization_dictionary)
    model, solution = solve_hitting_set_problem(T, S)

    result = {}
    for key in summarization_dictionary.keys():
        if ([elem for elem in solution if elem[1][0] == key]):
            result[key] = summarization_dictionary[key]
    
    print(str(len(result)) + "/" + str(len(summarization_dictionary)) + " unique summarizations have been selected for the Between-Lane Summarizatation.")
    return result

