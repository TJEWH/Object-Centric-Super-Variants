import logging

from ocpa.visualization.log.variants import factory as variants_visualization_factory

import Inter_Variant_Generation as IEVG
import Super_Variant_Definition as SVD
import Super_Variant_Hierarchy as SVH
import Super_Variant_Visualization as SVV
import Input_Extraction_Definition as IED


def build_triad_hierarchy(initial_super_variants):
    # Generating 3 hierarchies from the initial super variants with uniform frequency distribution
    hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(
        initial_super_variants, base=4)

    # Visualizing each hierarchy bottom-up
    for hierarchy in hierarchies:
        SVH.explore_hierarchy_bottom_up(hierarchy)

    # print_hierarchy_costs(hierarchies)


def print_hierarchy_costs(hierarchies):
    # Printing the accumulated summarization costs
    for i, h_list in enumerate(hierarchies):
        accumulated_cost = 0

        for hierarchy in h_list:
            for level in hierarchy.keys():
                accumulated_cost += hierarchy[level][1]

        logging.info("Cost for hierarchy " + str(i) + ": " + str(accumulated_cost))


def print_hierarchy_costs_alt(hierarchies):
    # Printing the accumulated summarization costs
    for h_list in hierarchies.values()[0]:

        for hierarchy in h_list.values():
            logging.info("Cost for hierarchy " + str(hierarchy[0][0][0].id) + ": " + str(hierarchy[1]))


def manual_alignment(super_variant, positions, interactions):
    """Only used in publication"""
    for i in range(len(super_variant.lanes)):
        super_variant.lanes[i] = manual_alignment_l(super_variant.lanes[i], positions[i])

    for k in range(len(super_variant.interaction_points)):
        super_variant.interaction_points[k].index_in_lanes = interactions[k][0]
        for t in range(len(super_variant.interaction_points[k].exact_positions)):
            super_variant.interaction_points[k].exact_positions[t].set_base_index(interactions[k][t])
    return super_variant


def manual_alignment_l(lane, positions):
    """Only used in publication"""
    for j in range(len(lane.elements)):
        if type(lane.elements[j]) is SVD.CommonConstruct or type(lane.elements[j]) is SVD.InteractionConstruct:
            lane.elements[j].index = positions[j]
            lane.elements[j].position.set_base_index(positions[j])

        elif type(lane.elements[j]) is SVD.OptionalConstruct or type(lane.elements[j]) is SVD.ChoiceConstruct:
            lane.elements[j].index_start = positions[j][0]
            lane.elements[j].position_start.set_base_index(positions[j][0])
            lane.elements[j].index_end = positions[j][1]
            lane.elements[j].position_end.set_base_index(positions[j][1])

            for h in range(len(lane.elements[j].choices)):
                lane.elements[j].choices[h] = manual_alignment_l(lane.elements[j].choices[h], positions[j][2][h])

    return lane


def visualize_variant_summarization_step(ocel):
    # Visualize input variants
    variant_layout = variants_visualization_factory.apply(ocel)
    variants = []

    number_of_variants = len(ocel.variants)

    _range = range(10) if number_of_variants > 10 else range(number_of_variants)

    for idx in _range:
        extracted_variant = IED.extract_lanes(
            variant=variant_layout[ocel.variants[idx]],
            frequency=ocel.variant_frequencies[idx]
        )

        variants.append(extracted_variant)
        SVV.visualize_variant(extracted_variant, idx)


def visualize_intra_summarizations(intra_variant_summarizations, all_summarizations, use_artificial_frequencies=False):
    try:
        # Visualize selected intra-variant summarizations
        global_frequencies = [0.069, 0.05, 0.047, 0.03, 0.025, 0.019, 0.019, 0.018, 0.017, 0.016]
        for i in range(len(intra_variant_summarizations)):
            # Replace with artificial frequencies
            if use_artificial_frequencies:
                intra_variant_summarizations[i].frequency = global_frequencies[i]
            # Visualize the summarization
            SVV.visualize_super_variant(intra_variant_summarizations[i])

        # Visualize intra-variant summarizations of variant v_3
        SVV.MARK_INCORRECT_INTERACTIONS = False
        SVV.visualize_variant(all_summarizations[3][1][1][0], 3)
        SVV.visualize_variant(all_summarizations[4][1][1][0], 3)
        SVV.MARK_INCORRECT_INTERACTIONS = True

    except:
        for x in intra_variant_summarizations:
            logging.error(x)
