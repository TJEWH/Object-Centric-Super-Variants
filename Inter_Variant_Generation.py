import Inter_Variant_Summarization as IVS
import Super_Variant_Visualization as SVV
from enum import Enum
import copy 
import math

class Distribution(Enum):
    UNIFORM = 1
    NORMAL = 2
    EXPLORATION = 3


def generate_super_variant_hierarchy(initial_super_variant_set, number_of_super_variants, max_number_of_levels = math.inf, frequency_distribution_type = Distribution.EXPLORATION, base = 2, print_results = False):
    return generate_super_variant_hierarchy_by_classification([initial_super_variant_set], number_of_super_variants, max_number_of_levels, frequency_distribution_type, base, print_results)


def generate_super_variant_hierarchy_by_classification(initial_super_variant_classification, number_of_super_variants_per_class = 1, max_number_of_levels = math.inf, frequency_distribution_type = Distribution.EXPLORATION, base = 2, print_results = False):
    result = []
    final_level_super_variants = []
    for super_variant_set in initial_super_variant_classification:
        if(frequency_distribution_type == Distribution.UNIFORM or frequency_distribution_type == Distribution.NORMAL):
            if(frequency_distribution_type == Distribution.UNIFORM):
                class_result, class_final_level_super_variants = generate_super_variant_hierarchy_uniform(super_variant_set, number_of_super_variants_per_class, max_number_of_levels, print_results)
            else:
                class_result, class_final_level_super_variants = generate_super_variant_hierarchy_normal(super_variant_set, number_of_super_variants_per_class, max_number_of_levels, print_results)

            final_level_super_variants.extend(class_final_level_super_variants)

        elif(frequency_distribution_type == Distribution.EXPLORATION):
            class_result = generate_super_variant_hierarchy_exploration(super_variant_set, max_number_of_levels, base, print_results)
            final_level_super_variants.extend((max(class_result.items(), key=lambda x:x[0]))[1][0])

        result.append(class_result)

    for super_variant in final_level_super_variants:
        SVV.visualize_super_variant(super_variant)
    return result, final_level_super_variants


def generate_super_variant_hierarchy_uniform(initial_super_variant_set, number_of_super_variants, max_number_of_levels = math.inf, print_results = False):
    return generate_super_variant_hierarchy_by_frequency(initial_super_variant_set, number_of_super_variants, max_number_of_levels, Distribution.UNIFORM, print_results)

def generate_super_variant_hierarchy_normal(initial_super_variant_set, number_of_super_variants, max_number_of_levels = math.inf, print_results = False):
    return generate_super_variant_hierarchy_by_frequency(initial_super_variant_set, number_of_super_variants, max_number_of_levels, Distribution.NORMAL, print_results)

def generate_super_variant_hierarchy_exploration(initial_super_variant_set, max_number_of_levels, base = 2, print_results = False):
    return generate_super_variant_hierarchy_by_cost(initial_super_variant_set, max_number_of_levels, 1, base, print_results)


def generate_super_variant_hierarchy_by_frequency(initial_super_variant_set, number_of_super_variants, max_number_of_levels, distribution_type, print_results = False):
    if(len(initial_super_variant_set) <= number_of_super_variants):
        result = dict()
        result[1] = initial_super_variant_set
        return result
        
    else:
        indexed_initial_set = dict()
        for super_variant in initial_super_variant_set:
            indexed_initial_set[super_variant.id] = super_variant

        model, clusters = cluster_by_frequency(indexed_initial_set, number_of_super_variants, distribution_type, print_results)

        size_largest_cluster = max([len(cluster) for cluster in clusters])
        for i in range(2, max(3, size_largest_cluster)):
            if(math.ceil(math.log(size_largest_cluster, i)) <= max_number_of_levels):
                base = i
                break

        result = []
        final_level_super_variants = []
        for cluster in clusters:
            cluster_result = generate_super_variant_hierarchy_by_cost(list(cluster.values()), max_number_of_levels, 1, base, print_results)
            final_level_super_variants.append((max(cluster_result.items(), key=lambda x:x[0]))[1][0][0])
            if(print_results):
                print("The following levels have been generated.")
                for level in cluster_result.keys():
                    print(level)
                    for super_variant in cluster_result[level][0]:
                        print(super_variant.id)
                    print("-----------")
            result.append(cluster_result)

        return result, final_level_super_variants
    

def generate_super_variant_hierarchy_by_cost(initial_super_variant_set, max_number_of_level, counter, base, print_results = False):

    if(len(initial_super_variant_set) == 1):
        result = dict()
        result[counter] = (initial_super_variant_set, 0)
        return result
        
    else:
        indexed_initial_set = dict()
        for super_variant in initial_super_variant_set:
            indexed_initial_set[super_variant.id] = super_variant


        distances = dict()
        for i in indexed_initial_set.keys():
            for j in indexed_initial_set.keys():
                if(j>i):
                    mapping, cost = IVS.decide_matching(indexed_initial_set[i], indexed_initial_set[j], copy.deepcopy(indexed_initial_set[i].lanes), copy.deepcopy(indexed_initial_set[j].lanes), True, False)
                    distances[i,j] = cost
                else:
                    distances[i,j] = 0

        model, clusters = cluster_by_size(indexed_initial_set, base, distances, print_results)

        level_result = []
        accumulated_cost = 0
        for cluster in clusters:
            if(print_results):
                print("Summarizing Super Variants with IDs: ")
                for id in cluster:
                    print(id)
            super_variant1 = indexed_initial_set[cluster[0]]
            for i in range(1, len(cluster)):
                super_variant2 = indexed_initial_set[cluster[i]]
                super_variant, cost = IVS.join_super_variants(super_variant1, super_variant2 ,False)
                accumulated_cost += cost
                super_variant1 = copy.deepcopy(super_variant)
            level_result.append(super_variant1)

        if(max_number_of_level == 1 or len(level_result) == 1):
            result = dict()
        else:
            result = generate_super_variant_hierarchy_by_cost(level_result, max_number_of_level-1, counter+1, base, print_results)

        result[counter] = (level_result, accumulated_cost)
        return result


def cluster_by_frequency(indexed_initial_set, number_of_clusters, distribution_type, print_results = False):

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

    if(print_results):
        print('\n Objective value: %g\n' % model.ObjVal)
        print('\n Variable values: \n')
    clusters = []
    for i in range(number_of_clusters):
        if(print_results):
            print("The following Super Variants are clustered. \n")
        cluster = dict()
        accumulated_frequency_cluster = 0
        for elem in indexed_initial_set.keys():
            if(print_results):
                print(str(elem) + ": " + str(x[i,elem].X))
            if(x[i,elem].X == 1.0):
                cluster[elem] = indexed_initial_set[elem]
                accumulated_frequency_cluster += indexed_initial_set[elem].frequency
        clusters.append(cluster)
        if(print_results):
            print("With accumulated frequency: " + str(accumulated_frequency_cluster))
            print("The ideal accumulated frequency would be: " + str(ideal_cluster_frequency[i]))
            print("-----------------------------")

    return model, clusters


def cluster_by_size(indexed_initial_set, cluster_size, distances, print_results = False):

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

    if(print_results):
        print('\n Objective value: %g\n' % model.ObjVal)
        print('\n Variable values: \n')
    clusters = []
    for i in range(number_of_clusters):
        if(print_results):
            print("The following Super Variants are clustered. \n")
        cluster = []
        accumulated_distances = 0
        for elem in indexed_initial_set.keys():
            if(print_results):
                print(str(elem) + ": " + str(x[i,elem].X))
            if(x[i,elem].X == 1.0):
                cluster.append(elem)
                for elem2 in indexed_initial_set.keys():
                    if(x[i,elem2].X == 1.0):
                        accumulated_distances += distances[elem, elem2]

        clusters.append(cluster)
        if(print_results):
            print("With average distance/cost: " + str(accumulated_distances/cluster_size))
            print("-----------------------------")

    return model, clusters


def classify_initial_super_variants_by_activity(initial_super_variant_set, activity_label, object_types = set()): 

    if(object_types == set()):
        for super_variant in initial_super_variant_set:
            object_types = object_types.union(super_variant.object_types)

    result = [[],[]]

    for super_variant in initial_super_variant_set:
        activity_containted = False
        for lane in super_variant.lanes:
            if(lane.object_type in object_types):
                if(lane.contains_activity(activity_label)):
                    activity_containted = True
                    break

        if activity_containted:
            result[0].append(super_variant)
        else: 
            result[1].append(super_variant)

    return result

def classify_initial_super_variants_by_object_cardinality(initial_super_variant_set, object_type):

    result = dict()

    for super_variant in initial_super_variant_set:
        cardinality = 0
        for lane in super_variant.lanes:
            if(lane.object_type == object_type):
                cardinality += 1

        if cardinality in result.keys():
            result[cardinality].append(super_variant)

        else: result[cardinality] = [super_variant]

    return list(result.values())

def classify_initial_super_variants_by_expression(initial_super_variant_set, boolean_expression):
    result = [[],[]]
    for super_variant in initial_super_variant_set:

        if boolean_expression(super_variant):
            result[0].append(super_variant)
        else: 
            result[1].append(super_variant)

    return result


def containes_3_payment_reminder(super_variant):
    count = 0
    for lane in super_variant.lanes:
        count += lane.count_activity("Payment Reminder")

    return count >= 3
