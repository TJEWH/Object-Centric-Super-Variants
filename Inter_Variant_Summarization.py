import Super_Variant_Definition as SVD
import Super_Variant_Visualization as WVV
import Intra_Variant_Summarization as WVS
import Input_Extraction_Definition as IED
import Inter_Lane_Summarization as ILS
def join_super_variants(summarization1, summarization2, print_result = True):
    import copy
    #WVV.visualize_super_variant(summarization1)
    #WVV.visualize_super_variant(summarization2)
    mapping, cost = decide_matching(summarization1, summarization2, copy.deepcopy(summarization1.lanes), copy.deepcopy(summarization2.lanes), True, print_result)
    if(print_result):
        print("The cost of joining these Super Variants is " + str(cost) + ".")

    intermediate_lanes = []
    intermediate_mappings = []

    for pair in mapping:
        if(pair[0] == None):
            if(print_result):
                print("Lane " + str(pair[1]) + " of the Super Variant 2 is made optional.")
            lane2 = [lane for lane in summarization2.lanes if lane.lane_id == pair[1]][0]
            super_lane, mapping = optional_super_lane(summarization2, lane2, False)
            if(print_result):
                print("The resulting Super Lane is the following: " + str(super_lane))
            intermediate_lanes.append(super_lane)
            intermediate_mappings.append((super_lane.lane_id, mapping))

        elif(pair[1] == None):
            if(print_result):
                print("Lane " + str(pair[0]) + " of the Super Variant 1 is made optional.")
            lane1 = [lane for lane in summarization1.lanes if lane.lane_id == pair[0]][0]
            super_lane, mapping = optional_super_lane(summarization1, lane1, True)
            if(print_result):
                print("The resulting Super Lane is the following: " + str(super_lane))
            intermediate_lanes.append(super_lane)
            intermediate_mappings.append((super_lane.lane_id, mapping))

        else:
            if(print_result):
                print("Lane " + str(pair[0]) + " of the Super Variant 1 and lane " + str(pair[1]) + " of Super Variant 2 are merged.")
            lane1 = [lane for lane in summarization1.lanes if lane.lane_id == pair[0]][0]
            lane2 = [lane for lane in summarization2.lanes if lane.lane_id == pair[1]][0]

            super_lane, mapping = join_super_lanes(summarization1, summarization2, lane1, lane2, print_result)
            if(print_result):
                print("The resulting Super Lane is the following: " + str(super_lane))
            intermediate_lanes.append(super_lane)
            intermediate_mappings.append((super_lane.lane_id, mapping))

    result_lanes, result_interaction_points = ILS.__re_align_lanes(intermediate_lanes, ILS.__merge_interactions(ILS.__merge_interaction_mappings(intermediate_mappings)), print_result)
    super_variant = SVD.SuperVariant(summarization1.id + summarization2.id, result_lanes, summarization1.object_types.union(summarization2.object_types), result_interaction_points, summarization1.frequency + summarization2.frequency)
    super_variant.encode_lexicographically()
    print(super_variant)
    #WVV.visualize_super_variant(super_variant)
    return super_variant, cost


def optional_super_lane(summarization, lane, first):
    
    elements = []
    object_type = lane.object_type
    lane_name = lane.object_type + " i"
    lane_id = tuple(lane.lane_id)
    cardinality = lane.cardinality
    frequency = lane.frequency

    new_interaction_points_mapping = {}
    current_horizontal_index = 0

    for elem in lane.elements:

        if(isinstance(elem, SVD.CommonConstruct) or isinstance(elem, SVD.InteractionConstruct)):
            activity = elem.activity
            frequency = elem.frequency
            if(not isinstance(elem, SVD.InteractionConstruct)):
                elements.append(SVD.CommonConstruct(activity, frequency, current_horizontal_index))
            else:
                elements.append(SVD.InteractionConstruct(activity, frequency, current_horizontal_index))

                current_interaction_point = None
                for interaction_point in summarization.interaction_points:
                    if(interaction_point.index_in_lanes == elem.position and lane.lane_id in interaction_point.interaction_lanes):
                            current_interaction_point = interaction_point
                            break

                if(first):
                    new_interaction_points_mapping[(1, current_interaction_point.index_in_lanes, str(current_interaction_point.interaction_lanes))] = (0,current_horizontal_index)
                else:
                    new_interaction_points_mapping[(2, current_interaction_point.index_in_lanes, str(current_interaction_point.interaction_lanes))] = (0,current_horizontal_index)

            current_horizontal_index += 1
                
        else:          
            new_choices = []
            length = 0

            for i in range(len(elem.choices)):
                index = current_horizontal_index
                new_choice = []
                for c_elem in elem.choices[i]:
                    c_activity = c_elem.activity
                    c_frequency = c_elem.frequency

                    if(not isinstance(c_elem, SVD.InteractionConstruct)):
                        new_choice.append(SVD.CommonConstruct(c_activity, c_frequency, index))
                    else:
                        new_choice.append(SVD.InteractionConstruct(c_activity, c_frequency, index))

                        current_interaction_point = None
                        for interaction_point in summarization.interaction_points:
                            if(interaction_point.index_in_lanes == c_elem.position and lane.lane_id in interaction_point.interaction_lanes):
                                    current_interaction_point = interaction_point
                                    break

                        if(first):
                            new_interaction_points_mapping[(1, current_interaction_point.index_in_lanes, str(current_interaction_point.interaction_lanes))] = (i,index)
                        else:
                            new_interaction_points_mapping[(2, current_interaction_point.index_in_lanes, str(current_interaction_point.interaction_lanes))] = (i,index)

                    index += 1
                
                new_choices.append(new_choice)
                length = max(length, len(new_choice))

            if(isinstance(elem, SVD.ChoiceConstruct)):
                elements.append(SVD.ChoiceConstruct(new_choices, current_horizontal_index, current_horizontal_index + length-1))
            else:
                elements.append(SVD.OptionalConstruct(new_choices, current_horizontal_index, current_horizontal_index + length-1))

            current_horizontal_index += length

    print(new_interaction_points_mapping)
    return SVD.OptionalSuperLane(lane_id, lane_name, object_type, elements, cardinality, frequency), new_interaction_points_mapping



def join_super_lanes(summarization1, summarization2, lane1, lane2, print_result = True):

    object_type = lane1.object_type
    lane_name = lane1.object_type + " i"
    lane_id = (lane1.lane_id, lane2.lane_id)
    frequency = lane1.frequency + lane2.frequency
    if(lane1.cardinality == lane2.cardinality):
        cardinality = lane1.cardinality
    else:
        cardinality = "1..n"

    elements, mappings =  ILS.__inter_lane_summarization([lane1, lane2], [summarization1.interaction_points, summarization2.interaction_points], print_result)
    return SVD.SuperLane(lane_id, lane_name, object_type, elements, cardinality, frequency), mappings


def decide_matching(summarization1, summarization2, remaining_lanes1, remaining_lanes2, propagate = True, print_result = True):
    import math

    # Base case 1: All lanes of summarization1 are matched
    if(len(remaining_lanes1) == 0):
        if(print_result):
            print("Empty. The rest is optional.")
        result = []
        cost = 0
        for lane in remaining_lanes2:
            if(print_result):
                print("Lane " + str(lane.lane_id) + " of Super Variant 2 has no matching partner and is optional.")
            result.append((None, lane.lane_id))
            cost += len(lane.elements)
        return result, cost
    
    # Base case 2: All lanes of summarization2 are matched
    elif(len(remaining_lanes2) == 0):
        if(print_result):
            print("Empty. The rest is optional.")
        result = []
        cost = 0
        for lane in remaining_lanes1:
            if(print_result):
                print("Lane " + str(lane.lane_id) + " of Super Variant 1 has no matching partner and is optional.")
            result.append((lane.lane_id, None))
            cost += len(lane.elements)
        return result, cost

    else:
        current_matching_candidate_1 = remaining_lanes1.pop()
        matching_candidates_2 = [lane for lane in remaining_lanes2 if lane.object_type == current_matching_candidate_1.object_type]

        # Fallback case: no corresponding matching
        if(len(matching_candidates_2) == 0):
            
            if(print_result):
                print("Lane " + str(current_matching_candidate_1.lane_id) + " of Super Variant 1 has no matching partner and is optional.")
            matching = [(current_matching_candidate_1.lane_id, None)]
            cost = len(current_matching_candidate_1.elements)
            new_remaining_lanes2 = remaining_lanes2
            propagation_matching, propagation_cost, new_remaining_lanes1 = propagate_optionality(summarization1, remaining_lanes1, current_matching_candidate_1, print_result)
            least_cost = propagation_cost + cost

        # Otherwise evaluate decision options
        else:
            least_cost = math.inf
            least_cost_matching = []
            least_cost_propagation_matching = []
            least_cost_new_remaining_lanes1 = []
            least_cost_new_remaining_lanes2 = []

            for candidate_2 in matching_candidates_2:
                if(print_result):
                    print("Evaluating the decision of matching lane " + str(current_matching_candidate_1.lane_id) + " of Super Variant 1 with the lane " + str(current_matching_candidate_1.lane_id) + " of Super Variant 2.")
                intermediate_matching = [(current_matching_candidate_1.lane_id, candidate_2.lane_id)]
                intermediate_cost = levenshtein_distance(current_matching_candidate_1, candidate_2)
                if(isinstance(current_matching_candidate_1, SVD.OptionalSuperLane) and not isinstance(candidate_2, SVD.OptionalSuperLane)):
                    intermediate_cost += len(candidate_2.elements)
                elif(not isinstance(current_matching_candidate_1, SVD.OptionalSuperLane) and isinstance(candidate_2, SVD.OptionalSuperLane)):
                    intermediate_cost += len(current_matching_candidate_1.elements)
                intermediate_remaining_lanes2_now = [lane for lane in remaining_lanes2 if lane.lane_id != candidate_2.lane_id]

                if(propagate):

                    if(print_result):
                        print("Propagating.")

                    # Determine lanes that require immediate propagation for both summarizations
                    interacting_lanes1 = []
                    for interaction_point in summarization1.interaction_points:
                        if (current_matching_candidate_1.lane_id in interaction_point.interaction_lanes):
                            interacting_lanes1.extend(interaction_point.interaction_lanes)
                    interacting_lanes1 = list(set(interacting_lanes1))

                    interacting_lanes2 = []
                    for interaction_point in summarization2.interaction_points:
                        if (candidate_2.lane_id in interaction_point.interaction_lanes):
                            interacting_lanes2.extend(interaction_point.interaction_lanes)
                    interacting_lanes2 = list(set(interacting_lanes2))
                    
                    propagation_lanes1 = [lane for lane in remaining_lanes1 if lane.lane_id in interacting_lanes1]
                    propagation_lanes2 = [lane for lane in intermediate_remaining_lanes2_now if lane.lane_id in interacting_lanes2]

                    # Propagate decision
                    intermediate_propagation_matching, intermediate_propagation_cost, intermediate_remaining_lanes1, intermediate_remaining_lanes2 = propagate_decision(summarization1, summarization2, remaining_lanes1, intermediate_remaining_lanes2_now, propagation_lanes1, propagation_lanes2, print_result)

                else:
                    if(print_result):
                        print("Not propagating.")
                    intermediate_propagation_matching = []
                    intermediate_propagation_cost = 0 
                    intermediate_remaining_lanes1 = remaining_lanes1
                    intermediate_remaining_lanes2 = intermediate_remaining_lanes2_now

                # Update the best evaluated choice
                if(intermediate_propagation_cost + intermediate_cost < least_cost):
                    if(print_result):
                        print("This is so far the most optimal decision.")
                    least_cost = intermediate_propagation_cost + intermediate_cost
                    least_cost_matching = intermediate_matching
                    least_cost_propagation_matching = intermediate_propagation_matching
                    least_cost_new_remaining_lanes1 = intermediate_remaining_lanes1
                    least_cost_new_remaining_lanes2 = intermediate_remaining_lanes2

            # Determine final decision
            matching = least_cost_matching
            propagation_matching = least_cost_propagation_matching
            new_remaining_lanes1 = least_cost_new_remaining_lanes1
            new_remaining_lanes2 = least_cost_new_remaining_lanes2

        if(print_result):
            print("------------------------------------")

        # Continue matching
        if(len(new_remaining_lanes1) == 0 and len(new_remaining_lanes2) == 0):
            following_matching = []
            following_cost = 0
        else:
            following_matching, following_cost = decide_matching(summarization1, summarization2, new_remaining_lanes1, new_remaining_lanes2, print_result)
        return matching + propagation_matching + following_matching, least_cost + following_cost


def propagate_decision(summarization1, summarization2, all_remaining_lanes1, all_remaining_lanes2, current_candidates_lanes1, current_candidates_lanes2, print_result):

    import copy

    if(print_result):
        print("Propagating the last decision among " + str(current_candidates_lanes1) + " and " + str(current_candidates_lanes2) +".")
    new_remaining_lanes1 = copy.deepcopy(all_remaining_lanes1)
    new_remaining_lanes2 = copy.deepcopy(all_remaining_lanes2)

    matching_result, matching_cost = decide_matching(summarization1, summarization2, current_candidates_lanes1, current_candidates_lanes2, False, print_result)

    # Remove matched lanes from lists
    for pair in matching_result:
        if(pair[0]):
            new_remaining_lanes1 = [lane for lane in new_remaining_lanes1 if lane.lane_id != pair[0]]
        if(pair[1]):
            new_remaining_lanes2 = [lane for lane in new_remaining_lanes2 if lane.lane_id != pair[1]]

    for pair in matching_result:

        if(print_result):
            print("Propagating.")
        # Determine lanes that require immediate propagation for both summarizations
        interacting_lanes1 = []
        for interaction_point in summarization1.interaction_points:
            if (pair[0] and pair[0] in interaction_point.interaction_lanes):
                interacting_lanes1.extend(interaction_point.interaction_lanes)
        interacting_lanes1 = list(set(interacting_lanes1))

        interacting_lanes2 = []
        for interaction_point in summarization2.interaction_points:
            if (pair[1] and pair[1] in interaction_point.interaction_lanes):
                interacting_lanes2.extend(interaction_point.interaction_lanes)
        interacting_lanes2 = list(set(interacting_lanes2))

        propagation_lanes1 = [lane for lane in new_remaining_lanes1 if lane.lane_id in interacting_lanes1]
        propagation_lanes2 = [lane for lane in new_remaining_lanes2 if lane.lane_id in interacting_lanes2]

        propagation_matching, propagation_cost, new_propagation_lanes1, new_propagation_lanes2 = propagate_decision(summarization1, summarization2, new_remaining_lanes1, new_remaining_lanes2, propagation_lanes1, propagation_lanes2, print_result)
        
        matching_result.extend(propagation_matching)
        matching_cost += propagation_cost
        new_remaining_lanes1 = new_propagation_lanes1
        new_remaining_lanes2 = new_propagation_lanes2        

    return matching_result, matching_cost, new_remaining_lanes1, new_remaining_lanes2


def propagate_optionality(summarization, remaining_lanes, current_candidate, print_result):

    import copy 

    # Initialize propagation variables
    propagation_result = []
    propagation_cost = 0

    returned_remaining_lanes = copy.deepcopy(remaining_lanes)

    # Extract all lanes that interact with the current candidate
    interacting_lanes = []
    for interaction_point in summarization.interaction_points:
        if (current_candidate.lane_id in interaction_point.interaction_lanes):
            interacting_lanes.extend(interaction_point.interaction_lanes)
    interacting_lanes = list(set(interacting_lanes))

    propagation_lanes = [lane for lane in remaining_lanes if lane in interacting_lanes]

    while propagation_lanes:
        current_lane = interacting_lanes.pop()
        if(print_result):
            print("Lane " + str(current_lane.lane_id) + " of Super Variant 1 has no matching partner and is optional.")
        propagation_result.append(tuple(current_lane.lane_id, None))
        propagation_cost += len(current_lane.elements)
        returned_remaining_lanes = [lane for lane in returned_remaining_lanes if lane.lane_id != current_lane.lane_id]

        new_interacting_lanes = []
        for interaction_point in summarization.interaction_points:
            if (current_lane.lane_id in interaction_point.interaction_lanes):
                new_interacting_lanes.extend(interaction_point.interaction_lanes)
        new_interacting_lanes = list(set(new_interacting_lanes))

        propagation_lanes.extend([lane for lane in remaining_lanes if lane in new_interacting_lanes])
        propagation_lanes = list(set(propagation_lanes))

    return propagation_result, propagation_cost, returned_remaining_lanes


def levenshtein_distance(lane1, lane2):
    import math
    realizations1 = lane1.get_realizations()
    realizations2 = lane2.get_realizations()
    minimum = math.inf

    for realization1 in realizations1:
        for realization2 in realizations2:
            minimum = min(minimum, __levenshtein_distance_realizations(realization1.elements, realization2.elements))

    return minimum


def __levenshtein_distance_realizations(lane1, lane2):
    if(len(lane2) == 0):
        return len(lane1)
    elif(len(lane1) == 0):
        return len(lane2)
    elif(type(lane1[0]) == type(lane2[0]) and lane1[0].activity == lane2[0].activity):
        return __levenshtein_distance_realizations(lane1[1:],lane2[1:])
    else:
        return 1 + min(__levenshtein_distance_realizations(lane1[1:],lane2[1:]), __levenshtein_distance_realizations(lane1,lane2[1:]),__levenshtein_distance_realizations(lane1[1:],lane2))
