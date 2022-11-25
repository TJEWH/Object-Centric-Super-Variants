import Input_Extraction_Definition as IED
import Super_Variant_Definition as SVD

def max_order_preserving_common_activities(lanes):
    '''
    Extracts the longest sequence od activities found in all lanes, preserving their order
    :param lanes: Multiple sequences of activities
    :type lanes: list of VariantLane
    :return: the longest order preserving common activity sequence and their indices in the variant
    :rtype: dict
    '''
    # Initialization, copy elements
    activity_sets = []
    l = [lane.activities for lane in lanes]
    base_lane = l[0]
    base_indices = lanes[0].horizontal_indices
    
    # Retrieves all common sublists that ensure the precise order
    for i in range(len(base_lane)):
        
        # Keeping track of the original indices and the remaining sublists
        comparison = [] 
        indices = []
        for lane in range(1,len(l)):
            comparison.append(lanes[lane].activities)
            indices.append(lanes[lane].horizontal_indices)
            
        set = dict()
        
        # For each activity in base lane as starting point find the list of activities
        # that appear in all other lanes
        for j in range(i,len(base_lane)):
            if (all(base_lane[j] in lane for lane in comparison[0:])):

                #Create result tuple
                indices_of_lane = ()
                indices_of_lane = indices_of_lane + (base_indices[j],)
                
                # Add the corresponding index for each other variant and adjust the lists
                for k in range(len(comparison)):
                    indices_of_lane = indices_of_lane + (indices[k][comparison[k].index(base_lane[j])],)
                    indices[k] = indices[k][comparison[k].index(base_lane[j])+1:]
                    comparison[k] = comparison[k][comparison[k].index(base_lane[j])+1:]
                
                set[base_lane[j]] = indices_of_lane
        activity_sets.append(set)
        
    # Return the maximal list of activities for optimality
    return max(activity_sets, key=len)

def check_optional_pattern(activities):
    '''
    Checks whether only one of the given activities subsequences is non-empty, thus allowing 
    to apply the Optional Pattern
    :param activities: subsequences of activities of multiple lanes between common activities
    :type activities: list
    :return: Whether or not the Optional Pattern can be applied
    :rtype: Boolean
    '''
    non_empty_sequences = [activity_list[0] for activity_list in activities if activity_list[0]]
    non_empty_sequences = [list(sequence) for sequence in set(tuple(sequence) for sequence in non_empty_sequences)]
    return len(non_empty_sequences) == 1


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
    
    if(check_optional_pattern(activities)):
        
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

            is_interacting_activity = IED.is_interaction_point(interactions, optional_activities[0][0][i], indices)        
            if(print_result):
                print("This is an interaction point: " + str(is_interacting_activity))
            if (is_interacting_activity):
                for index in (indices):
                    new_interaction_points_mapping[index,optional_activities[0][0][i]] = length
            
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
                    is_interacting_activity = IED.is_interaction_point(interactions, elem[0][i],[index])    
                    contains_interaction_point = (contains_interaction_point or is_interacting_activity)
                    if (is_interacting_activity):
                        new_interaction_points_mapping[index, elem[0][i]] = length
                        
                
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
                elements.append(SVD.OptionalConstruct([c for c in choice if c != ""],frequencies))
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


def summarize_lanes(lanes, interactions, print_result):
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
    common_activities = max_order_preserving_common_activities(lanes)

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
        is_interacting_activity = IED.is_interaction_point(interactions, list(common_activities.keys())[i],list(common_activities.values())[i])        
        if(print_result):
            print("This is an interaction point: " + str(is_interacting_activity))
        if (is_interacting_activity):
            for index in (set(list(common_activities.values())[i])):
                new_interaction_points_mapping[index,list(common_activities.keys())[i]] = current_horizontal_index
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
            value = {}
            for k in range(len(mappings)):
                if(key in list(mappings[k][1].keys())):
                    value[mappings[k][0]] = mappings[k][1][key]
            merged_mappings[key] = value
            
    new_interactions = {}
    # merge all mappings that represent the same new interaction point
    for key in merged_mappings.keys():
        value = merged_mappings[key]
        merging_candidates = [k for k in list(merged_mappings.keys()) if merged_mappings[k] == value]
        
        if not(any(k in merging_candidates for k in list(new_interactions.keys()))):
            new_interactions[key] = value
    
    # Remove all interaction points, that no longer are interaction points
    result = {}
    for key in new_interactions.keys():
        if (len(list(new_interactions[key].keys())) > 1):
            result[key] = new_interactions[key]
    
    return result            
            

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
    mappings = merge_interaction_mappings(mappings)
    print(mappings)
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


def partition(collection):
    if len(collection) == 1:
        yield [collection]
        return

    first = collection[0]
    for smaller in partition(collection[1:]):
        # insert `first` in each of the subpartition's subsets
        for n, subset in enumerate(smaller):
            yield smaller[:n] + [[first] + subset]  + smaller[n+1:]
        # put `first` in its own subset 
        yield [ [ first ] ] + smaller

def get_partitions(candidate):
    partitions = []
    for n, p in enumerate(partition(list(candidate)), 1):
        partitions.append(p)
    return(partitions)
