import Input_Extraction_Definition as IED
import Super_Variant_Definition as SVD

def __get_candidates(lanes, interactions):
    '''
    Yields all maximal merging candidate sets for a set of lanes, thus, all sets of lanes that share all interaction points
    :param lanes: The lanes of the variant
    :type lanes: List of VariantLane
    :param interactions: The interactions of the variant
    :type interactions: List of InteractionPoints
    :return: A list of sets of lanes that can be merged
    :rtype: List
    '''
    result = []
    
    for lane1 in lanes:
        candidate_set = {lane1}
        candidate_interactions = []
        for interaction in interactions:
            if (lane1.lane_id in interaction.interaction_lanes):
                candidate_interactions.extend(interaction.interaction_lanes)
                
        for lane2 in lanes:
            if (lane1 != lane2 and lane1.object_type == lane2.object_type):
                comparison_interactions = []
                for interaction in interactions:
                     if (lane2.lane_id in interaction.interaction_lanes):
                        comparison_interactions.extend(interaction.interaction_lanes)
                if (set(candidate_interactions) == set(comparison_interactions)):
                    candidate_set.add(lane2)
        if(candidate_set not in result):
            result.append(candidate_set)
        
    return result

def __branch_on_candidates(variant, remaining_candidates, init_summarization, level, print_result):
    '''
    Visits one node in the candidate tree, summarizes the current merging candidate and recurses on subtrees
    :param variant: The variant to be summarized
    :type variant: ExtractedVariant
    :param remaining_candidates: The merging candidates that have not yet been merged
    :type remaining_candidates: List
    :param init_summarization: Stores the current state of the within-variant summarization, namely the summarized lanes thus far and the corresponding mappings of interaction points
    :type init_summarization: Dictionary
    :param level: The current depth in the tree
    :type level: Integer
    :param print_result: Whether or not the print commands should be executed
    :type print_result: Boolean
    :return: The summarization of the current candidate joined with the results from the child nodes
    :rtype: List
    '''
    import copy
    current_summarization = copy.deepcopy(init_summarization)
    new_lanes = []
    new_mappings = []
    if(print_result):
        print("------------------------------------------")
        print("Current Level: " + str(level))
    for partition in current_summarization["Candidate"]:
        if(print_result):
            print("----")
            print("Summarizing Lanes: " + str([lane.lane_id for lane in partition]))
        summarized_lane, new_intermediate_mappings = __between_lane_summarization(partition, variant.interaction_points, print_result)
        new_lanes.append(summarized_lane)
        new_mappings.append((summarized_lane.lane_id, new_intermediate_mappings))

    # Check for redundancies
        for i in range(len(new_lanes)):
            for j in range(i+1, len(new_lanes)):
                summary1 = new_lanes[i]
                summary2 = new_lanes[j]
                if(summary1.same_summarization(summary2) or summary1.subsumed_summarization(summary2)):
                    if(print_result):
                        print("----")
                        print("Redundancy found, pruning subtree!")
                        print("\n")
                    return None

    current_summarization["Lanes"].extend(new_lanes)
    current_summarization["Mappings"].extend(new_mappings)

    # Recursive call
    if (len(remaining_candidates) == 0):
        if(print_result):
            print("----")
            print("Leaf node reached!")
            print("\n")
        return [current_summarization]

    else:
        result = []
        for candidate in get_partitions(remaining_candidates[0]):
            current_summarization["Candidate"] = candidate
            subtree_result = __branch_on_candidates(variant, remaining_candidates[1:], (current_summarization), level+1, print_result)
            if(subtree_result != None):
                result.extend(subtree_result)
        if(print_result):
            print("\n")
        return result


def within_variant_summarization(variant, print_result = True):
    '''
    Yields all unique valid summarizations of a given variant
    :param variant: The variant that is to be generalized
    :type variant: ExtractedVariant
    :param print_result: Whether or not the print commands should be executed
    :type print_result: Boolean
    :return: A list of all unique valid summarizations of the variant
    :rtype: SummarizedLane
    '''

    # Initialize candidate parameters 
    all_candidates = __get_candidates(variant.lanes, variant.interaction_points)
    first_choice =  get_partitions(all_candidates[0])
    all_summarizations = []
    init_summary = {}
    init_summary["Lanes"] = []
    init_summary["Mappings"] = []

    # Traverse tree of candidates
    for partition in first_choice:
        init_summary["Candidate"] = partition
        subtree_result = __branch_on_candidates(variant, all_candidates[1:], init_summary, 1, print_result)
        if(subtree_result != None):
            all_summarizations.extend(subtree_result)

    # Re-align summarizations
    result = []
    for summarization in all_summarizations:
        result_lanes, result_interaction_points = __re_align_lanes(summarization["Lanes"], __merge_interaction_mappings(summarization["Mappings"]), print_result)
        result.append(SVD.SummarizedVariant(result_lanes, variant.object_types, result_interaction_points, variant.frequency))
        result[-1].encode_lexicographically()

        if(print_result):
            print(result[-1])
            print("-------------------")

    return result


def __between_lane_summarization(lanes, interactions, print_result):
    '''
    Yields a generic summarizations of lanes of the same object type
    :param lanes: The lanes of the same object type that need summarization
    :type lanes: List of Variant Lanes
    :param interactions: The interaction points of the variant of the lanes
    :type interactions: List of Interaction Points
    :param print_result: Whether or not the print commands should be executed
    :type print_result: Boolean
    :return: The summarization of the given lanes
    :rtype: SuperLane
    '''
    common_activities = __max_order_preserving_common_activities(lanes)

    # Initializing the values for the summarized lanes object
    elements = []
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
        interval_elements, interval_length = __apply_patterns(interval_subprocesses, current_horizontal_index, print_result)
        elements.extend(interval_elements)
        current_horizontal_index += interval_length
                     
        # Add the common activity to the elements of the summarized lane
        if(print_result):
            print("\n")
            print("Adding the common activity: " + str(list(common_activities.keys())[i][1]))

        # Checks if the common activity is an interaction point
        is_interacting_activity, interaction_point = IED.is_interaction_point(interactions, [lane.lane_id for lane in lanes][0], list(common_activities.values())[i][0])        
        #if(is_interacting_activity and all(elem in [lane.lane_id for lane in lanes] for elem in interaction_point.interaction_lanes)):
            #elements.append(SVD.CommonConstruct(list(common_activities.keys())[i][1], len(lanes), current_horizontal_index))
        #else:
        if(print_result):
            print("This is an interaction point: " + str(is_interacting_activity))

        if (is_interacting_activity):
            for index in (set(list(common_activities.values())[i])):
                new_interaction_points_mapping[(index, str(interaction_point.interaction_lanes))] = current_horizontal_index
            elements.append(SVD.InteractionConstruct(list(common_activities.keys())[i][1], len(lanes), current_horizontal_index))
        else:
            elements.append(SVD.CommonConstruct(list(common_activities.keys())[i][1], len(lanes), current_horizontal_index))
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
    interval_elements, interval_length = __apply_patterns(interval_subprocesses, current_horizontal_index, print_result)
    elements.extend(interval_elements)
    current_horizontal_index += interval_length
        
    cardinality = "1"
    if len(lanes)>1:
        cardinality = "n"
        
    return SVD.SuperLane(lane_id, lane_name, object_type, elements, cardinality), new_interaction_points_mapping


def __apply_patterns(activities, start_index, print_result):
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
        return [], 0
    
    if(print_result):
            print("\n")
            print("Applying a pattern to the elements: ")
            print(activities)
            
    elements = []
    length = 0
    
    # Determine choices and their frequencies
    choice_activities = [activity_list[0] for activity_list in activities]
    longest_option = max(choice_activities, key=len)
    length = len(longest_option)
    unique_choice_sequences = [list(sequence) for sequence in set(tuple(sequence) for sequence in choice_activities) if list(sequence) != []]
    unique_choice_sequences.sort()
    frequencies = []
    for choice in unique_choice_sequences:
        frequency = 0
        for sequence in choice_activities:
            if (choice == sequence):
                frequency += 1
        frequencies.append(frequency)

    unique_choice_sequences_elements = []
    for i in range(len(unique_choice_sequences)):
        choice_elements = []
        position = start_index
        for activity in unique_choice_sequences[i]:
            choice_elements.append(SVD.CommonConstruct(activity, frequencies[i], position))
            position += 1
        unique_choice_sequences_elements.append(choice_elements)

        
    # Adding Construct
    if([] in choice_activities):
        if(print_result):

        # Output printing
            print("\n")
            print("Adding a optional choice element between the following sequences.")
            print(unique_choice_sequences)

        elements.append(SVD.OptionalConstruct(unique_choice_sequences_elements, start_index, start_index+length-1))

    else:

        if(print_result):
            # Output printing
            print("\n")
            print("Adding a choice element between the following sequences.")
            print(unique_choice_sequences)

        elements.append(SVD.ChoiceConstruct(unique_choice_sequences_elements, start_index, start_index+length-1))
            
    return elements, length


def __merge_interaction_mappings(mappings):
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
            for k in range(i+1, len(mappings)):
                if(key in list(mappings[k][1].keys())):
                    positions[mappings[k][0]] = mappings[k][1][key]
            if(len(positions.keys()) > 1 and key not in merged_mappings.keys()):
                merged_mappings[key] = positions
    
    return merged_mappings        
            

def __re_align_lanes(lanes, mappings, print_result):
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
        lanes = [lane for lane in aligned_lanes if lane.lane_id in list(earliest_interaction_point[1].keys())]
        if(print_result):
            print("We have an interaction at the following points in the interacting lanes: " + str(earliest_interaction_point[1]))
        element = lanes[0].get_element(earliest_interaction_point[1][lanes[0].lane_id])
        name = element.activity
        types = set([lane.object_type for lane in lanes])
                
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
                element = lane.get_element(current_position)
                lane.shift_lane(element, offset)
                if(print_result):
                    print("We have shifted lane " + lane.lane_name + " by " + str(offset) + " starting from activity " + str(element) + ".")
                        
                        
                # Update all values in the dictionary accordingly
                for key in updated_mappings.keys():
                    if(lane.lane_id in updated_mappings[key].keys() and updated_mappings[key][lane.lane_id]>=current_position):
                        updated_mappings[key][lane.lane_id] += offset
                        
        del updated_mappings[earliest_interaction_point[0]]
        updated_interaction_points.append(IED.InteractionPoint(name, [lane.lane_id for lane in lanes], types, position))
        
    return aligned_lanes, updated_interaction_points


def __max_order_preserving_common_activities(lanes):
    '''
    Extracts the longest sequence of activities found in all lanes, preserving their order
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
            
            if (all(base_lane[j] in lane for lane in comparison)):

                #Create result tuple
                indices_of_lane = ()
                indices_of_lane = indices_of_lane + (base_indices[j],)
                
                # Add the corresponding index for each other variant and adjust the lists
                for k in range(len(comparison)):
                    indices_of_lane = indices_of_lane + (indices[k][comparison[k].index(base_lane[j])],)
                    indices[k] = indices[k][comparison[k].index(base_lane[j])+1:]
                    comparison[k] = comparison[k][comparison[k].index(base_lane[j])+1:]
                
                duplicate_key_set = [key for key in list(set.keys()) if key[1] == base_lane[j]]
                if (len(duplicate_key_set) > 0):
                    maximum = max([key[0] for key in duplicate_key_set])
                    set[maximum+1, base_lane[j]] = (indices_of_lane)
                else:
                    set[0, base_lane[j]] = (indices_of_lane)
        activity_sets.append(set)
        
    # Return the maximal list of activities for optimality
    return max(activity_sets, key=len)


def __partition(collection):
    if len(collection) == 1:
        yield [collection]
        return

    first = collection[0]
    for smaller in __partition(collection[1:]):
        for n, subset in enumerate(smaller):
            yield smaller[:n] + [[first] + subset]  + smaller[n+1:]
        yield [ [ first ] ] + smaller

def get_partitions(candidate):
    partitions = []
    for n, p in enumerate(__partition(list(candidate)), 1):
        partitions.append(p)
    return(partitions)