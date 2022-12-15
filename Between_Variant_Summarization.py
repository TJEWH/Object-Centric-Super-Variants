import Super_Variant_Definition as SVD
import Super_Variant_Visualization as WVV

def join_super_variants(summarization1, summarization2):
    WVV.visualize_super_variant_summarization(summarization1)
    WVV.visualize_super_variant_summarization(summarization2)
    #print(summarization1.lanes[1])
    #print(summarization2.lanes[1])
    #print(levensthein_distance(summarization1.lanes[1], summarization2.lanes[1]))
    mapping, cost = decide_matching(summarization1, summarization2, summarization1.lanes, summarization2.lanes)
    print(mapping)
    print(cost)
    return


def decide_matching(summarization1, summarization2, remaining_lanes1, remaining_lanes2, propagate = True):
    import math

    # Base case 1: All lanes of summarization1 are matched
    if(len(remaining_lanes1) == 0):
        print("Empty. The rest is optional.")
        result = []
        cost = 0
        for lane in remaining_lanes2:
            print("Lane " + str(lane.lane_id) + " of Super Variant 2 has no matching partner and is optional.")
            result.append((None, lane.lane_id))
            cost += len(lane.elements)
        return result, cost
    
    # Base case 2: All lanes of summarization2 are matched
    elif(len(remaining_lanes2) == 0):
        print("Empty. The rest is optional.")
        result = []
        cost = 0
        for lane in remaining_lanes1:
            print("Lane " + str(lane.lane_id) + " of Super Variant 1 has no matching partner and is optional.")
            result.append((lane.lane_id, None))
            cost += len(lane.elements)
        return result, cost

    else:
        current_matching_candidate_1 = remaining_lanes1.pop()
        matching_candidates_2 = [lane for lane in remaining_lanes2 if lane.object_type == current_matching_candidate_1.object_type]

        # Fallback case: no corresponding matching
        if(len(matching_candidates_2) == 0):
            
            print("Lane " + str(current_matching_candidate_1.lane_id) + " of Super Variant 1 has no matching partner and is optional.")
            matching = [(current_matching_candidate_1.lane_id, None)]
            cost = len(current_matching_candidate_1.elements)
            new_remaining_lanes2 = remaining_lanes2
            propagation_matching, propagation_cost, new_remaining_lanes1 = propagate_optionality(summarization1, remaining_lanes1, current_matching_candidate_1)
            least_cost = propagation_cost + cost

        # Otherwise evaluate decision options
        else:
            least_cost = math.inf
            least_cost_matching = []
            least_cost_propagation_matching = []
            least_cost_new_remaining_lanes1 = []
            least_cost_new_remaining_lanes2 = []

            for candidate_2 in matching_candidates_2:
                print("Evaluating the decision of matching lane " + str(current_matching_candidate_1.lane_id) + " of Super Variant 1 with the lane " + str(current_matching_candidate_1.lane_id) + " of Super Variant 2.")
                intermediate_matching = [(current_matching_candidate_1.lane_id, candidate_2.lane_id)]
                intermediate_cost = levensthein_distance(current_matching_candidate_1, candidate_2)
                intermediate_remaining_lanes2_now = [lane for lane in remaining_lanes2 if lane.lane_id != candidate_2.lane_id]

                if(propagate):

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
                    intermediate_propagation_matching, intermediate_propagation_cost, intermediate_remaining_lanes1, intermediate_remaining_lanes2 = propagate_decision(summarization1, summarization2, remaining_lanes1, intermediate_remaining_lanes2_now, propagation_lanes1, propagation_lanes2)

                else:
                    print("Not propagating.")
                    intermediate_propagation_matching = []
                    intermediate_propagation_cost = 0 
                    intermediate_remaining_lanes1 = remaining_lanes1
                    intermediate_remaining_lanes2 = intermediate_remaining_lanes2_now

                # Update the best evaluated choice
                if(intermediate_propagation_cost + intermediate_cost < least_cost):
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

        print("------------------------------------")

        # Continue matching
        if(len(new_remaining_lanes1) == 0 and len(new_remaining_lanes2) == 0):
            following_matching = []
            following_cost = 0
        else:
            following_matching, following_cost = decide_matching(summarization1, summarization2, new_remaining_lanes1, new_remaining_lanes2)
        return matching + propagation_matching + following_matching, least_cost + following_cost

def propagate_decision(summarization1, summarization2, all_remaining_lanes1, all_remaining_lanes2, current_candidates_lanes1, current_candidates_lanes2):

    import copy

    print("Propagating the last decision among " + str(current_candidates_lanes1) + " and " + str(current_candidates_lanes2) +".")
    new_remaining_lanes1 = copy.deepcopy(all_remaining_lanes1)
    new_remaining_lanes2 = copy.deepcopy(all_remaining_lanes2)

    matching_result, matching_cost = decide_matching(summarization1, summarization2, current_candidates_lanes1, current_candidates_lanes2, False)

    # Remove matched lanes from lists
    for pair in matching_result:
        if(pair[0]):
            new_remaining_lanes1 = [lane for lane in new_remaining_lanes1 if lane.lane_id != pair[0]]
        if(pair[1]):
            new_remaining_lanes2 = [lane for lane in new_remaining_lanes2 if lane.lane_id != pair[1]]

    for pair in matching_result:

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

        propagation_matching, propagation_cost, new_propagation_lanes1, new_propagation_lanes2 = propagate_decision(summarization1, summarization2, new_remaining_lanes1, new_remaining_lanes2, propagation_lanes1, propagation_lanes2)
        
        matching_result.extend(propagation_matching)
        matching_cost += propagation_cost
        new_remaining_lanes1 = new_propagation_lanes1
        new_remaining_lanes2 = new_propagation_lanes2        

    return matching_result, matching_cost, new_remaining_lanes1, new_remaining_lanes2

    

    #if allremaining / current != empty:
        #updated_lanes = remove current lanes from remaining
        #final_res = propagate_decision(updated_lanes)
    #final_res += res
    #return

def propagate_optionality(summarization, remaining_lanes, current_candidate):

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

def levensthein_distance(lane1, lane2):
    import math
    realizations1 = lane1.get_realizations()
    realizations2 = lane2.get_realizations()
    minimum = math.inf

    for realization1 in realizations1:
        for realization2 in realizations2:
            minimum = min(minimum, __levensthein_distance_realizations(realization1.elements, realization2.elements))

    return minimum


def __levensthein_distance_realizations(lane1, lane2):
    if(len(lane2) == 0):
        return len(lane1)
    elif(len(lane1) == 0):
        return len(lane2)
    elif(type(lane1) == type(lane2) and lane1[0].activity == lane2[0].activity):
        return __levensthein_distance_realizations(lane1[1:],lane2[1:])
    else:
        return 1 + min(__levensthein_distance_realizations(lane1[1:],lane2[1:]), __levensthein_distance_realizations(lane1,lane2[1:]),__levensthein_distance_realizations(lane1[1:],lane2))

def super_lane_edit_distance(lane1, lane2, summarization1, summarization2):

    import math
    if (lane1.object_type != lane2.object_type):
        return math.inf, None

    else:
        print(lane1)
        print(lane2)
        align_interaction_points(summarization1,summarization2, lane1, lane2)

            
def align_interaction_points(summarization1, summarization2, lane1, lane2):
    import math
    import copy

    lane1_interaction_points = get_all_interaction_points(summarization1, lane1)
    print(lane1_interaction_points)
    lane2_interaction_points = get_all_interaction_points(summarization2, lane2)

    interaction_point_mappings = []
    remaining_interaction_set2 = lane2_interaction_points
    for interaction_set1 in lane1_interaction_points.keys():
        minimal_distance = math.inf
        minimal_interaction_mapping = None
        for interaction_set2 in remaining_interaction_set2.keys():
            current_distance = get_distance_interaction_points(lane1_interaction_points[interaction_set1], remaining_interaction_set2[interaction_set2])
            if(current_distance < minimal_distance):
                minimal_distance = current_distance
                minimal_interaction_mapping = interaction_set2
        interaction_point_mappings.append([interaction_set1, minimal_interaction_mapping, minimal_distance])
        del remaining_interaction_set2[minimal_interaction_mapping]

    print(interaction_point_mappings)
    element_mapping = dict()
    number_of_interaction = 0
    for elem in lane1.elements:
        #if(isinstance(elem, SVD.InteractionConstruct)):

            #number_of_interaction += 1
            #interaction_point = [interaction_point for interaction_point in summarization1.interaction_points if lane1.lane_id in interaction_point.interaction_lanes and elem.position == interaction_point.index_in_lanes][0]
            #key1 = copy.deepcopy(interaction_point.interaction_lanes)
            #key1.sort()
            #key1 = str(key1)
            #key2 = [mapping[1] for mapping in interaction_point_mappings if mapping[0] == key1][0]
            
            
        return       


def get_all_interaction_points(summarization, lane):

    import copy
    result = dict()
    for i in range(len(lane.elements)):

        if (isinstance(lane.elements[i], SVD.InteractionConstruct)):

            interaction_point = [interaction_point for interaction_point in summarization.interaction_points if lane.lane_id in interaction_point.interaction_lanes and lane.elements[i].position == interaction_point.index_in_lanes][0]

            key = copy.deepcopy(interaction_point.interaction_lanes)
            key.sort()

            if(str(key) in result.keys()):
                result[str(key)][0][lane.elements[i].position] = lane.elements[i]

            else:
                
                types_cardinalities = dict()
                for type in interaction_point.interacting_types:
                    cardinalities = []
                    interacting_type_lanes = [type_lane for type_lane  in summarization.lanes if type_lane.lane_id in interaction_point.interaction_lanes and type_lane.object_type == type]
                    for interacting_lane in interacting_type_lanes:
                        cardinalities.append(interacting_lane.cardinality)
                    cardinalities.sort()
                    types_cardinalities[type] = cardinalities

                result[str(key)] = (dict(), types_cardinalities)
                result[str(key)][0][lane.elements[i].position] = lane.elements[i]

    return result


def get_distance_interaction_points(interactions1, interactions2):

    import textdistance
    distance = 0

    # Determine distance among cardinality-type-relations
    for type in interactions1[1].keys():
        if type not in interactions2[1].keys():
            distance += len(interactions1[1][type])*2
        else: 
            distance += textdistance.levenshtein.distance(interactions1[1][type], interactions2[1][type])

    for type in interactions2[1].keys():
        if type not in interactions1[1].keys():
            distance += len(interactions2[1][type])*2

    # Determine distance among point-label-relations
    all_activity_labels = set()
    for element in interactions1[0].values():
        all_activity_labels.add(element.activity)
    for element  in interactions2[0].values():
        all_activity_labels.add(element.activity)

    activity_mapping = dict((activity, number) for number, activity in enumerate(all_activity_labels))

    order_name_list1 = []
    for position in interactions1[0].keys():
        order_name_list1.append(activity_mapping[interactions1[0][position].activity])

    order_name_list2 = []
    for position in interactions2[0].keys():
        order_name_list2.append(activity_mapping[interactions2[0][position].activity])

    distance += textdistance.levenshtein.distance(order_name_list1, order_name_list2)
    return distance



    
    return