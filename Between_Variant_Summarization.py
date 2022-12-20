import Super_Variant_Definition as SVD
import Super_Variant_Visualization as WVV
import Within_Variant_Summarization as WVS
import Input_Extraction_Definition as IED

def join_super_variants(summarization1, summarization2, print_result = True):
    import copy
    WVV.visualize_super_variant(summarization1)
    WVV.visualize_super_variant(summarization2)
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

    result_lanes, result_interaction_points = __re_align_lanes(intermediate_lanes, __merge_interactions(WVS.__merge_interaction_mappings(intermediate_mappings)), print_result)
    super_variant = SVD.SuperVariant(summarization1.id + summarization2.id, result_lanes, summarization1.object_types.union(summarization2.object_types), result_interaction_points, summarization1.frequency + summarization2.frequency)
    super_variant.encode_lexicographically()
    print(super_variant)
    WVV.visualize_super_variant(super_variant)
    return super_variant

def __merge_interactions(merged_interactions):
    result_interactions = dict()
    for key1 in merged_interactions.keys():
        exists = False
        for key2 in result_interactions.keys():
            if (merged_interactions[key1] == result_interactions[key2]):
                exists = True
        if(not exists):
            result_interactions[key1] = merged_interactions[key1]

    return result_interactions


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
        if(isinstance(element, SVD.GeneralChoiceStructure)):
            name = "Choice"
        else:
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


def optional_super_lane(summarization, lane, first):
    
    elements = []
    object_type = lane.object_type
    lane_name = lane.object_type + " i"
    lane_id = tuple(lane.lane_id)
    cardinality = lane.cardinality

    new_interaction_points_mapping = {}
    current_horizontal_index = 0

    for elem in lane.elements:

        if(isinstance(elem, SVD.CommonConstruct) or isinstance(elem, SVD.InteractionConstruct)):
            activity = elem.activity
            frequency = elem.frequency
            if(isinstance(elem, SVD.CommonConstruct)):
                elements.append(SVD.CommonConstruct(activity, frequency, current_horizontal_index))
            else:
                elements.append(SVD.InteractionConstruct(activity, frequency, current_horizontal_index))

                current_interaction_point = None
                for interaction_point in summarization.interaction_points:
                    if(interaction_point.index_in_lanes == elem.position and lane.lane_id in interaction_point.interaction_lanes):
                            current_interaction_point = interaction_point
                            break

                if(first):
                    new_interaction_points_mapping[(1, current_interaction_point.index_in_lanes, str(current_interaction_point.interaction_lanes))] = current_horizontal_index
                else:
                    new_interaction_points_mapping[(2, current_interaction_point.index_in_lanes, str(current_interaction_point.interaction_lanes))] = current_horizontal_index

            current_horizontal_index += 1
                
        else:          
            new_choices = []
            length = 0

            for choice in elem.choices:
                index = current_horizontal_index
                new_choice = []
                for c_elem in choice:
                    c_activity = c_elem.activity
                    c_frequency = c_elem.frequency

                    if(isinstance(c_elem, SVD.CommonConstruct)):
                        new_choice.append(SVD.CommonConstruct(c_activity, c_frequency, index))
                    else:
                        new_choice.append(SVD.InteractionConstruct(c_activity, c_frequency, index))

                        current_interaction_point = None
                        for interaction_point in summarization.interaction_points:
                            if(interaction_point.index_in_lanes == c_elem.position and lane.lane_id in interaction_point.interaction_lanes):
                                    current_interaction_point = interaction_point
                                    break

                        if(first):
                            new_interaction_points_mapping[(1, current_interaction_point.index_in_lanes, str(current_interaction_point.interaction_lanes))] = index
                        else:
                            new_interaction_points_mapping[(2, current_interaction_point.index_in_lanes, str(current_interaction_point.interaction_lanes))] = index

                    index += 1
                
                new_choices.append(new_choice)
                length = max(length, len(new_choice))

            if(isinstance(elem, SVD.ChoiceConstruct)):
                elements.append(SVD.ChoiceConstruct(new_choices, current_horizontal_index, current_horizontal_index + length-1))
            else:
                elements.append(SVD.ChoiceConstruct(new_choices, current_horizontal_index, current_horizontal_index + length-1))

            current_horizontal_index += length


    return SVD.OptionalSuperLane(lane_id, lane_name, object_type, elements, cardinality), new_interaction_points_mapping



def join_super_lanes(summarization1, summarization2, lane1, lane2, print_result = True):
    return __between_lane_summarization(summarization1, summarization2, lane1, lane2, lane1.get_realizations(), lane2.get_realizations(), print_result)


def __between_lane_summarization(summarization1, summarization2, o_lane1, o_lane2, lanes1, lanes2, print_result):

    import copy
    # Initializing the values for the summarized lanes object
    elements = []
    object_type = o_lane1.object_type
    lane_name = o_lane1.object_type + " i"
    lane_id = (o_lane1.lane_id, o_lane2.lane_id)
    if(o_lane1.cardinality == o_lane2.cardinality):
        cardinality = o_lane1.cardinality
    else:
        cardinality = "1..n"
    
    new_interaction_points_mapping = {}
    current_horizontal_index = 0

    all_lanes = []
    for lane in lanes1:
        all_lanes.append((1, lane, len(lane.elements)))
    for lane in lanes2:
        all_lanes.append((2, lane, len(lane.elements)))

    longest_common_sequence, value = __get_longest_common_subsequence(copy.deepcopy(all_lanes))
    start_indices = [0 for lane in all_lanes]

    for common_element in longest_common_sequence:

        # Determine all interval subprocesses and summarize them
        interval_subprocesses = []
        for j in range(len(all_lanes)):
            start_index = start_indices[j]
            end_index = (common_element[1][j][2])
            if(end_index - start_index >= 0):
                interval_subprocesses.append((all_lanes[j][0], (all_lanes[j][1].elements[start_index:end_index])))
            else:
                interval_subprocesses.append((all_lanes[j][0],[]))
        
        # Add summarized subprocess to elements
        interval_elements, interval_length, interval_mapping = __apply_patterns(interval_subprocesses, current_horizontal_index, summarization1, summarization2, o_lane1, o_lane2, print_result)
        elements.extend(interval_elements)
        new_interaction_points_mapping.update(interval_mapping)
        current_horizontal_index += interval_length
                     
        # Add the common activity to the elements of the summarized lane
        if(print_result):
            print("\n")
            print("Adding the common activity: " + str(common_element[0]))

        # Get frequency of the event
        frequency1 = 0 
        frequency2 = 0
        for i in range(len(all_lanes)):
            if(all_lanes[i][0] == 1 and frequency1 == 0):
                frequency1 = all_lanes[i][1].elements[common_element[1][i][2]].frequency
            elif(all_lanes[i][0] == 2 and frequency2 == 0):
                frequency2 = all_lanes[i][1].elements[common_element[1][i][2]].frequency


        
        # Checks if the common activity is an interaction point
        is_interacting_activity = isinstance(all_lanes[0][1].elements[common_element[1][0][2]], SVD.InteractionConstruct)   

        if(print_result):
            print("This is an interaction point: " + str(is_interacting_activity))

        if (is_interacting_activity):

            interaction_point1 = None
            interaction_point2 = None
            for i in range(len(all_lanes)):
                if(all_lanes[i][0] == 1):
                    element = all_lanes[i][1].elements[common_element[1][i][2]]
                    for interaction_point in summarization1.interaction_points:
                        if(interaction_point.index_in_lanes == element.position and o_lane1.lane_id in interaction_point.interaction_lanes):
                            interaction_point1 = interaction_point
                            break
                elif(all_lanes[i][0] == 2):
                    element = all_lanes[i][1].elements[common_element[1][i][2]]
                    for interaction_point in summarization2.interaction_points:
                        if(interaction_point.index_in_lanes == element.position and o_lane2.lane_id in interaction_point.interaction_lanes):
                            interaction_point2 = interaction_point
                            break

            new_interaction_points_mapping[(1, interaction_point1.index_in_lanes, str(interaction_point1.interaction_lanes))] = current_horizontal_index
            new_interaction_points_mapping[(2, interaction_point2.index_in_lanes, str(interaction_point2.interaction_lanes))] = current_horizontal_index

            elements.append(SVD.InteractionConstruct(common_element[0], frequency1 + frequency2, current_horizontal_index))

        else:
            elements.append(SVD.CommonConstruct(common_element[0], frequency1 + frequency2, current_horizontal_index))

        current_horizontal_index += 1
        
        # Update indices for the next iteration
        for i in range(len(all_lanes)):
            start_indices[i] = common_element[1][i][2] + 1


    # Determine all interval subprocesses and summarize them
    interval_subprocesses = []
    for j in range(len(all_lanes)):
        start_index = start_indices[j]
        end_index = len(all_lanes[j][1].elements)
        if(end_index - start_index >= 0):
            interval_subprocesses.append((all_lanes[j][0], (all_lanes[j][1].elements[start_index:end_index])))
        else:
            interval_subprocesses.append((all_lanes[j][0],[]))
        
    # Add summarized subprocess to elements
    interval_elements, interval_length, interval_mapping = __apply_patterns(interval_subprocesses, current_horizontal_index, summarization1, summarization2, o_lane1, o_lane2, print_result)
    elements.extend(interval_elements)
    new_interaction_points_mapping.update(interval_mapping)
    current_horizontal_index += interval_length

    return SVD.SuperLane(lane_id, lane_name, object_type, elements, cardinality), new_interaction_points_mapping



def __apply_patterns(interval_subprocesses, start_index, summarization1, summarization2, o_lane1, o_lane2, print_result):

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
    choice_activities = dict()

    for elements in interval_subprocesses:
        choice = []
        frequency = 0
        lane_id = elements[0]
        for i in range(len(elements[1])):

            if(isinstance(elements[1][i], SVD.InteractionConstruct)):
                if (lane_id == 1):
                    interaction_point1 = None
            
                    for interaction_point in summarization1.interaction_points:
                        if(interaction_point.index_in_lanes == elements[1][i].position and o_lane1.lane_id in interaction_point.interaction_lanes):
                            interaction_point1 = interaction_point
                            break

                    new_mapping[(1, interaction_point1.index_in_lanes, str(interaction_point1.interaction_lanes))] = start_index + i

                else:
                    interaction_point2 = None
            
                    for interaction_point in summarization2.interaction_points:
                        if(interaction_point.index_in_lanes == elements[1][i].position and o_lane2.lane_id in interaction_point.interaction_lanes):
                            interaction_point2 = interaction_point
                            break

                    new_mapping[(2, interaction_point2.index_in_lanes, str(interaction_point2.interaction_lanes))] = start_index + i


            choice.append(elements[1][i].activity)
            frequency = elements[1][i].frequency

        if(str(choice) in choice_activities.keys()):
            current_frequency = choice_activities[str(choice)][1]
            elements = choice_activities[str(choice)][0]
            choice_activities[str(choice)] = (elements, current_frequency + frequency)
        else:
            choice_activities[str(choice)] = (choice, frequency)
            

    unique_choices = [choice for choice in choice_activities.values() if choice[0] != []]
    unique_choices.sort(key=lambda a: a[0])
    frequencies = [choice[1] for choice in unique_choices]
    unique_choice_sequences = [choice[0] for choice in unique_choices]

    longest_option = max(unique_choice_sequences, key=len)
    length = len(longest_option)

    unique_choice_sequences_elements = []
    for i in range(len(unique_choice_sequences)):
        choice_elements = []
        position = start_index
        for activity in unique_choice_sequences[i]:
            choice_elements.append(SVD.CommonConstruct(activity, frequencies[i], position))
            position += 1
        unique_choice_sequences_elements.append(choice_elements)
        
    # Adding Construct
    if(str([]) in choice_activities.keys()):
        if(print_result):

        # Output printing
            print("\n")
            print("Adding a optional choice element between the following sequences.")
            print(unique_choice_sequences)

        returned_elements.append(SVD.OptionalConstruct(unique_choice_sequences_elements, start_index, start_index+length-1))

    else:

        if(print_result):
            # Output printing
            print("\n")
            print("Adding a choice element between the following sequences.")
            print(unique_choice_sequences)

        returned_elements.append(SVD.ChoiceConstruct(unique_choice_sequences_elements, start_index, start_index+length-1))
            
    return returned_elements, length, new_mapping



def __get_longest_common_subsequence(lanes):

    base_element = lanes[0][1].elements[lanes[0][2]-1]

    if any([lane[2] == 0 for lane in lanes]):
        return [], 0 

    elif(all((type(lane[1].elements[lane[2]-1]) == type(base_element) and lane[1].elements[lane[2]-1].activity == base_element.activity) for lane in lanes)):
        
        recursive_result, recursive_value = __get_longest_common_subsequence([(lane[0], lane[1], lane[2]-1) for lane in lanes])
        indices = [(lane[0], lane[1], lane[2]-1) for lane in lanes]
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




def join_super_lanes_recursive(summarization1, summarization2, id1, id2, lane1_elements, lane2_elements, current_position):

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
