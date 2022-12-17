import Super_Variant_Definition as SVD
import Super_Variant_Visualization as WVV

def join_super_variants(summarization1, summarization2):
    import copy
    WVV.visualize_super_variant_summarization(summarization1)
    WVV.visualize_super_variant_summarization(summarization2)
    mapping, cost = decide_matching(summarization1, summarization2, copy.deepcopy(summarization1.lanes), copy.deepcopy(summarization2.lanes), True, False)
    print(mapping)
    print("The cost of joining these Super Variants is " + str(cost) + ".")
    result, cost, mapping = join_super_lanes(summarization1, summarization2, summarization1.lanes[1].lane_id, summarization2.lanes[1].lane_id, summarization1.lanes[1].elements, summarization2.lanes[1].elements, 0)
    #print(result)
    for elem in result:
        print(elem)
    return

def join_super_lanes(summarization1, summarization2, id1, id2, lane1_elements, lane2_elements, current_position):

    result_elements = []
    result_cost = 0
    result_mapping = []
    
    # No elements remain in lane2, thus the rest of lane1 is entirely optional (Should actaully be a unified optional construct)
    if(len(lane2_elements) == 0):
        print("No elements remain in lane 2. The remaining elements in lane 1 will become optional.")
        connected_activities = []
        start_position = current_position

        for elem in lane1_elements:
            if(isinstance(elem, SVD.CommonConstruct)):
                if(isinstance(elem, SVD.InteractionConstruct)):
                    for interaction in summarization1.interaction_points:
                        if(interaction.index_in_lanes == elem.position and id1 in interaction.interaction_lanes):
                            result_mapping.append({current_position: {id1: (interaction.index_in_lanes, interaction.interaction_lanes)}})
                connected_activities.append(elem)
                result_cost  += 1
                current_position += 1
                
            elif(isinstance(elem, SVD.GeneralChoiceStructure)):
                result_cost += 1
                if(connected_activities != []):
                    sequence = []
                    frequency = 0
                    for elem in connected_activities:
                        sequence.append(elem.activity)
                        frequency = elem.frequency
                    result_elements.append(SVD.OptionalConstruct([sequence], frequency, start_position, current_position))
                    current_position += 1
                    start_position = current_position
                    
                    connected_activities = []

                result_elements.append(SVD.OptionalConstruct(elem.choices, elem.frequencies, current_position, current_position + (elem.position_end - elem.position_start)))
                current_position = current_position + (elem.position_end - elem.position_start)
                start_position = current_position
            
        if(connected_activities != []):
            sequence = []
            frequency = 0
            for elem in connected_activities:
                sequence.append(elem.activity)
                frequency = elem.frequency
            result_elements.append(SVD.OptionalConstruct([sequence], frequency, start_position, current_position))

        return result_elements, result_cost, result_mapping


    # No elements remain in lane1, thus the rest of lane2 is entirely optional (Should actaully be a unified optional construct)
    elif(len(lane1_elements) == 0):
        print("No elements remain in lane 1. The remaining elements in lane 2 will become optional.")
        connected_activities = []
        start_position = current_position

        for elem in lane2_elements:
            if(isinstance(elem, SVD.CommonConstruct)):
                if(isinstance(elem, SVD.InteractionConstruct)):
                    for interaction in summarization2.interaction_points:
                        if(interaction.index_in_lanes == elem.position and id2 in interaction.interaction_lanes):
                            result_mapping.append({current_position: {id2: (interaction.index_in_lanes, interaction.interaction_lanes)}})
                connected_activities.append(elem)
                result_cost  += 1
                current_position += 1
                
            elif(isinstance(elem, SVD.GeneralChoiceStructure)):
                result_cost += 1
                if(connected_activities != []):
                    sequence = []
                    frequency = 0
                    for elem in connected_activities:
                        sequence.append(elem.activity)
                        frequency = elem.frequency
                    result_elements.append(SVD.OptionalConstruct([sequence], frequency, start_position, current_position))
                    current_position += 1
                    start_position = current_position
                    
                    connected_activities = []

                result_elements.append(SVD.OptionalConstruct(elem.choices, elem.frequencies, current_position, current_position + (elem.position_end - elem.position_start)))
                current_position = current_position + (elem.position_end - elem.position_start)
                start_position = current_position
            
        if(connected_activities != []):
            sequence = []
            frequency = 0
            for elem in connected_activities:
                sequence.append(elem.activity)
                frequency = elem.frequency
            result_elements.append(SVD.OptionalConstruct([sequence], frequency, start_position, current_position))

        return result_elements, result_cost, result_mapping

    elif((type(lane1_elements[0]) == SVD.CommonConstruct and type(lane2_elements[0]) == SVD.CommonConstruct) or (type(lane1_elements[0]) == SVD.InteractionConstruct and type(lane2_elements[0]) == SVD.InteractionConstruct)):
    
        print("Considering the element " + str(lane1_elements[0]) + " of lane 1 and the element " + str(lane2_elements[0]) + " of lane 2.")

        # If both are single elements (no choice or optional) and perfectly align, merge them
        if(lane1_elements[0].activity == (lane2_elements[0].activity)):

            # map the original two interaction points to the new position
            if(isinstance(lane1_elements[0], SVD.InteractionConstruct)):
                value1 = tuple()
                value2 = tuple()
                for interaction in summarization1.interaction_points:
                    if(interaction.index_in_lanes == lane1_elements[0].position and id1 in interaction.interaction_lanes):
                        value1 = (interaction.index_in_lanes, interaction.interaction_lanes)
                for interaction in summarization2.interaction_points:
                    if(interaction.index_in_lanes == lane2_elements[0].position and id2 in interaction.interaction_lanes):
                        value2 = (interaction.index_in_lanes, interaction.interaction_lanes)
                result_mapping.append({current_position: {id1: value1, id2: value2}})

            print("Merging the element " + str(lane1_elements[0]) + " of lane 1 with the element " + str(lane2_elements[0]) + " into a common element.")
            recursive_elements, recursive_cost, recursive_mapping = join_super_lanes(summarization1, summarization2, id1, id2, lane1_elements[1:], lane2_elements[1:], current_position + 1)
            return [SVD.CommonConstruct(lane1_elements[0].activity, lane1_elements[0].frequency + lane2_elements[0].frequency, current_position)] + recursive_elements, recursive_cost, result_mapping + recursive_mapping

        # If both are single elements (no choice or optional), but do not perfectly align then evaluate the best option
        # 1. Make either one of the optional and continue
        # 2. Merge them into a choice and continue
        else:
            optional1_elements, optional1_cost, optional1_mapping = join_super_lanes(summarization1, summarization2, id1, id2, lane1_elements[1:], lane2_elements, current_position + 1)
            optional2_elements, optional2_cost, optional2_mapping = join_super_lanes(summarization1, summarization2, id1, id2, lane1_elements, lane2_elements[1:], current_position + 1)
            merge12_elements, merge12_cost, merge12_mapping = join_super_lanes(summarization1, summarization2, id1, id2, lane1_elements[1:], lane2_elements[1:], current_position + 1)

            # Case 1.1
            if(optional1_cost <= optional2_cost and optional1_cost <= merge12_cost):

                if(isinstance(lane1_elements[0], SVD.InteractionConstruct)):
                    for interaction in summarization1.interaction_points:
                        if(interaction.index_in_lanes == lane1_elements[0].position and id1 in interaction.interaction_lanes):
                            result_mapping.append({current_position: {id1: (interaction.index_in_lanes, interaction.interaction_lanes)}})

                print("Making the element " + str(lane1_elements[0]) + " of lane 1 optional.")
                return [SVD.OptionalConstruct([lane1_elements[0].activity], [lane1_elements[0].frequency], current_position, current_position)] + optional1_elements, 1 + optional1_cost, result_mapping + optional1_mapping

            # Case 1.2
            elif(optional2_cost <= merge12_cost):
                
                if(isinstance(lane2_elements[0], SVD.InteractionConstruct)):
                    for interaction in summarization2.interaction_points:
                        if(interaction.index_in_lanes == lane2_elements[0].position and id2 in interaction.interaction_lanes):
                            result_mapping.append({current_position: {id2: (interaction.index_in_lanes, interaction.interaction_lanes)}})

                print("Making the element " + str(lane2_elements[0]) + " of lane 2 optional.")
                return [SVD.OptionalConstruct([lane2_elements[0].activity], [lane2_elements[0].frequency], current_position, current_position)] + optional2_elements, 1 + optional2_cost, result_mapping + optional2_mapping
            
            # Case 2
            else:

                if(isinstance(lane1_elements[0], SVD.InteractionConstruct)):
                    value1 = tuple()
                    value2 = tuple()
                    for interaction in summarization1.interaction_points:
                        if(interaction.index_in_lanes == lane1_elements[0].position and id1 in interaction.interaction_lanes):
                            value1 = (interaction.index_in_lanes, interaction.interaction_lanes)
                    for interaction in summarization2.interaction_points:
                        if(interaction.index_in_lanes == lane2_elements[0].position and id2 in interaction.interaction_lanes):
                            value2 = (interaction.index_in_lanes, interaction.interaction_lanes)
                    result_mapping.append({current_position: {id1: value1, id2: value2}})

                print("Merging the element " + str(lane1_elements[0]) + " of lane 1 with the element " + str(lane2_elements[0]) + " into a choice element.")
                return [SVD.ChoiceConstruct([lane1_elements[0].activity, lane2_elements[0].activity], [lane1_elements[0].frequency, lane2_elements[0].frequency], current_position, current_position)] + merge12_elements, 1 + merge12_cost, result_mapping + merge12_mapping

    # Interaction points should always be matched with the next interaction point of the other lane, thus make the other element optional if there is no match and continue
    elif((type(lane1_elements[0]) == SVD.InteractionConstruct and type(lane2_elements[0]) != type(lane1_elements[0]))):

        optional2_elements, optional2_cost, optional2_mapping = join_super_lanes(summarization1, summarization2, id1, id2, lane1_elements, lane2_elements[1:], current_position + 1)

        print("Making the element " + str(lane2_elements[0]) + " of lane 2 optional.")
        return [SVD.OptionalConstruct([lane2_elements[0].activity], [lane2_elements[0].frequency], current_position, current_position)] + optional2_elements, 1 + optional2_cost, result_mapping + optional2_mapping

    # Interaction points should always be matched with the next interaction point of the other lane, thus make the other element optional if there is no match and continue
    elif((type(lane2_elements[0]) == SVD.InteractionConstruct and type(lane1_elements[0]) != type(lane1_elements[0]))):
        
        optional1_elements, optional1_cost, optional1_mapping = join_super_lanes(summarization1, summarization2, id1, id2, lane1_elements[1:], lane2_elements, current_position + 1)

        print("Making the element " + str(lane1_elements[0]) + " of lane 1 optional.")
        return [SVD.OptionalConstruct([lane1_elements[0].activity], [lane1_elements[0].frequency], current_position, current_position)] + optional1_elements, 1 + optional1_cost, result_mapping + optional1_mapping
    
    else:
        # Case 1: 1 Common, other Optional/Choice

        # Case 2: Both Optional/Choice

        print("Exit")
        return result_elements, result_cost, result_mapping



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
