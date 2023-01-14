import Super_Variant_Definition as SVD
import Input_Extraction_Definition as IED

def __inter_lane_summarization(lanes, interactions, print_result):


    elements = []
    new_interaction_points_mapping = {}
    current_horizontal_index = 0

    base_lanes = [lane.remove_non_common_elements() for lane in lanes]
    realization_lanes = [lane.get_realizations() for lane in lanes]

    all_lanes = []
    for i in range(len(realization_lanes)):
        for realization in realization_lanes[i]:
            all_lanes.append((i, realization, len(realization.elements)))

    base_lanes_indexed = []
    for i in range(len(base_lanes)):
            base_lanes_indexed.append((i, base_lanes[i], len(base_lanes[i].elements)))

    longest_common_sequence, length = __get_longest_common_subsequence(base_lanes_indexed)
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
                    if(elem.position >= last_positions[index] and elem.position < current_positions[index]):
                        subprocess.append(elem)
                interval_subprocesses.append((all_lanes[j][0], subprocess))
            else:
                interval_subprocesses.append((all_lanes[j][0],[]))
    
        
        # Add summarized subprocess to elements
        interval_elements, interval_length, interval_mapping = __apply_patterns(interval_subprocesses, current_horizontal_index, interactions, base_lanes, print_result)
        elements.extend(interval_elements)
        new_interaction_points_mapping.update(interval_mapping)
        current_horizontal_index += interval_length
                     
        # Add the common activity to the elements of the summarized lane
        if(print_result):
            print("\n")
            print("Adding the common activity: " + str(common_element[0]))

        # Get frequency of the event
        element_frequency = 0
        for i in range(len(base_lanes)):
            element_frequency += base_lanes[i].get_element(common_element[1][i][2]).frequency

        
        # Checks if the common activity is an interaction point
        is_interacting_activity = False
        for i in range(len(base_lanes)):
            is_interacting_activity = is_interacting_activity or isinstance(base_lanes[i].get_element(common_element[1][i][2]), SVD.InteractionConstruct)

        if(print_result):
            print("This is an interaction point: " + str(is_interacting_activity))

        if (is_interacting_activity):

            interaction_points = []
  
            for i in range(len(base_lanes)):
                element = base_lanes[i].get_element(common_element[1][i][2])
                interaction_point = None
                for interaction_point in interactions[i]:
                    if(interaction_point.index_in_lanes == element.position and base_lanes[i].lane_id in interaction_point.interaction_lanes):
                        interaction_point = interaction_point
                        break
                interaction_points.append(interaction_point)

            for i in range(len(interaction_points)):
                new_interaction_points_mapping[(i, interaction_points[i].index_in_lanes, str(interaction_points[i].interaction_lanes))] = (0,current_horizontal_index)

            elements.append(SVD.InteractionConstruct(common_element[0], element_frequency, current_horizontal_index))

        else:
            elements.append(SVD.CommonConstruct(common_element[0], element_frequency, current_horizontal_index))

        current_horizontal_index += 1
        
        # Update indices for the next iteration
        for i in range(len(last_positions)):
            last_positions[i] = current_positions[i] + 1

    
    for i in range(len(current_positions)):
        current_positions[i] = base_lanes[i].elements[-1].position + 1

    # Determine all interval subprocesses and summarize them
    interval_subprocesses = []
    for j in range(len(all_lanes)):
        index = all_lanes[j][0]
        if(current_positions[index] - last_positions[index] >= 0):
            subprocess = []
            for elem in all_lanes[j][1].elements:
                if(elem.position >= last_positions[index] and elem.position < current_positions[index]):
                    subprocess.append(elem)
            interval_subprocesses.append((all_lanes[j][0], subprocess))
        else:
            interval_subprocesses.append((all_lanes[j][0],[]))
        
    # Add summarized subprocess to elements
    interval_elements, interval_length, interval_mapping = __apply_patterns(interval_subprocesses, current_horizontal_index, interactions, base_lanes, print_result)
    elements.extend(interval_elements)
    new_interaction_points_mapping.update(interval_mapping)
    current_horizontal_index += interval_length

    return elements, new_interaction_points_mapping



def __apply_patterns(interval_subprocesses, start_index, interactions, base_lanes, print_result):

    if sum([len(elements[1]) for elements in interval_subprocesses]) == 0:
        return [], 0, dict()
    
    new_mapping = dict()
    if(print_result):
            print("\n")
            print("Applying a pattern to the elements: ")
            for elements in interval_subprocesses:
                print(elements[1])
            
    returned_elements = []
    length = 0

    # Determine choices and their frequencies
    choices = []
    frequencies = []
    is_optional = False

    for elements in interval_subprocesses:
        position = start_index
        choice = []
        frequency = 0
        lane_id = elements[0]
        current_mappings = dict()

        for i in range(len(elements[1])):

            if(isinstance(elements[1][i], SVD.InteractionConstruct)):
                
                interaction_point = None
            
                for interaction_point in interactions[elements[0]]:
                    if(interaction_point.index_in_lanes == elements[1][i].position and base_lanes[elements[0]].lane_id in interaction_point.interaction_lanes):
                        interaction_point = interaction_point
                        break

                current_mappings[(elements[0], interaction_point.index_in_lanes, str(interaction_point.interaction_lanes))] = start_index + i

                choice.append(SVD.InteractionConstruct(elements[1][i].activity, elements[1][i].frequency, position))
            else:
                choice.append(SVD.CommonConstruct(elements[1][i].activity, elements[1][i].frequency, position))

            position += 1
            frequency = elements[1][i].frequency

        if(choice == []):
            is_optional = True

        else:
            duplicate = False
            for i in range(len(choices)):
                equal = True
                for j in range(len(choices[i])):
                    equal = equal and ((type(choices[i][j]) == type(choice[j])) and (choices[i][j].activity == choice[j].activity))

                    if(not equal):
                        break

                if(equal):
                    duplicate = True
                    frequencies[i] += frequency
                    for j in range(len(choices[i])):
                        choices[i][j].frequency += choice[j].frequency
                    for key in current_mappings.keys():
                        new_mapping[key] = (i,current_mappings[key])
                    break

            if(not duplicate):
                frequencies.append(frequency)
                current_index = len(choices)
                choices.append(choice)
                for key in current_mappings.keys():
                    new_mapping[key] = (current_index,current_mappings[key])


    longest_option = max(choices, key=len)
    length = len(longest_option)
        
    # Adding Construct
    if(is_optional):
        if(print_result):

        # Output printing
            print("\n")
            print("Adding a optional choice element between the following sequences.")
            for choice in choices:
                for elem in choice:
                    print(elem)
                print("----------")

        returned_elements.append(SVD.OptionalConstruct(choices, start_index, start_index + length - 1))

    else:

        if(print_result):
            # Output printing
            print("\n")
            print("Adding a choice element between the following sequences.")
            for choice in choices:
                for elem in choice:
                    print(elem)
                print("----------")

        returned_elements.append(SVD.ChoiceConstruct(choices, start_index, start_index + length - 1))
            
    return returned_elements, length, new_mapping



def __get_longest_common_subsequence(lanes):

    base_element = lanes[0][1].elements[lanes[0][2]-1]

    if any([lane[2] == 0 for lane in lanes]):
        return [], 0 

    elif(all((type(lane[1].elements[lane[2]-1]) == type(base_element) and lane[1].elements[lane[2]-1].activity == base_element.activity) for lane in lanes)):
        
        recursive_result, recursive_value = __get_longest_common_subsequence([(lane[0], lane[1], lane[2]-1) for lane in lanes])
        indices = [(lane[0], lane[1], lane[1].elements[lane[2]-1].position) for lane in lanes]
        return recursive_result + [(base_element.activity, indices)], recursive_value + 1

    else:
        maximum_value = -1
        maximum_result = []

        for i in range(1, pow(2,len(lanes))-1):
            binary = list(bin(i)[2:].zfill(len(lanes)))
            recursive_call_lanes = []
            for i in range(len(lanes)):
                if (binary[i] == '1'):
                    recursive_call_lanes.append((lanes[i][0], lanes[i][1], lanes[i][2]-1))
                else:
                    recursive_call_lanes.append(lanes[i])

            recursive_result, recursive_value = __get_longest_common_subsequence(recursive_call_lanes)

            if (recursive_value > maximum_value):
                maximum_value = recursive_value
                maximum_result = recursive_result

        return maximum_result, maximum_value


def __merge_interactions(merged_interactions):
    print(merged_interactions)
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
        earliest_interaction_point = min(updated_mappings.items(), key=lambda x: list(list(x[1].values())[1]))
        lanes = [lane for lane in aligned_lanes if lane.lane_id in list(earliest_interaction_point[1].keys())]
        if(print_result):
            print("We have an interaction at the following points in the interacting lanes: " + str(earliest_interaction_point[1]))
        
        types = set([lane.object_type for lane in lanes])
        element = lanes[0].get_element(updated_mappings[earliest_interaction_point[0]][lanes[0].lane_id][1])
        if(type(element) == SVD.ChoiceConstruct or type(element) == SVD.OptionalConstruct):
            for elem in element.choices[updated_mappings[earliest_interaction_point[0]][lanes[0].lane_id][0]]:
                if (elem.position == updated_mappings[earliest_interaction_point[0]][lanes[0].lane_id][1]):
                    activity_label = elem.activity
                    break
        else:
            activity_label = element.activity
        all_positions = [value[1] for value in earliest_interaction_point[1].values()]

        if(len(set(all_positions)) == 1):
            if(print_result):
                print("No alignment required.")
            position = all_positions[0]
                    
        else: 

            target_position = max(all_positions)
            position = target_position
            
            for lane in lanes:
                
                # Shift indices by the offset
                original_lane = copy.deepcopy(lane)
                current_position = updated_mappings[earliest_interaction_point[0]][lane.lane_id][1]
                choice_id = updated_mappings[earliest_interaction_point[0]][lane.lane_id][0]
                offset = target_position - current_position
                partial_shift, element_index, previous_start_position, previous_end_position = lane.shift_lane_exact(current_position, offset, choice_id)
                
                if(print_result and not partial_shift):
                    print("We have shifted lane " + lane.lane_name + " by " + str(offset) + " starting from element " + str(original_lane.elements[element_index]) + ".")

                if(print_result and partial_shift):
                    print("We have shifted lane " + lane.lane_name + " by " + str(offset) + " starting with a partial shift in option " + str(choice_id) + " of the element " + str(original_lane.elements[element_index]) + ".")
                        
                # Update all values in the dictionary accordingly
                if(offset == 0):
                    continue 

                for key in updated_mappings.keys():

                    if(lane.lane_id in updated_mappings[key].keys() and updated_mappings[key][lane.lane_id][1]>=current_position):
                        if(not partial_shift):
                            tuple = updated_mappings[key][lane.lane_id]
                            updated_mappings[key][lane.lane_id]= (tuple[0], tuple[1] + offset)

                        else:
                            elem = original_lane.get_element(updated_mappings[key][lane.lane_id][1])

                            if(type(elem) == SVD.InteractionConstruct):
                                tuple = updated_mappings[key][lane.lane_id]
                                updated_mappings[key][lane.lane_id]= (tuple[0], tuple[1] + offset)

                            elif(isinstance(elem,SVD.GeneralChoiceStructure)):
                                if(updated_mappings[key][lane.lane_id][1] >= previous_start_position and updated_mappings[key][lane.lane_id][1] <= previous_end_position):
                                    if(updated_mappings[key][lane.lane_id][0] == choice_id):
                                        tuple = updated_mappings[key][lane.lane_id]
                                        updated_mappings[key][lane.lane_id]= (tuple[0], tuple[1] + offset)
                                else:
                                    tuple = updated_mappings[key][lane.lane_id]
                                    updated_mappings[key][lane.lane_id]= (tuple[0], tuple[1] + offset)
                        
        del updated_mappings[earliest_interaction_point[0]]
        updated_interaction_points.append(IED.InteractionPoint(activity_label, [lane.lane_id for lane in lanes], types, position))
        
    return aligned_lanes, updated_interaction_points