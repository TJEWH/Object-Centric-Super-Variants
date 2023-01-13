import Super_Variant_Definition as SVD

def __inter_lane_summarization(summarization1, summarization2, o_lane1, o_lane2, lanes1, lanes2, print_result):

    # Initializing the values for the summarized lanes object
    elements = []
    object_type = o_lane1.object_type
    lane_name = o_lane1.object_type + " i"
    lane_id = (o_lane1.lane_id, o_lane2.lane_id)
    frequency = o_lane1.frequency + o_lane2.frequency
    if(o_lane1.cardinality == o_lane2.cardinality):
        cardinality = o_lane1.cardinality
    else:
        cardinality = "1..n"
    
    new_interaction_points_mapping = {}
    current_horizontal_index = 0
    base_lane1 = o_lane1.remove_non_common_elements()
    base_lane2 = o_lane2.remove_non_common_elements()

    all_lanes = []
    for lane in lanes1:
        all_lanes.append((1, lane, len(lane.elements)))
    for lane in lanes2:
        all_lanes.append((2, lane, len(lane.elements)))

    longest_common_sequence, value = __get_longest_common_subsequence([(1, base_lane1, len(base_lane1.elements)), (2, base_lane2, len(base_lane2.elements))])
    last_position1 = 0
    last_position2 = 0

    for common_element in longest_common_sequence:

        current_position1 = common_element[1][0][2]
        current_position2 = common_element[1][1][2]

        # Determine all interval subprocesses and summarize them
        interval_subprocesses = []
        for j in range(len(all_lanes)):
            if(all_lanes[j][0] == 1):
                if(current_position1 - last_position1 >= 0):
                    subprocess = []
                    for elem in all_lanes[j][1].elements:
                        if(elem.position >= last_position1 and elem.position < current_position1):
                            subprocess.append(elem)
                    interval_subprocesses.append((all_lanes[j][0], subprocess))
                else:
                    interval_subprocesses.append((all_lanes[j][0],[]))
            else: 
                if(current_position2 - last_position2 >= 0):
                    subprocess = []
                    for elem in all_lanes[j][1].elements:
                        if(elem.position >= last_position2 and elem.position < current_position2):
                            subprocess.append(elem)
                    interval_subprocesses.append((all_lanes[j][0], subprocess))
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
        frequency1 = base_lane1.get_element(common_element[1][0][2]).frequency
        frequency2 = base_lane2.get_element(common_element[1][1][2]).frequency

        
        # Checks if the common activity is an interaction point
        is_interacting_activity = isinstance(base_lane1.get_element(common_element[1][0][2]), SVD.InteractionConstruct)   

        if(print_result):
            print("This is an interaction point: " + str(is_interacting_activity))

        if (is_interacting_activity):

            interaction_point1 = None
            interaction_point2 = None

            element1 = base_lane1.get_element(common_element[1][0][2])
            for interaction_point in summarization1.interaction_points:
                if(interaction_point.index_in_lanes == element1.position and o_lane1.lane_id in interaction_point.interaction_lanes):
                    interaction_point1 = interaction_point
                    break

            element2 = base_lane2.get_element(common_element[1][1][2])
            for interaction_point in summarization2.interaction_points:
                if(interaction_point.index_in_lanes == element2.position and o_lane2.lane_id in interaction_point.interaction_lanes):
                    interaction_point2 = interaction_point
                    break

            new_interaction_points_mapping[(1, interaction_point1.index_in_lanes, str(interaction_point1.interaction_lanes))] = (0,current_horizontal_index)
            new_interaction_points_mapping[(2, interaction_point2.index_in_lanes, str(interaction_point2.interaction_lanes))] = (0,current_horizontal_index)

            elements.append(SVD.InteractionConstruct(common_element[0], frequency1 + frequency2, current_horizontal_index))

        else:
            elements.append(SVD.CommonConstruct(common_element[0], frequency1 + frequency2, current_horizontal_index))

        current_horizontal_index += 1
        
        # Update indices for the next iteration
        last_position1 = current_position1 + 1
        last_position2 = current_position2 + 1



    current_position1 = base_lane1.elements[-1].position + 1
    current_position2 = base_lane2.elements[-1].position + 1

    # Determine all interval subprocesses and summarize them
    interval_subprocesses = []
    for j in range(len(all_lanes)):
        if(all_lanes[j][0] == 1):
            if(current_position1 - last_position1 >= 0):
                subprocess = []
                for elem in all_lanes[j][1].elements:
                    if(elem.position >= last_position1 and elem.position < current_position1):
                        subprocess.append(elem)
                interval_subprocesses.append((all_lanes[j][0], subprocess))
            else:
                interval_subprocesses.append((all_lanes[j][0],[]))
        else: 
            if(current_position2 - last_position2 >= 0):
                subprocess = []
                for elem in all_lanes[j][1].elements:
                    if(elem.position >= last_position2 and elem.position < current_position2):
                        subprocess.append(elem)
                interval_subprocesses.append((all_lanes[j][0], subprocess))
            else:
                interval_subprocesses.append((all_lanes[j][0],[]))
        
    # Add summarized subprocess to elements
    interval_elements, interval_length, interval_mapping = __apply_patterns(interval_subprocesses, current_horizontal_index, summarization1, summarization2, o_lane1, o_lane2, print_result)
    elements.extend(interval_elements)
    new_interaction_points_mapping.update(interval_mapping)
    current_horizontal_index += interval_length

    return SVD.SuperLane(lane_id, lane_name, object_type, elements, cardinality, frequency), new_interaction_points_mapping



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
                if (lane_id == 1):
                    interaction_point1 = None
            
                    for interaction_point in summarization1.interaction_points:
                        if(interaction_point.index_in_lanes == elements[1][i].position and o_lane1.lane_id in interaction_point.interaction_lanes):
                            interaction_point1 = interaction_point
                            break

                    current_mappings[(1, interaction_point1.index_in_lanes, str(interaction_point1.interaction_lanes))] = start_index + i

                else:
                    interaction_point2 = None
            
                    for interaction_point in summarization2.interaction_points:
                        if(interaction_point.index_in_lanes == elements[1][i].position and o_lane2.lane_id in interaction_point.interaction_lanes):
                            interaction_point2 = interaction_point
                            break

                    current_mappings[(2, interaction_point2.index_in_lanes, str(interaction_point2.interaction_lanes))] = start_index + i


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