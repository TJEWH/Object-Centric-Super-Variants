import Input_Extraction_Definition as IED
import Summarization_Utils as SU
import Super_Variant_Definition as SVD

def get_candidates(lanes, interactions):
    result = []
    
    for lane1 in lanes:
        candidate_set = {lane1}
        candidate_interactions = [interaction for interaction in interactions if lane1 in interaction.interaction_lanes]
        for lane2 in lanes:
            if (lane1 != lane2 and lane1.object_type == lane2.object_type):
                if (all([lane2 in interaction.interaction_lanes for interaction in candidate_interactions])):
                    candidate_set.add(lane2)
        if(candidate_set not in result):
            result.append(candidate_set)
        
    return result

def branch_on_candidates(variant, remaining_candidates, init_summarization, level, print_result):
    import copy
    current_summarization = copy.deepcopy(init_summarization)
    print("Current Level: " + str(level))
    for partition in current_summarization["Candidate"]:
        print("Summarizing Lanes: " + str([lane.lane_id for lane in partition]))
        summarized_lane, new_mappings = between_lane_summarization(partition, variant.interaction_points, False)
        current_summarization["Lanes"].append(summarized_lane)
        current_summarization["Mappings"].append((summarized_lane.lane_id, new_mappings))

    # Recursive call
    if (len(remaining_candidates) == 0):
        print("Leaf node reached!")
        return [current_summarization]
    else:
        result = []
        for candidate in SU.get_partitions(remaining_candidates[0]):
            current_summarization["Candidate"] = candidate
            result.extend(branch_on_candidates(variant, remaining_candidates[1:], (current_summarization), level+1, print_result))
        return result

def within_variant_summarization(variant, print_result = True):
    all_candidates = get_candidates(variant.lanes, variant.interaction_points)
    first_choice =  SU.get_partitions(all_candidates[0])
    all_summarizations = []
    init_summary = {}
    init_summary["Lanes"] = []
    init_summary["Mappings"] = []
    for partition in first_choice:
        init_summary["Candidate"] = partition
        all_summarizations.extend(branch_on_candidates(variant, all_candidates[1:], init_summary, 1, print_result))

    
    result = []
    for summarization in all_summarizations:
        for lane in summarization["Lanes"]:
            print(lane)
        result_lanes, result_interaction_points = re_align_lanes(summarization["Lanes"], merge_interaction_mappings(summarization["Mappings"]),False)
        result.append(SVD.SummarizedVariant(result_lanes, variant.object_types, result_interaction_points))
    
    return result


def between_lane_summarization(lanes, interactions, print_result):
    '''
    Yields a generic summarizations of lanes of the same object type
    :param lanes: The lanes of the same object type that need summarization
    :type lanes: List of Variant Lanes
    :param interactions: The interaction points of the variant of the lanes
    :type interactions: List of Interaction Points
    :param print_result: Whether or not the print commands should be executed
    :type print_result: Boolean
    :return: The summarization of the given lanes
    :rtype: SummarizedLane
    '''
    common_activities = SU.max_order_preserving_common_activities(lanes)

    # Initializing the values for the summarized lanes object
    elements = []
    horizontal_indices = []
    object_type = lanes[0].object_type
    lane_name = lanes[0].object_type + " i"
    lane_id = tuple([lane.lane_id for lane in lanes])
    
    new_interaction_points_mapping = {}
    current_horizontal_index = 0
    
    # Add current indices for all lanes into a list
    positions = []
    for i in range(len(lanes)):
        first_index = list(common_activities.values())[0][i]
        positions.append((0,first_index))
        
    for i in range(len(common_activities)):
        
        # Determine all interval subprocesses and summarize them
        interval_subprocesses = []
        for j in range(len(lanes)):
            start_index = positions[j][0]
            end_index = lanes[j].horizontal_indices.index(positions[j][1])
            interval_subprocesses.append((lanes[j].activities[start_index:end_index],lanes[j].horizontal_indices[start_index:end_index]))
        
        # Add summarized subprocess to elements
        if(print_result):
            print("\n")
            print("Applying a pattern to the elements: ")
            print("\n")
            print(interval_subprocesses)
        interval_elements, interval_length, intermediate_new_interaction_points = apply_patterns(interval_subprocesses, interactions, print_result)
        elements.extend(interval_elements)
        horizontal_indices.extend(list(range(current_horizontal_index, current_horizontal_index + interval_length)))
        for key in list(intermediate_new_interaction_points.keys()):
            new_interaction_points_mapping[key] = intermediate_new_interaction_points[key] + current_horizontal_index
            if(print_result):
                print("We added the mapping: " + str(key) + " to " + str(intermediate_new_interaction_points[key] + current_horizontal_index))
        current_horizontal_index += interval_length
                     
        # Add the common activity to the elements of the summarized lane
        if(print_result):
            print("\n")
            print("Adding the common activity: ")
            print(list(common_activities.keys())[i])
        is_interacting_activity, interaction_point = IED.is_interaction_point(interactions, list(common_activities.keys())[i], list(common_activities.values())[i])        
        if(print_result):
            print("This is an interaction point: " + str(is_interacting_activity))
        if (is_interacting_activity):
            for index in (set(list(common_activities.values())[i])):
                new_interaction_points_mapping[(index, str(interaction_point.interaction_lanes))] = current_horizontal_index
                if(print_result):
                    print("We added the mapping: " + str(tuple([index,list(common_activities.keys())[i]])) + " to " + str(current_horizontal_index))
        
        elements.append(SVD.CommonConstruct(list(common_activities.keys())[i],len(lanes)))
        horizontal_indices.append(current_horizontal_index)
        current_horizontal_index += 1
            
        # Update indices for the next iteration
        new_positions = []
        for j in range(len(lanes)):
            if(i+1 < len(common_activities.values())):
                next_index = list(common_activities.values())[i+1][j]
            else:
                next_index = lanes[j].horizontal_indices[-1]
            new_positions.append((lanes[j].horizontal_indices.index(positions[j][1])+1,next_index))
        positions = new_positions
    
    # Check all activities after the last common activity
    interval_subprocesses = []
    for j in range(len(lanes)):
        start_index = positions[j][0]
        interval_subprocesses.append((lanes[j].activities[start_index:],lanes[j].horizontal_indices[start_index:]))
    
    # Add summarized subprocess to elements
    interval_elements, interval_length, intermediate_new_interaction_points = apply_patterns(interval_subprocesses, interactions, print_result)
    elements.extend(interval_elements)
    horizontal_indices.extend(list(range(current_horizontal_index, current_horizontal_index + interval_length)))
    for key in list(intermediate_new_interaction_points.keys()):
            new_interaction_points_mapping[key] = intermediate_new_interaction_points[key] + current_horizontal_index
            if(print_result):
                print("We added the mapping: " + str(key) + " to " + str(intermediate_new_interaction_points[key] + current_horizontal_index))
    current_horizontal_index += interval_length
        
    return SVD.SummarizedLane(lane_id, lane_name, object_type, elements, horizontal_indices, len(lanes)), new_interaction_points_mapping


def apply_patterns(activities, interactions, print_result):
    '''
    Determines an applicable pattern (Optional Pattern or Exclusive Choice Pattern) for a set of activity sequences 
    and their current indices
    :param activities: A list of activity sequences and their indices
    :type activities: List
    :param interactions: The interaction points of the variant of the lanes
    :type interactions: List of type InteractionPoint
    :param print_result: Whether or not the print commands should be executed
    :type print_result: Boolean
    :return: The application of a pattern to summarize the sequences, the number of elements of the summarization, 
             the mapping from orginal interaction points to their new indices in the summatrized sequence
    :rtype: List of type SummarizedConstruct, Int, Dictionary
    '''
    if sum([len(activity_list[0]) for activity_list in activities]) == 0:
        return [], 0, {}
    
    elements = []
    length = 0
    new_interaction_points_mapping = {}
    
    if(SU.check_optional_pattern(activities)):
        
        optional_activities = [activity_list for activity_list in activities if activity_list[0]]
        frequency = sum([1 for activity_list in activities if activity_list[0]])
        for i in range(len(optional_activities[0][0])):
            
            if(print_result):
            # Output printing
                print("\n")
                print("Adding the optional activity: ")
                print(optional_activities[0][0][i])
            
            # Storing the new positions of the interaction points
            indices = tuple()
            for j in range(len(optional_activities)):
                indices += (optional_activities[j][1][i],)

            is_interacting_activity, interaction_point = IED.is_interaction_point(interactions, optional_activities[0][0][i], indices)        
            if(print_result):
                print("This is an interaction point: " + str(is_interacting_activity))
            if (is_interacting_activity):
                for index in (indices):
                    new_interaction_points_mapping[index, str(interaction_point.interaction_lanes)] = length
            
            # Adding Construct
            elements.append(SVD.OptionalConstruct([optional_activities[0][0][i]],[frequency]))
            length += 1
            
        return elements, length, new_interaction_points_mapping
    
    else:
        
        choice_activities = [activity_list for activity_list in activities]
        longest_option = max([choice[0] for choice in choice_activities], key=len)
        unique_choice_sequences = [list(sequence) for sequence in set(tuple(sequence) for sequence in [option[0] for option in choice_activities])]

        # Add the corresponding choices
        for i in range(len(longest_option)):
            
            # Determine the activity at index i for each choice
            choice = []
            for j in range(len(unique_choice_sequences)):
                if (i < len(unique_choice_sequences[j])):
                    choice.append(unique_choice_sequences[j][i])
                else:
                    choice.append("")
            choice = list(set(choice))
            
            # Storing the new positions of the interaction points
            contains_interaction_point = False
            for elem in choice_activities:
                if(len(elem[1])>i):
                    index = elem[1][i]
                    is_interacting_activity, interaction_point = IED.is_interaction_point(interactions, elem[0][i],[index])    
                    contains_interaction_point = (contains_interaction_point or is_interacting_activity)
                    if (is_interacting_activity):
                        new_interaction_points_mapping[index, str(interaction_point.interaction_lanes)] = length
                        
                
            # Determine frequency
            frequencies = []
            for c in choice:
                if(c != ""):
                    frequency = 0
                    for j in range(len(choice_activities)):   
                        if(len(choice_activities[j][0])>i):
                            if(choice_activities[j][0][i] == c):
                                frequency += 1
                    frequencies.append(frequency)
                        
            if("" in choice):
                if(print_result):
                    print("This optional choice containts an interaction point: " + str(is_interacting_activity))
            
                if(print_result):
                    # Output printing
                    print("\n")
                    print("Adding the optional choice activities: ")
                    print([c for c in choice if c != ""])
            
            # Adding Construct
                elements.append(SVD.OptionalConstruct([c for c in choice if c != ""], frequencies))
                length += 1
            else:
                if(print_result):
                    print("This choice containts an interaction point: " + str(is_interacting_activity))
                
                if(print_result):
                    # Output printing
                    print("\n")
                    print("Adding the choice between the following activity: ")
                    print(choice)
            
                # Adding Construct
                elements.append(SVD.ChoiceConstruct(choice,frequencies))
                length += 1
            
        return elements, length, new_interaction_points_mapping


def merge_interaction_mappings(mappings):
    '''
    Pre-processes the mappings from the summarization for easy handling
    :param mappings: The mappings of original interaction points to new indices in the summarized lanes
    :type mappings: Dictionary
    :return: Each interaction point of the summarized lanes and their current positions in the involved lanes
    :rtype: Dictionary
    '''
    merged_mappings = {}
    # merge the individual dictionaries for all lanes
    for i in range(len(mappings)):
        mapping = mappings[i][1]
        for key in mapping.keys():
            positions = {}
            positions[mappings[i][0]] = mappings[i][1][key]
            for k in range(len(mappings)):
                if(k > i and key in list(mappings[k][1].keys())):
                    positions[mappings[k][0]] = mappings[k][1][key]
            if(len(positions.keys()) > 1 and key not in merged_mappings.keys()):
                merged_mappings[key] = positions
    
    return merged_mappings        
            

def re_align_lanes(lanes, mappings, print_result):
    '''
    Given the summarized lanes and the mappings from original interaction points to new indices, this method aligns the lane, such
    that interaction points between multiple lanes have the same horizontal index
    :param lanes: The summarized lanes
    :type lanes: List of type SummarizedLane
    :param mappings: The mappings of original interaction points to new indices in the summarized lanes for each lane
    :type mappings: Dictionary
    :param print_result: Whether or not the print commands should be executed
    :type print_result: Boolean
    :return: The lanes with updated horizontal indices and a list of the corresponding interaction points
    :rtype: List of type SummarizedLane, List of type InteractionPoint
    '''
    # Initialize variables and return values
    import copy
    aligned_lanes = copy.deepcopy(lanes)
    updated_mappings = copy.deepcopy(mappings)
    updated_interaction_points = []
    
    # Align the lanes such that the interaction points have the same horizontal index
    for i in range(len(mappings.keys())):
        earliest_interaction_point = min(updated_mappings.items(), key=lambda x: list(x[1].values()))
        if(print_result):
            print("We have an interaction at the following points in the interacting lanes: " + str(earliest_interaction_point[1]))
        name = earliest_interaction_point[0][1]
        lanes = [lane.lane_id for lane in aligned_lanes if lane.lane_id in list(earliest_interaction_point[1].keys())]
        types = list(earliest_interaction_point[1].keys())
        
        if(len(set(list(earliest_interaction_point[1].values()))) == 1):
            if(print_result):
                print("No alignment required.")
            position = list(earliest_interaction_point[1].values())[0]
            
        else: 
            target_position = max(set(list(earliest_interaction_point[1].values())))
            position = target_position
            involved_lanes = [lane for lane in aligned_lanes if lane.lane_id in list(earliest_interaction_point[1].keys())]
            for lane in involved_lanes:
                
                # Shift indices by the offset
                current_position = updated_mappings[earliest_interaction_point[0]][lane.lane_id]
                offset = target_position - current_position
                if(print_result):
                    print("We have shifted lane " + lane.lane_name + " by " + str(offset) + " starting from activity " + str(lane.elements[lane.horizontal_indices.index(current_position)]) + ".")
                lane.update_indices(lane.horizontal_indices.index(current_position),offset)
                
                
                # Update all values in the dictionary accordingly
                for key in updated_mappings.keys():
                    if(lane.lane_id in updated_mappings[key].keys() and updated_mappings[key][lane.lane_id]>=current_position):
                        updated_mappings[key][lane.lane_id] += offset
                
        del updated_mappings[earliest_interaction_point[0]]
        updated_interaction_points.append(IED.InteractionPoint(name, lanes, types, position))
        
    return aligned_lanes, updated_interaction_points