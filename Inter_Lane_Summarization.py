import Super_Variant_Definition as SVD
import Input_Extraction_Definition as IED

def __inter_lane_summarization(lanes, interactions, print_results, offset = 0, allow_nested_structures = False):
    '''
    Performs the summarization of the given Super Lanes using the set of defined patterns.
    :param lanes: The Super Lanes that should be summarized
    :type lanes: list of type SuperLane
    :param interactions: The sets of interaction points corresponding to the involved Super Lanes
    :type interactions: list
    :param print_results: Whether the results should be output in the console
    :type print_results: bool
    :param offset: The starting index of the horizontal positions
    :type offset: int
    :param allow_nested_structures: Whether the choice structures are allowed to be nested
    :type allow_nested_structures: bool
    :return: The summarizing elements, a mapping from original interaction positions to the new positions
    :rtype: list of type SummarizationElement, dict
    '''
    elements = []
    new_interaction_points_mapping = {}
    current_horizontal_index = offset

    base_lanes = [lane.remove_non_common_elements() for lane in lanes]
    realization_lanes = [lane.get_realizations() for lane in lanes]

    all_lanes = []
    for i in range(len(realization_lanes)):
        for realization in realization_lanes[i]:
            all_lanes.append((i, realization, len(realization.elements)))

    base_lanes_indexed = []
    for i in range(len(base_lanes)):
            base_lanes_indexed.append((i, base_lanes[i], len(base_lanes[i].elements)))

    longest_common_sequence, length, number_of_interactions = __get_longest_common_subsequence(base_lanes_indexed)
    last_positions = [0 for lane in base_lanes]

    for common_element in longest_common_sequence:

        current_positions = []
        for i in range(len(common_element[1])):
            current_positions.append(common_element[1][i][2])


        # Determine all interval subprocesses and summarize them
        interval_subprocesses = []
        for j in range(len(all_lanes)):
            index = all_lanes[j][0]
            if(current_positions[index] - last_positions[index] >= 0):
                subprocess = []
                for elem in all_lanes[j][1].elements:
                    if(elem.index >= last_positions[index] and elem.index < current_positions[index]):
                        subprocess.append(elem)
                interval_subprocesses.append((all_lanes[j][0], subprocess))
            else:
                interval_subprocesses.append((all_lanes[j][0],[]))
    
        
        # Add summarized subprocess to elements
        interval_elements, interval_length, interval_mapping = __apply_patterns(interval_subprocesses, current_horizontal_index, interactions, base_lanes, print_results, allow_nested_structures)
        elements.extend(interval_elements)
        new_interaction_points_mapping.update(interval_mapping)
        current_horizontal_index += interval_length
                     
        # Add the common activity to the elements of the summarized lane
        if(print_results):
            print("\n")
            print("Adding the common activity: " + str(common_element[0]))

        # Get frequency of the event
        element_frequency = 0
        for i in range(len(base_lanes)):
            element_frequency += base_lanes[i].get_element(common_element[2][i][2]).frequency
        element_frequency = element_frequency / len(base_lanes)

        
        # Checks if the common activity is an interaction point
        is_interacting_activity = False
        for i in range(len(base_lanes)):
            is_interacting_activity = is_interacting_activity or isinstance(base_lanes[i].get_element(common_element[2][i][2]), SVD.InteractionConstruct)

        if(print_results):
            print("This is an interaction point: " + str(is_interacting_activity))

        if (is_interacting_activity):

            interaction_points = []
  
            for i in range(len(base_lanes)):
                element = base_lanes[i].get_element(common_element[2][i][2])
                is_interacting_activity, interaction_point = IED.is_interaction_point(interactions[i], base_lanes[i].lane_id, element.position)
                interaction_points.append(interaction_point)

            for i in range(len(interaction_points)):
                new_interaction_points_mapping[(i, str([str(position) for position in interaction_points[i].exact_positions]), str(interaction_points[i].interaction_lanes))] = IED.BasePosition(0, current_horizontal_index)

            elements.append(SVD.InteractionConstruct(common_element[0], element_frequency, IED.BasePosition(0, current_horizontal_index), current_horizontal_index))

        else:
            elements.append(SVD.CommonConstruct(common_element[0], element_frequency, IED.BasePosition(0, current_horizontal_index), current_horizontal_index))

        current_horizontal_index += 1
        
        # Update indices for the next iteration
        for i in range(len(last_positions)):
            last_positions[i] = current_positions[i] + 1


    # Determine all interval subprocesses and summarize them
    interval_subprocesses = []
    for j in range(len(all_lanes)):
        index = all_lanes[j][0]
        current_position = all_lanes[j][1].elements[-1].index + 1
        if(current_position - last_positions[index] >= 0):
            subprocess = []
            for elem in all_lanes[j][1].elements:
                if(elem.index >= last_positions[index] and elem.index < current_position):
                    subprocess.append(elem)
            interval_subprocesses.append((all_lanes[j][0], subprocess))
        else:
            interval_subprocesses.append((all_lanes[j][0],[]))

    # Add summarized subprocess to elements
    interval_elements, interval_length, interval_mapping = __apply_patterns(interval_subprocesses, current_horizontal_index, interactions, base_lanes, print_results, allow_nested_structures)
    elements.extend(interval_elements)
    new_interaction_points_mapping.update(interval_mapping)
    current_horizontal_index += interval_length

    return elements, new_interaction_points_mapping


#TODO
def __apply_patterns(interval_subprocesses, start_index, interactions, base_lanes, print_results, allow_nested_structures):
    '''
    Applies the defined patterns "Exclusive Choice Pattern" and "Optional Pattern" to the extracted subsequences of the initial Super Lanes between their common activities.
    :param interval_subprocesses: The extracted subprocess for each Super Lane between a pair of common activities
    :type interval_subprocesses: list
    :param interactions: The sets of interaction points corresponding to the involved Super Lanes
    :type interactions: list
    :param base_lanes: The set of Super Lanes with only the corresponding common and interaction elements
    :type base_lanes: list of type SuperLanes
    :param print_results: Whether or not the print commands should be executed
    :type print_results: bool
    :param allow_nested_structures: Whether the choice structures are allowed to be nested
    :type allow_nested_structures: bool
    :return: An element summarizing the extracted subprocesses for each initial Super Lane, the length of the element, the mapping from original interaction points to their positions in the element
    :rtype: SummarizationElement, int, dict
    '''
    import copy
    if sum([len(elements[1]) for elements in interval_subprocesses]) == 0:
        return [], 0, dict()
    
    new_mapping = dict()
    if(print_results):
            print("\n")
            print("Applying a pattern to the elements: ")
            for elements in interval_subprocesses:
                print(elements[1])
            
    returned_elements = []
    end_index = start_index

    # Determine choices and their frequencies
    choices = []
    frequencies = []
    is_optional = False
    empty_frequency = 0

    for elements in interval_subprocesses:
        position = start_index
        choice = []
        current_mappings = dict()

        for i in range(len(elements[1])):

            if(isinstance(elements[1][i], SVD.InteractionConstruct)):
                is_interacting_activity, interaction_point = IED.is_interaction_point(interactions[elements[0]], base_lanes[elements[0]].lane_id, elements[1][i].position)
                current_mappings[(elements[0], str([str(position) for position in interaction_point.exact_positions]), str(interaction_point.interaction_lanes))] = start_index + i

                choice.append(SVD.InteractionConstruct(elements[1][i].activity, elements[1][i].frequency, IED.BasePosition(0, position), position))
            else:
                choice.append(SVD.CommonConstruct(elements[1][i].activity, elements[1][i].frequency, IED.BasePosition(0, position), position))

            position += 1

        if(choice == []):
            is_optional = True
            empty_frequency += 1

        else:
            duplicate = False
            for i in range(len(choices)):
                equal = True
                if(len(choices[i][0]) == len(choice)):
                    for j in range(len(choices[i][0])):
                        equal = equal and ((type(choices[i][0][j]) == type(choice[j])) and (choices[i][0][j].activity == choice[j].activity))

                        if(not equal):
                            break
                else:
                    equal = False

                if(equal):
                    duplicate = True
                    cardinality = "n"
                    frequencies[i] += 1
                    choices[i] = (choices[i][0], cardinality, frequencies[i])

                    for key in current_mappings.keys():
                        new_mapping[key] = IED.RecursiveLanePosition(0, IED.BasePosition(i, current_mappings[key]))
                    break

            if(not duplicate):
                frequencies.append(1)
                current_index = len(choices)
                for elem in choice:
                    horizontal_position = elem.position.get_base_index()
                    elem.position = IED.RecursiveLanePosition(0, IED.BasePosition(current_index, horizontal_position))
                    end_index = max(end_index, horizontal_position)
                choices.append(tuple((choice, "1", 1)))
                for key in current_mappings.keys():
                    new_mapping[key] = IED.RecursiveLanePosition(0, IED.BasePosition(current_index, current_mappings[key]))



    for i in range(len(choices)):
        for elem in choices[i][0]:
            elem.frequency = choices[i][2] / len(interval_subprocesses)
        choices[i] = SVD.SuperLane(i, "option " + str(i), base_lanes[0].object_type, choices[i][0], choices[i][1], choices[i][2])


    # TODO Apply recursive summarizations with only 1 nested level and height 1 (number of choices)
   
    # Applying Optional Pattern
    if(is_optional):
        if(print_results):

        # Output printing
            print("\n")
            print("Adding a optional choice element between the following sequences.")
            for choice in choices:
                for elem in choice.elements:
                    print(elem)
                print("----------")
        empty_frequency = empty_frequency / len(interval_subprocesses)
        returned_elements.append(SVD.OptionalConstruct(choices, IED.BasePosition(0, start_index), IED.BasePosition(0, end_index), start_index, end_index, empty_frequency))

    #Applying Exclusive Choice Pattern Pattern
    else:

        if(print_results):
            # Output printing
            print("\n")
            print("Adding a choice element between the following sequences.")
            for choice in choices:
                for elem in choice.elements:
                    print(elem)
                print("----------")

        returned_elements.append(SVD.ChoiceConstruct(choices, IED.BasePosition(0, start_index), IED.BasePosition(0, end_index), start_index, end_index))
            
    return returned_elements, end_index - start_index + 1, new_mapping



def __get_longest_common_subsequence(lanes):
    '''
    Computes the Longest Common Subsequence among the activity sequences of a set of Super Lanes.
    that interaction points between multiple lanes have the same horizontal index
    :param lanes: The lanes among which the longest common subsequence should be computed
    :type lanes: List of type SuperLane
    :return: The Longest Common Subsequence and the corresponding positions in the lanes, the length of the longest_common_subsequence, the number of common interactions in the subsequence
    :rtype: list, int, int
    '''
    base_element = lanes[0][1].elements[lanes[0][2]-1]

    if any([lane[2] == 0 for lane in lanes]):
        return [], 0, 0

    elif(all((type(lane[1].elements[lane[2]-1]) == type(base_element) and lane[1].elements[lane[2]-1].activity == base_element.activity) for lane in lanes)):
        
        recursive_result, recursive_value, recursive_interactions = __get_longest_common_subsequence([(lane[0], lane[1], lane[2]-1) for lane in lanes])
        indices = [(lane[0], lane[1], lane[1].elements[lane[2]-1].index) for lane in lanes]
        positions = [(lane[0], lane[1], lane[1].elements[lane[2]-1].position) for lane in lanes]
        if(type(base_element) == SVD.InteractionConstruct):
            recursive_interactions = recursive_interactions + 1
        return recursive_result + [(base_element.activity, indices, positions)], recursive_value + 1, recursive_interactions

    else:
        maximum_value = -1
        maximum_result = []
        maximum_interaction = -1

        for i in range(1, pow(2,len(lanes))-1):
            binary = list(bin(i)[2:].zfill(len(lanes)))
            recursive_call_lanes = []
            for i in range(len(lanes)):
                if (binary[i] == '1'):
                    recursive_call_lanes.append((lanes[i][0], lanes[i][1], lanes[i][2]-1))
                else:
                    recursive_call_lanes.append(lanes[i])

            recursive_result, recursive_value, recursive_interactions = __get_longest_common_subsequence(recursive_call_lanes)

            if ((recursive_value > maximum_value) or (recursive_value == maximum_value and recursive_interactions > recursive_interactions)):
                maximum_value = recursive_value
                maximum_result = recursive_result
                maximum_interaction = recursive_interactions


        return maximum_result, maximum_value, maximum_interaction


def __merge_interactions(merged_interactions):
    '''
    Merges the interaction point mappings that are at the same position in the final Super Lane.
    :param merged_interactions: The already combined mappings of original interaction points to new indices in the summarized lanes
    :type merged_interactions: dict
    :return: Each interaction point of the final Super Lanes and their current positions in the involved lanes, merged by position
    :rtype: dict
    '''
    result_interactions = dict()
    for key1 in merged_interactions.keys():
        exists = False
        for key2 in result_interactions.keys():
            if (merged_interactions[key1] == result_interactions[key2]):
                exists = True
        if(not exists):
            result_interactions[key1] = merged_interactions[key1]

    return result_interactions

def __merge_interaction_mappings(mappings):
    '''
    Pre-processes the mappings from the summarization for later alignment by merging the mappings for each Super Lane.
    :param mappings: The mappings of original interaction points to new indices in the summarized lanes
    :type mappings: dict
    :return: Each interaction point of the final Super Lanes and their current positions in the involved lanes
    :rtype: dict
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
    Given the summarized Super Lanes and the mappings from original interaction points to new indices, the lanes are aligned according to the interaction points.
    :param lanes: The summarized lanes of the Super Variant
    :type lanes: list of type SuperLane
    :param mappings: The mappings of original interaction points to new indices in the summarized lanes for each lane
    :type mappings: dict
    :param print_result: Whether or not the print commands should be executed
    :type print_result: bool
    :return: The Super Lanes with updated horizontal indices and a list of the corresponding interaction points
    :rtype: list of type SuperLane, list of type InteractionPoint
    '''
    # Initialize variables and return values
    import copy
    import math
    #updated_mappings, aligned_lanes = split_interactions(copy.deepcopy(mappings), copy.deepcopy(lanes))
    updated_mappings, aligned_lanes = copy.deepcopy(mappings), copy.deepcopy(lanes)
    updated_interaction_points = []

    # Align the lanes such that the interaction points have the same horizontal index
    for i in range(len(mappings.keys())):
        earliest_interaction_point = min(updated_mappings.items(), key=lambda x: min([position.get_base_index() for position in x[1].values()]))
        lanes = [lane for lane in aligned_lanes if lane.lane_id in list(earliest_interaction_point[1].keys())]

        if(print_result):
            print("We have an interaction at the following positions in the interacting lanes:")
            for key in earliest_interaction_point[1].keys():
                print(str(key) + ": " + str(earliest_interaction_point[1][key]))
        
        types = set([lane.object_type for lane in lanes])
        element = lanes[0].get_element(updated_mappings[earliest_interaction_point[0]][lanes[0].lane_id])
        activity_label = element.activity

        all_positions = [value for value in earliest_interaction_point[1].values()]

        if(len(set([value.get_base_index() for value in all_positions])) == 1):
            if(print_result):
                print("No alignment required.")
            position = all_positions[0]
            index = position.get_base_index()
            interacting_lanes = list(earliest_interaction_point[1].keys())
            exact_positions = list(earliest_interaction_point[1].values())
                    
        else: 
            target_position = max(all_positions, key = lambda x: x.get_base_index())
            position = target_position
            index = position.get_base_index()

            interacting_lanes = []
            exact_positions = []
            
            for lane in lanes:
                
                # Shift indices by the offset
                current_position = updated_mappings[earliest_interaction_point[0]][lane.lane_id]
                offset = target_position.get_base_index() - current_position.get_base_index()

                interacting_lanes.append(lane.lane_id)
                exact_positions.append(current_position)

                if(offset == 0):
                    continue 

                updated_positions = dict()

                for key in updated_mappings.keys():
                    if(lane.lane_id in updated_mappings[key].keys() and updated_mappings[key][lane.lane_id].get_base_index() >= current_position.get_base_index()):
                        updated_positions[str(updated_mappings[key][lane.lane_id])] = updated_mappings[key][lane.lane_id]

                updated_positions = lane.shift_lane_exact(current_position, offset, copy.deepcopy(updated_positions), current_position)
                
                print("Updated position: " + str(updated_positions[str(current_position)]))
                exact_positions[-1] = updated_positions[str(current_position)]

                
                if(print_result):
                    print("We have shifted lane " + lane.lane_name + " by " + str(offset) + " starting from the element at the position " + str(current_position) + ".")

                # Update all values in the dictionary accordingly
                for key in updated_mappings.keys():
                    if(lane.lane_id in updated_mappings[key].keys() and updated_mappings[key][lane.lane_id].get_base_index() >= current_position.get_base_index()):
                        updated_mappings[key][lane.lane_id] = updated_positions[str(updated_mappings[key][lane.lane_id])]

                        
        
        del updated_mappings[earliest_interaction_point[0]]
        updated_interaction_points.append(IED.InteractionPoint(activity_label, interacting_lanes, types, index, exact_positions))

        
    final_lanes = []
    for lane in aligned_lanes:
        final_lanes.append(copy.deepcopy(lane).shift_activities_up())

    
    return final_lanes, updated_interaction_points



# TODO refine
def split_interactions(mappings, lanes):
    import copy
    new_mappings = copy.deepcopy(mappings)
    duplicates = []

    for i in range(len(list(mappings.keys()))):
        mapping1 = list(mappings.keys())[i]
        duplicate_mappings = dict()
        lane_id = 0

        for key1 in mappings[mapping1].keys():
            position1 = mappings[mapping1][key1]

            for j in range(i+1,len(list(mappings.keys()))):
                mapping2 = list(mappings.keys())[j]

                for key2 in mappings[mapping2].keys():
                    position2 = mappings[mapping2][key2]

                    if(key1 == key2 and position1 == position2):
                         del new_mappings[mapping1]
                         del new_mappings[mapping2]
                         duplicate_mappings[mapping1] = mappings[mapping1]
                         duplicate_mappings[mapping2] = mappings[mapping2]
                         lane_id = key1

        if (len(duplicate_mappings)):
            duplicates.append((duplicate_mappings, lane_id))
    
    new_lanes = []

    for duplicate in duplicates:
        empty_frequency = len(duplicate[0]) - 1
        earliest_interaction_point = min(duplicate[0].items(), key=lambda x: min([position[1] for position in x[1].values()]))
        del duplicate[0][earliest_interaction_point[0]]
  
        for lane in lanes:
            if (lane.lane_id == duplicate[1]):
                positions = earliest_interaction_point[1][duplicate[1]]
                new_lane, new_element = copy.deepcopy(lane).make_optional(positions[1], empty_frequency, positions[0])
                new_mappings[earliest_interaction_point[0]] = earliest_interaction_point[1]
                break
        
        for i in range(len(list(duplicate[0].keys()))):
            current_interaction_point = min(duplicate[0].items(), key=lambda x: list(list(x[1].values())[1]))
            del duplicate[0][current_interaction_point[0]]
            lower_bound = new_element.position_start

            # Problem: Must also consider if it is an entirely different lane 
            #for key in mappings.keys():
                #if(key != earliest_interaction_point[0] and key != current_interaction_point[0]):
                    #if(duplicate[1] in mappings[key].keys() and mappings[key][duplicate[1]][1] > lower_bound):
                        #print(mappings[key])

                        #for key2 in mappings[key].keys():
                            #if(key2 != duplicate[1] and key2 in current_interaction_point[1].keys()):
                                #if(mappings[key][key2][1] < current_interaction_point[1][key2][1]):
                                    #lower_bound = max(mappings[key][duplicate[1]][1] + 1, lower_bound)

            # Update all mappings due to the shift of element positions
            new_position_mapping = (positions[0], lower_bound + 1)
            new_mappings[current_interaction_point[0]] = current_interaction_point[1]
            new_mappings[current_interaction_point[0]][duplicate[1]] = new_position_mapping
            new_lane = new_lane.add_optional_activity(lower_bound + 1, copy.deepcopy(new_element), current_interaction_point[1][duplicate[1]][0])
            for key in new_mappings.keys():
                if(key != earliest_interaction_point[0] and key != current_interaction_point[0]):
                    if(duplicate[1] in mappings[key].keys() and mappings[key][duplicate[1]][1] > lower_bound):
                        old_position = new_mappings[key][duplicate[1]]
                        new_mappings[key][duplicate[1]] = (old_position[0], old_position[1]+1)
                        
        new_lanes.append(new_lane)
        

    for lane in lanes:
        if (lane.lane_id not in [new_lane.lane_id for new_lane in new_lanes]):
            new_lanes.append(lane)

    return new_mappings, new_lanes

