import copy
import logging
import math
import time
from enum import Enum

import Inter_Variant_Summarization as IEVS


class Distribution(Enum):
    UNIFORM = 1
    NORMAL = 2
    EXPLORATION = 3


NESTED_STRUCTURES = False


def generate_super_variant_hierarchy(initial_super_variant_set, number_of_super_variants=1,
                                     max_number_of_levels=math.inf,
                                     frequency_distribution_type=Distribution.EXPLORATION, base=2):
    """
    Generates a Super Variant hierarchy for a set of Super Variants.

    Parameters:
        initial_super_variant_set (list): The list of sets of Super Variants
        number_of_super_variants (int): The number of desired clusters and final Super Variants per set of Super Variants
        max_number_of_levels (int): The maximal level reached in the generation of Super Variants
        frequency_distribution_type (Distribution): The distribution type used to cluster the Super Variants
        base (int): The logarithmic base, determines how many variants are to be summarized in a single generative step of an exploratory setting

    Returns:
        dict, list: The set of Super Variants for each level and the levels accumulated cost and a list of the final Super Variants
    """
    return generate_super_variant_hierarchy_by_classification(
        [initial_super_variant_set],
        number_of_super_variants,
        max_number_of_levels,
        frequency_distribution_type,
        base)


def generate_super_variant_hierarchy_by_classification(initial_super_variant_classification,
                                                       number_of_super_variants_per_class=1,
                                                       max_number_of_levels=math.inf,
                                                       frequency_distribution_type=Distribution.EXPLORATION,
                                                       base=2):
    """
    Generates a Super Variant hierarchy for each set of Super Variants based on an initial classification.

    Parameters:
        initial_super_variant_classification (list): The list of sets of Super Variants
        number_of_super_variants_per_class (int): The number of desired clusters and final Super Variants per set of Super Variants
        max_number_of_levels (int): The maximal level reached in the generation of Super Variants
        frequency_distribution_type (Distribution): The distribution type used to cluster the Super Variants
        base (int): The logarithmic base, determines how many variants are to be summarized in a single generative step of an exploratory setting

    Returns:
        dict, list: The set of Super Variants for each level and the levels accumulated cost and a list of the final Super Variants
    """
    result = []
    final_level_super_variants = []

    maximal_clusters = len(initial_super_variant_classification[0])
    if number_of_super_variants_per_class >= maximal_clusters:
        number_of_super_variants_per_class = maximal_clusters
        logging.info(f"Number of super variants per class is set to {maximal_clusters} "
                     f"as it was higher than the number of classes.")

    if frequency_distribution_type == Distribution.UNIFORM or frequency_distribution_type == Distribution.NORMAL:
        for super_variant_set in initial_super_variant_classification:
            class_result, class_final_level_super_variants = generate_super_variant_hierarchy_by_frequency(
                initial_super_variant_set=super_variant_set,
                number_of_super_variants=number_of_super_variants_per_class,
                distribution_type=frequency_distribution_type,
                max_number_of_levels=max_number_of_levels
            )
            final_level_super_variants.append(class_final_level_super_variants)
            result.append(class_result)

    # Generates an exploratory Super Variant hierarchy given a logarithmic base and a maximal number of levels.
    elif frequency_distribution_type == Distribution.EXPLORATION:
        for super_variant_set in initial_super_variant_classification:
            class_result = generate_super_variant_hierarchy_by_cost(
                initial_super_variant_set=[(super_variant, None, None) for super_variant in super_variant_set],
                max_number_of_level=max_number_of_levels,
                counter=0,
                base=base
            )

            final_level_super_variants.append((max(class_result.items(), key=lambda x: x[0]))[1][0])
            result.append(class_result)

    return result, final_level_super_variants


def generate_super_variant_hierarchy_by_frequency(initial_super_variant_set, number_of_super_variants,
                                                  max_number_of_levels, distribution_type):
    """
    Creates a grouping of the initial set of Super Variants in accordance with a frequency distribution and then
    generates a Super Variant hierarchy.

    Parameters:
        initial_super_variant_set (list): The set of Super Variants
        number_of_super_variants (int): The number of desired clusters and final Super Variants
        max_number_of_levels (int): The maximal level reached in the generation of Super Variants
        distribution_type (Distribution): The distribution type used to cluster the Super Variants

    Returns:
        dict: The set of Super Variants for each level and the levels accumulated cost
        list: A list of the final Super Variants
    """
    if len(initial_super_variant_set) <= number_of_super_variants:
        result = dict()
        result[0] = [(super_variant, None, None) for super_variant in initial_super_variant_set]
        return result

    else:
        indexed_initial_set = dict()
        for super_variant in initial_super_variant_set:
            indexed_initial_set[super_variant.id] = super_variant

        clusters = _cluster_by_frequency(
            indexed_initial_set=indexed_initial_set,
            number_of_clusters=number_of_super_variants,
            distribution_type=distribution_type
        )

        size_largest_cluster = max([len(cluster) for cluster in clusters])
        for i in range(2, max(3, size_largest_cluster)):
            if math.ceil(math.log(size_largest_cluster, i)) <= max_number_of_levels:
                base = i
                break

        result = []
        final_level_super_variants = []

        for cluster in clusters:
            cluster_result = generate_super_variant_hierarchy_by_cost(
                initial_super_variant_set=[(super_variant, None, None) for super_variant in cluster.values()],
                max_number_of_level=max_number_of_levels,
                counter=0,
                base=base,
            )

            final_level_super_variants.extend((max(cluster_result.items(), key=lambda x: x[0]))[1][0])

            logging.debug("The following levels have been generated.")
            for level in cluster_result.keys():
                logging.debug(level)
                [logging.debug(super_variant[0].id) for super_variant in cluster_result[level][0]]
                logging.debug("-" * 36)
            result.append(cluster_result)

        return result, final_level_super_variants


def generate_super_variant_hierarchy_by_cost(initial_super_variant_set, max_number_of_level, counter, base,
                                             measure_times=False, times=None):
    """
    Recursively generates Super Variants based on an initial set-up to a desired depth using the minimum cost possible.

    Parameters:
        initial_super_variant_set (list): The set of Super Variants
        max_number_of_level (int): The maximal level reached in the generation of Super Variants
        counter (int): The current generation level
        base (int): The logarithmic base, determines how many variants are to be summarized in a single generative step
        measure_times (bool): Whether the computation times should be measured
        times (dict): The times of the other levels

    Returns:
        dict: The set of Super Variants for each level and the levels accumulated cost
    """
    if len(initial_super_variant_set) == 1:
        result = dict()
        result[counter] = (initial_super_variant_set, 0)
        return result

    else:
        if measure_times:
            time_start = time.perf_counter()
            number_offers = 0

        indexed_initial_set = dict()
        for super_variant in initial_super_variant_set:
            indexed_initial_set[super_variant[0].id] = super_variant

            if measure_times:
                number_offers += len(super_variant[0].get_lanes_of_type('offer'))

        if measure_times:
            time_before_mapping = time.perf_counter()

        distances = dict()
        for i in indexed_initial_set.keys():
            for j in indexed_initial_set.keys():
                if j > i:
                    mapping, cost = IEVS.decide_matching(
                        indexed_initial_set[i][0],
                        indexed_initial_set[j][0],
                        copy.deepcopy(indexed_initial_set[i][0].lanes),
                        copy.deepcopy(indexed_initial_set[j][0].lanes),
                        True)

                    distances[i, j] = cost
                else:
                    distances[i, j] = 0

        if measure_times:
            time_after_mapping = time.perf_counter()

        clusters = _cluster_by_size(indexed_initial_set, max(base, 2), distances)  # on main only base
        if measure_times:
            time_after_clustering = time.perf_counter()
            number_summarizations = 0

        level_result = []
        accumulated_cost = 0
        for cluster in clusters:
            logging.debug("Summarizing Super Variants with IDs: ")
            [logging.debug(_id) for _id in cluster]

            super_variant1 = indexed_initial_set[cluster[0]]
            for i in range(1, len(cluster)):
                super_variant2 = indexed_initial_set[cluster[i]]
                super_variant, cost = IEVS.join_super_variants(
                    super_variant1[0],
                    super_variant2[0],
                    NESTED_STRUCTURES
                )
                if measure_times:
                    number_summarizations += 1
                accumulated_cost += cost
                super_variant1 = (
                    copy.deepcopy(super_variant),
                    copy.deepcopy(super_variant1),
                    copy.deepcopy(super_variant2))

            level_result.append(super_variant1)

        if measure_times:
            time_after_summarization = time.perf_counter()

            if max_number_of_level == 1 or len(level_result) == 1:
                result = dict()
            else:
                result, times = generate_super_variant_hierarchy_by_cost(
                    level_result,
                    max_number_of_level - 1,
                    counter + 2 if counter == 0 else counter + 1,
                    base,
                    measure_times,
                    times)

            if counter == 0:
                result[1] = (level_result, accumulated_cost)
                result[0] = (initial_super_variant_set, 0)
                times[1] = [
                    time_after_summarization - time_start,
                    time_after_mapping - time_before_mapping,
                    time_after_clustering - time_after_mapping,
                    time_after_summarization - time_after_clustering,
                    number_summarizations,
                    number_offers / len(initial_super_variant_set)]
            else:
                result[counter] = (level_result, accumulated_cost)
                times[counter] = [
                    time_after_summarization - time_start,
                    time_after_mapping - time_before_mapping,
                    time_after_clustering - time_after_mapping,
                    time_after_summarization - time_after_clustering,
                    len(initial_super_variant_set),
                    number_summarizations,
                    number_offers / len(initial_super_variant_set)]

            return result, times

        else:
            # on main only else part
            if max_number_of_level == 1 or len(level_result) == 1:
                result = dict()
            else:
                result = generate_super_variant_hierarchy_by_cost(
                    level_result,
                    max_number_of_level - 1,
                    counter + 2 if counter == 0 else counter + 1,
                    base)

            if counter == 0:
                result[1] = (level_result, accumulated_cost)
                result[0] = (initial_super_variant_set, 0)
            else:
                result[counter] = (level_result, accumulated_cost)
            return result


def _cluster_by_frequency(indexed_initial_set, number_of_clusters, distribution_type):
    """
    Clusters a set of Super Variants into a number of clusters based on the provided distances.

    Parameters:
        indexed_initial_set (dict): The set of Super Variants with indices as keys
        number_of_clusters (int): The number of desired clusters
        distribution_type (Distribution): The distribution type used to cluster the Super Variants

    Returns:
        list: A list containing a list for every cluster
    """
    accumulated_frequency = sum([indexed_initial_set[index].frequency for index in indexed_initial_set.keys()])

    if distribution_type == Distribution.UNIFORM:
        ideal_cluster_frequency = [accumulated_frequency / number_of_clusters] * number_of_clusters
    elif distribution_type == Distribution.NORMAL:
        import scipy.stats as st
        step_size = 3 / number_of_clusters
        ideal_cluster_frequency = []
        for i in range(number_of_clusters):
            ideal_cluster_frequency.append((((st.norm.cdf(i + 1 * step_size) - 0.5) * 2) - (
                    (st.norm.cdf(i * step_size) - 0.5) * 2)) * accumulated_frequency)

    import gurobipy
    gurobipy.setParam('OutputFlag', 0)
    model = gurobipy.Model("ClusteringByFrequency")
    x = {}
    for i in range(number_of_clusters):
        for elem in indexed_initial_set.keys():
            x[i, elem] = model.addVar(name="x_%s,%s" % (str(i), str(elem)), vtype=gurobipy.GRB.BINARY)

    model.update()

    for elem in indexed_initial_set.keys():
        model.addConstr(sum(x[i, elem] for i in range(number_of_clusters)) == 1)

    for i in range(number_of_clusters):
        model.addConstr(sum(x[i, elem] for elem in indexed_initial_set.keys()) >= 1)

    model.setObjective(sum(
        (sum(x[i, elem] * indexed_initial_set[elem].frequency
             for elem in indexed_initial_set.keys()) - ideal_cluster_frequency[i]) *
        (sum(x[i, elem] * indexed_initial_set[elem].frequency
             for elem in indexed_initial_set.keys()) - ideal_cluster_frequency[i]) for i in range(number_of_clusters)))

    model.modelSense = gurobipy.GRB.MINIMIZE
    model.optimize()

    logging.debug('\n Objective value: %g\n' % model.ObjVal)
    logging.debug('\n Variable values: \n')

    clusters = []
    for i in range(number_of_clusters):
        logging.debug("The following Super Variants are clustered. \n")

        cluster = dict()
        accumulated_frequency_cluster = 0
        for elem in indexed_initial_set.keys():
            logging.debug(str(elem) + ": " + str(x[i, elem].X))
            if x[i, elem].X == 1.0:
                cluster[elem] = indexed_initial_set[elem]
                accumulated_frequency_cluster += indexed_initial_set[elem].frequency

        clusters.append(cluster)

        logging.debug("With accumulated frequency: " + str(accumulated_frequency_cluster))
        logging.debug("The ideal accumulated frequency would be: " + str(ideal_cluster_frequency[i]))
        logging.debug("-" * 36)

    return clusters


def _cluster_by_size(indexed_initial_set, cluster_size, distances):
    """
    Clusters a set of Super Variants into a number of clusters based on the provided distances.

    Parameters:
        indexed_initial_set (dict): The set of Super Variants with indices as keys
        cluster_size (int): The number of Super Variants per cluster
        distances (dict): The distance for each pair of Super Variants

    Returns:
        list: A list containing a list for every cluster
    """
    number_of_clusters = math.ceil(len(indexed_initial_set) / cluster_size)

    import gurobipy
    gurobipy.setParam('OutputFlag', 0)
    model = gurobipy.Model("ClusteringBySize")

    x = {}
    for i in range(number_of_clusters):
        for elem in indexed_initial_set.keys():
            x[i, elem] = model.addVar(name="x_%s,%s" % (str(i), str(elem)), vtype=gurobipy.GRB.BINARY)

    model.update()

    for elem in indexed_initial_set.keys():
        model.addConstr(sum(x[i, elem] for i in range(number_of_clusters)) == 1)

    for i in range(number_of_clusters):
        model.addConstr(sum(x[i, elem] for elem in indexed_initial_set.keys()) >= 1)

    for i in range(number_of_clusters):
        model.addConstr(sum(x[i, elem] for elem in indexed_initial_set.keys()) <= cluster_size)

    model.setObjective(sum((sum(
        sum(x[i, elem1] * x[i, elem2] * distances[elem1, elem2] for elem2 in indexed_initial_set.keys()) for elem1 in
        indexed_initial_set.keys()) / cluster_size) for i in range(number_of_clusters)))
    model.modelSense = gurobipy.GRB.MINIMIZE
    model.optimize()

    logging.debug('\n Objective value: %g\n' % model.ObjVal)
    logging.debug('\n Variable values: \n')

    clusters = []
    for i in range(number_of_clusters):
        logging.debug("The following Super Variants are clustered. \n")

        cluster = []
        accumulated_distances = 0
        for elem in indexed_initial_set.keys():
            logging.debug(str(elem) + ": " + str(x[i, elem].X))

            if x[i, elem].X == 1.0:
                cluster.append(elem)
                for elem2 in indexed_initial_set.keys():
                    if x[i, elem2].X == 1.0:
                        accumulated_distances += distances[elem, elem2]

        clusters.append(cluster)

        logging.info("With average distance/cost: " + str(accumulated_distances / cluster_size))
        logging.debug("-" * 36)

    return clusters


def classify_initial_super_variants_by_activity(initial_super_variant_set, activity_label, object_types=None):
    """
    Given an activity_label, this method classifies a set of Super Variants into classes depending on whether that
    activity label is performed in the specified object instances.

    Parameters:
        initial_super_variant_set (list): The set of Super Variants
        activity_label (str): The name of the activity
        object_types (set): The names of the considered object types

    Returns:
        list: A list containing a list with all Super Variants classes
    """
    if object_types is None:
        object_types = set()
        for super_variant in initial_super_variant_set:
            object_types = object_types.union(super_variant.object_types)

    result = [[], []]

    for super_variant in initial_super_variant_set:
        activity_contained = False
        for lane in super_variant.lanes:
            if lane.object_type in object_types:
                if lane.contains_activity(activity_label):
                    activity_contained = True
                    break

        if activity_contained:
            result[0].append(super_variant)
        else:
            result[1].append(super_variant)

    return result
