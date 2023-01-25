import Inter_Variant_Summarization as IVS
import Summarization_Selection as SS
import Super_Variant_Visualization as SVV
import copy 
import math


def generate_super_variant_hierarchy_logarithmic(initial_super_variant_set, number_of_level):
    
    if(len(initial_super_variant_set) == 1):
        result = dict()
        result[1] = (initial_super_variant_set,0)
        return result
        
    else:
        indexed_initial_set = dict()
        for i, super_variant in enumerate(initial_super_variant_set):
            indexed_initial_set[i] = super_variant

        indexed_initial_set_remaining = copy.deepcopy(indexed_initial_set)
        matchings = dict()

        # keys might need shuffling
        for i in indexed_initial_set.keys():
            if(i in indexed_initial_set_remaining.keys()):

                minimal_cost = math.inf
                minimal_cost_mapping = None
                minimal_cost_index = i

                for j in indexed_initial_set_remaining.keys():

                    if (j > i):
                        mapping, cost = IVS.decide_matching(indexed_initial_set_remaining[i], indexed_initial_set_remaining[j], copy.deepcopy(indexed_initial_set_remaining[i].lanes), copy.deepcopy(indexed_initial_set_remaining[j].lanes), True, False)
                        if(cost < minimal_cost):
                            minimal_cost = cost
                            minimal_cost_mapping = mapping
                            minimal_cost_index = j

                matchings[i, minimal_cost_index] = (minimal_cost_mapping, minimal_cost)

                del indexed_initial_set_remaining[i]

                if(minimal_cost_index != i):
                    del indexed_initial_set_remaining[minimal_cost_index]

        level_result = []
        accumulated_cost = 0
        for matching in matchings.keys():
            if(matching[0] != matching[1]):
                super_variant1 = indexed_initial_set[matching[0]]
                super_variant2 = indexed_initial_set[matching[1]]
                super_variant = IVS.inter_variant_summarization(super_variant1, super_variant2, matchings[matching][0], False, False)
                level_result.append(super_variant)
                accumulated_cost += matchings[matching][1]
            else:
                level_result.append(indexed_initial_set[matching[0]])

        
        for super_variant in level_result:
            SVV.visualize_super_variant(super_variant)

        if(number_of_level == 1):
            result = dict()
        else:
            result = generate_super_variant_hierarchy_logarithmic(level_result, number_of_level-1)

        result[number_of_level] = (level_result, accumulated_cost)
        return result

def generate_super_variant_hierarchy_uniform(initial_super_variant_set, number_of_final_super_variants):
    
    if(len(initial_super_variant_set) <= number_of_final_super_variants):
        result = dict()
        result[1] = initial_super_variant_set
        return result
        
    else:
        # cluster best possible
        indexed_initial_set = dict()
        for i, super_variant in enumerate(initial_super_variant_set):
            indexed_initial_set[i] = super_variant

        model, result = cluster_initial_super_variant_set(indexed_initial_set, number_of_final_super_variants)

        intermediate_results = []
        for cluster in result:
            number_of_levels = math.ceil(math.log(len(list(cluster.keys())), 2))
            print(number_of_levels)
            cluster_result = generate_super_variant_hierarchy_logarithmic(list(cluster.values()), number_of_levels)
            intermediate_results.append(cluster_result)

        result = dict()
        longest_intermediate_result = max(intermediate_results, key=lambda x:len(list(x.keys())))
            
        for key in longest_intermediate_result.keys():
            super_variants = []
            accumulated_cost = 0
            for intermediate_result in intermediate_results:
                if key in intermediate_result.keys():
                    super_variants.extend(intermediate_result[key][0])
                    accumulated_cost += intermediate_result[key][1]
            result[key] = (super_variants, accumulated_cost)

        return result
    

def cluster_initial_super_variant_set(indexed_initial_set, number_of_clusters):
    accumulated_frequency = sum([indexed_initial_set[index].frequency for index in indexed_initial_set.keys()])
    ideal_cluster_frequency = accumulated_frequency/number_of_clusters

    import gurobipy
    model = gurobipy.Model("Clustering")
    x = {}
    for i in range(number_of_clusters):
        for elem in indexed_initial_set.keys():
            x[i,elem]=model.addVar(name="x_%s,%s" % (str(i), str(elem)), vtype = gurobipy.GRB.BINARY)

    model.update()

    for elem in indexed_initial_set.keys():
        model.addConstr(sum(x[i,elem] for i in range(number_of_clusters)) == 1)

    for i in range(number_of_clusters):
        model.addConstr(sum(x[i,elem] for elem in indexed_initial_set.keys()) >= 1)
    
    model.setObjective(sum( (sum(x[i,elem] * indexed_initial_set[elem].frequency for elem in indexed_initial_set.keys()) - ideal_cluster_frequency)*(sum(x[i,elem] * indexed_initial_set[elem].frequency for elem in indexed_initial_set.keys()) - ideal_cluster_frequency) for i in range(number_of_clusters)))
    model.modelSense = gurobipy.GRB.MINIMIZE
    model.optimize()
    print('\n Objective value: %g\n' % model.ObjVal)
    print('\n Variable values: \n')
    solution = []
    for i in range(number_of_clusters):
        print("The following Super Variants are clustered. \n")
        cluster = dict()
        accumulated_frequency_cluster = 0
        for elem in indexed_initial_set.keys():
            print(str(elem) + ": " + str(x[i,elem].X))
            if(x[i,elem].X == 1.0):
                cluster[elem] = indexed_initial_set[elem]
                accumulated_frequency_cluster += indexed_initial_set[elem].frequency
        solution.append(cluster)
        print("With accumulated frequency: " + str(accumulated_frequency_cluster))
        print("-----------------------------")

    return model, solution

    
                