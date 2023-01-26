import Inter_Variant_Summarization as IVS
import Super_Variant_Visualization as SVV
import copy 
import math
import enum

class Distribution(enum.Enum):
    UNIFORM = 1
    NORMAL = 2

def generate_super_variant_hierarchy_logarithmic(initial_super_variant_set, max_number_of_level, base = 2):
    return generate_super_variant_hierarchy(initial_super_variant_set, max_number_of_level, 1, base)
    
def generate_super_variant_hierarchy(initial_super_variant_set, max_number_of_level, counter, base):
    if(len(initial_super_variant_set) == 1):
        result = dict()
        result[counter] = (initial_super_variant_set, 0)
        return result
        
    else:
        indexed_initial_set = dict()
        for i, super_variant in enumerate(initial_super_variant_set):
            indexed_initial_set[i] = super_variant


        distances = dict()
        for i in indexed_initial_set.keys():
            for j in indexed_initial_set.keys():
                if(j>i):
                    mapping, cost = IVS.decide_matching(indexed_initial_set[i], indexed_initial_set[j], copy.deepcopy(indexed_initial_set[i].lanes), copy.deepcopy(indexed_initial_set[j].lanes), True, False)
                    distances[i,j] = cost
                else:
                    distances[i,j] = 0

        model, clusters = cluster_by_size(indexed_initial_set, base, distances)

        level_result = []
        accumulated_cost = 0
        for cluster in clusters:
            super_variant1 = indexed_initial_set[cluster[0]]
            for i in range(1, len(cluster)):
                super_variant2 = indexed_initial_set[cluster[i]]
                super_variant, cost = IVS.join_super_variants(super_variant1, super_variant2 ,False, False, False)
                accumulated_cost += cost
                super_variant1 = copy.deepcopy(super_variant)
            level_result.append(super_variant1)

        
        for super_variant in level_result:
            SVV.visualize_super_variant(super_variant)

        if(max_number_of_level == 1 or len(level_result) == 1):
            result = dict()
        else:
            result = generate_super_variant_hierarchy(level_result, max_number_of_level-1, counter+1, base)

        result[counter] = (level_result, accumulated_cost)
        return result



def generate_super_variant_hierarchy_uniform(initial_super_variant_set, number_of_super_variants, max_number_of_levels = math.inf, print_results = False):
    return generate_super_variant_hierarchy_by_frequency(initial_super_variant_set, number_of_super_variants, max_number_of_levels, print_results, Distribution.UNIFORM)


def generate_super_variant_hierarchy_normal(initial_super_variant_set, number_of_super_variants, max_number_of_levels = math.inf, print_results = False):
    return generate_super_variant_hierarchy_by_frequency(initial_super_variant_set, number_of_super_variants, max_number_of_levels, print_results, Distribution.NORMAL)


def generate_super_variant_hierarchy_by_frequency(initial_super_variant_set, number_of_super_variants, max_number_of_levels, print_results, distribution_type):
    if(len(initial_super_variant_set) <= number_of_super_variants):
        result = dict()
        result[1] = initial_super_variant_set
        return result
        
    else:
        indexed_initial_set = dict()
        for i, super_variant in enumerate(initial_super_variant_set):
            indexed_initial_set[i] = super_variant

        model, clusters = cluster_by_frequency(indexed_initial_set, number_of_super_variants, distribution_type)

        size_largest_cluster = max([len(cluster) for cluster in clusters])
        for i in range(2, max(3, size_largest_cluster)):
            if(math.ceil(math.log(size_largest_cluster, i)) <= max_number_of_levels):
                base = i
                break

        intermediate_results = []
        for cluster in clusters:
            cluster_result = generate_super_variant_hierarchy(list(cluster.values()), max_number_of_levels, 1, base)
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

        if(print_results):
            print("The following levels have been generated.")
            for level in result.keys():
                print(level)
                for sv in result[level][0]:
                    print(sv.id)
                print("-----------")

        return result
    

def cluster_by_frequency(indexed_initial_set, number_of_clusters, distribution_type):

    accumulated_frequency = sum([indexed_initial_set[index].frequency for index in indexed_initial_set.keys()])

    if (distribution_type == Distribution.UNIFORM):
        ideal_cluster_frequency = [accumulated_frequency/number_of_clusters]*number_of_clusters
    elif(distribution_type == Distribution.NORMAL):
        import scipy.stats as st
        stepsize = 3/number_of_clusters
        ideal_cluster_frequency = []
        for i in range(number_of_clusters):
            ideal_cluster_frequency.append((((st.norm.cdf(i+1*stepsize)- 0.5)*2) - ((st.norm.cdf(i*stepsize)- 0.5)*2))*accumulated_frequency)
        print(ideal_cluster_frequency)

    import gurobipy
    model = gurobipy.Model("ClusteringByFrequency")
    x = {}
    for i in range(number_of_clusters):
        for elem in indexed_initial_set.keys():
            x[i,elem]=model.addVar(name="x_%s,%s" % (str(i), str(elem)), vtype = gurobipy.GRB.BINARY)

    model.update()

    for elem in indexed_initial_set.keys():
        model.addConstr(sum(x[i,elem] for i in range(number_of_clusters)) == 1)

    for i in range(number_of_clusters):
        model.addConstr(sum(x[i,elem] for elem in indexed_initial_set.keys()) >= 1)
    
    model.setObjective(sum( (sum(x[i,elem] * indexed_initial_set[elem].frequency for elem in indexed_initial_set.keys()) - ideal_cluster_frequency[i])*(sum(x[i,elem] * indexed_initial_set[elem].frequency for elem in indexed_initial_set.keys()) - ideal_cluster_frequency[i]) for i in range(number_of_clusters)))
    model.modelSense = gurobipy.GRB.MINIMIZE
    model.optimize()

    print('\n Objective value: %g\n' % model.ObjVal)
    print('\n Variable values: \n')
    clusters = []
    for i in range(number_of_clusters):
        print("The following Super Variants are clustered. \n")
        cluster = dict()
        accumulated_frequency_cluster = 0
        for elem in indexed_initial_set.keys():
            print(str(elem) + ": " + str(x[i,elem].X))
            if(x[i,elem].X == 1.0):
                cluster[elem] = indexed_initial_set[elem]
                accumulated_frequency_cluster += indexed_initial_set[elem].frequency
        clusters.append(cluster)
        print("With accumulated frequency: " + str(accumulated_frequency_cluster))
        print("-----------------------------")

    return model, clusters


def cluster_by_size(indexed_initial_set, cluster_size, distances):

    number_of_clusters = math.ceil(len(indexed_initial_set)/cluster_size)

    import gurobipy
    model = gurobipy.Model("ClusteringBySize")

    x = {}
    for i in range(number_of_clusters):
        for elem in indexed_initial_set.keys():
            x[i,elem]=model.addVar(name="x_%s,%s" % (str(i), str(elem)), vtype = gurobipy.GRB.BINARY)

    model.update()

    for elem in indexed_initial_set.keys():
        model.addConstr(sum(x[i,elem] for i in range(number_of_clusters)) == 1)

    for i in range(number_of_clusters):
        model.addConstr(sum(x[i,elem] for elem in indexed_initial_set.keys()) >= 1)
    
    model.setObjective(sum( (sum(sum(x[i,elem1]*x[i,elem2]*distances[elem1,elem2] for elem2 in indexed_initial_set.keys()) for elem1 in indexed_initial_set.keys()) / cluster_size) for i in range(number_of_clusters)))
    model.modelSense = gurobipy.GRB.MINIMIZE
    model.optimize()

    print('\n Objective value: %g\n' % model.ObjVal)
    print('\n Variable values: \n')
    clusters = []
    for i in range(number_of_clusters):
        print("The following Super Variants are clustered. \n")
        cluster = []
        accumulated_distances = 0
        for elem in indexed_initial_set.keys():
            print(str(elem) + ": " + str(x[i,elem].X))
            if(x[i,elem].X == 1.0):
                cluster.append(elem)
                for elem2 in indexed_initial_set.keys():
                    if(x[i,elem2].X == 1.0):
                        accumulated_distances += distances[elem, elem2]

        clusters.append(cluster)
        print("With average distance/cost: " + str(accumulated_distances/cluster_size))
        print("-----------------------------")

    return model, clusters

    
                