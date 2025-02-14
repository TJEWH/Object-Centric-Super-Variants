import Inter_Variant_Generation as IEVG
import Super_Variant_Definition as SVD
import Super_Variant_Hierarchy as SVH


def build_triad_hierarchy(initial_super_variants):
    # Generating 3 hierarchies from the initial super variants with uniform frequency distribution
    hierarchies, final_super_variants = IEVG.generate_super_variant_hierarchy(
        initial_super_variants, base=4)

    # Visualizing each hierarchy bottom-up
    for hierarchy in hierarchies:
        SVH.explore_hierarchy_bottom_up(hierarchy)

    print_hierarchy_costs(hierarchies)


def print_hierarchy_costs(hierarchies):
    # Printing the accumulated summarization costs
    for i, h_list in enumerate(hierarchies):
        accumulated_cost = 0

        for hierarchy in h_list:
            for level in hierarchy.keys():
                accumulated_cost += hierarchy[level][1]

        print("Cost for hierarchy " + str(i) + ": " + str(accumulated_cost))


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