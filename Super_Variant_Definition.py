class SummarizedVariant:
    '''The data structure of the summarization of object-centric variants'''
    object_types = {}
    lanes = []
    interaction_points = []
    frequency = 0 
    
    def __init__(self, lanes, object_types, interaction_points, frequency):
        self.lanes = lanes
        self.object_types = object_types
        self.interaction_points = interaction_points
        self.frequency = frequency 

    
    def __str__(self):
        result_string = "Lanes: \n"
        for i in range(len(self.lanes)):
            result_string += str(self.lanes[i]) + "\n"
        result_string += "\nInvolved Objects: \n" + str(self.object_types) +"\n"
        result_string += "\nInteraction Points: \n"
        for i in range(len(self.interaction_points)):
            result_string += str(self.interaction_points[i]) + "\n"
        return result_string + "Frequency: " + str(self.frequency)


    def rename_lane(self, lane_id, new_name):
        '''
        Replaces the name of the lane in the summarized variant with the given lane id with a new name.
        :param self: The summarized variant
        :type self: SummarizedVariant
        :param lane_id: The id of the lane that should be renamed
        :type lane_id: tuple
        :param new_name: The new name for the lane
        :type new_name: str
        '''
        for lane in self.lanes:
            if(lane.lane_id == lane_id):
                lane.lane_name = new_name
                break

    
    def equals(self, other):
        '''
        Checks two summarized variants for equality up to lane naming and frequencies.
        :param self: The summarized variant
        :type self: SummarizedVariant
        :param other: The other summarized variant
        :type other: SummarizedVariant
        :return: Whether the two summarized variants are equal
        :rtype: bool
        '''
        return ((self.encode_lexicographically()) == (other.encode_lexicographically()))

   
    def encode_lexicographically(self):
        '''
        Converts the summarized variant into an encoding string.
        :param self: The summarized variant
        :type self: SummarizedVariant
        :return: The corresponding lexicographic encoding
        :rtype: str
        '''
        
        # Stores the mapping from original lane_id to the new lane_id based on the enumeration of the encoded lanes
        mapping = {}
        
        # The lanes are sorted by their type and encoded in this alphabetical order
        total_order_objects = [str(object) for object in list(self.object_types)]
        total_order_objects.sort()

        encoded_result = []
        for object in total_order_objects:

            # Determine all lanes for this object type
            object_lanes = [lane for lane in self.lanes if lane.object_type == object]

            # Determine the maximal number of digits for the new lane_id
            power_of_ten = len(str(len(object_lanes)))

            encoded_lanes = []
            id = 0

            # Encode each lane, enumerate the encodings provisionally
            for lane in object_lanes:

                encoding = lane.encode_lexicographically()
        
                # Fill up the current id with 0's such that every id has the same number of characters
                full_id = str(id)
                while (len(full_id) < power_of_ten):
                    full_id = str(0) + full_id
                encoded_lanes.append(full_id + encoding)

                # Store a reference between the temporary id and the original lane_id of the lane
                mapping[full_id + encoding] = (lane.lane_id, 0)
                id += 1

            # Sort the encodings aphabetically, excluding its temporary id
            encoded_lanes.sort(key = lambda x: x[power_of_ten:])
            
            # Replace the temporary id with the enumeration of encodings as the new lane_id and add the object type to the prefix
            for i in range(len(encoded_lanes)):
                full_id = str(i)
                while (len(full_id) < power_of_ten):
                    full_id = str(0) + full_id
                lane_id = mapping[encoded_lanes[i]][0]
                mapping[encoded_lanes[i]]= (lane_id, object + " " + full_id)
                self.rename_lane(lane_id, object + " " + full_id)
                encoded_lanes[i] = object + " " + full_id + ": " + encoded_lanes[i][power_of_ten:]


            encoded_result.extend(encoded_lanes)

        # Create dictionary for easy extraction of the new lane_id when encoding the interactions
        mapping = dict((x, y) for x, y in list(mapping.values()))

        interactions_result = []
        for interaction in self.interaction_points:

            # Encode references with the new lane_id and sort alphabetically
            interacting_lanes = [mapping[lane_id] for lane_id in interaction.interaction_lanes]
            interacting_lanes.sort()
            lanes_encoding = "".join(str(x) + ", " for x in interacting_lanes)
            lanes_encoding = lanes_encoding[:-2]
            encoding = f"IP[{interaction.index_in_lanes},[{lanes_encoding}]] "
            interactions_result.append(encoding)
        
        interactions_result.sort() 

        # Concatenate all encodings
        result = ""
        for encoded_lane in encoded_result:
            result += encoded_lane
        result += "- "
        for encoded_ip in interactions_result:
            result += encoded_ip
        
        # Additionally sort the Super Lane itself
        self.lanes.sort(key = lambda x: x.lane_name)
        return result


    def to_super_variant(self, id):
        '''
        Converts a generic summarized variant into a Super Variant by assigning an id.
        :param self: The summarized variant
        :type self: SummarizedVariant
        :param id: The id for the Super Variant
        :type id: int
        :return: The corresponding Super Variant
        :rtype: SuperVariant
        '''
        return SuperVariant(id, self.lanes, self.object_types, self.interaction_points, self.frequency)


    def get_lane(self, id):
        '''
        Finds and returns a lane of the summarized variant with the given id.
        :param self: The summarized variant
        :type self: SummarizedVariant
        :param id: The id of the lane
        :type id: int
        :return: The corresponding Super Lane
        :rtype: SuperLane
        '''
        for lane in self.lanes:
            if (lane.lane_id == id):
                return lane
        return None
 
class SuperVariant(SummarizedVariant):
    '''The generalized data structure of the summarization of object-centric variants and Super Variants'''
     
    id = 0

    def __init__(self, id, lanes, object_types, interaction_points, frequency):
        self.lanes = lanes
        self.object_types = object_types
        self.interaction_points = interaction_points
        self.frequency = frequency
        self.id = id

    def __str__(self):
        result_string = "Super Variant " + str(self.id) + "\nLanes: \n"
        for i in range(len(self.lanes)):
            result_string += str(self.lanes[i]) + "\n"
        result_string += "\nInvolved Objects: \n" + str(self.object_types) +"\n"
        result_string += "\nInteraction Points: \n"
        for i in range(len(self.interaction_points)):
            result_string += str(self.interaction_points[i]) + "\n"
        return result_string + "Frequency: " + str(self.frequency)
    
    
class SuperLane:
    '''The data structure of the summarization of lanes and Super Lanes'''
    lane_id = ()
    object_type = ""
    lane_name = ""
    elements = []
    cardinality = "0" 
    frequency = 0
    
    def __init__(self, lane_id, name, object_type, elements, cardinality, frequency):
        self.lane_id = lane_id
        self.object_type = object_type
        self.lane_name = name
        self.elements = elements
        self.cardinality = cardinality
        self.frequency = frequency
    
    def __str__(self):
        result_string = f"ID: {self.lane_id}, Name: {self.lane_name}, Cardinality: {self.cardinality}:  ["
        for i in range(len(self.elements)):
            result_string += str(self.elements[i]) + ","       
        result_string = result_string[:-1]
        return result_string + "]"


    def encode_lexicographically(self):
        '''
        Converts the Super Lane into an encoding string.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :return: The corresponding lexicographic encoding
        :rtype: str
        '''
        encoding = f"CAR {self.cardinality}: "

        for element in self.elements:

            if(type(element) == CommonConstruct):
                encoding += f"CO[{element.position}:{element.position}, {element.activity}] "

            elif(type(element) == InteractionConstruct):
                encoding += f"IP[{element.position}:{element.position}, {element.activity}] "
                        
            else:
                        
                # Determine all choice sequences and sort alphabetically
                choices = [choice.encode_lexicographically() for choice in element.choices]
                choices.sort()

                element.choices.sort(key = lambda x: x.encode_lexicographically())
                index = 0
                for choice in element.choices:
                    choice.lane_id = index
                    index += 1

                # Encode all choices
                choices_encoding = ""
                for choice in choices:
                    choices_encoding += choice
                    choices_encoding += ", "
                choices_encoding = choices_encoding[:-2]

                if(type(element) == ChoiceConstruct):
                    encoding += f"CH[{element.position_start}:{element.position_end}, [{choices_encoding}]] "
                        
                elif(type(element) == OptionalConstruct):
                    encoding += f"OP[{element.position_start}:{element.position_end}, [{choices_encoding}]] "

        return encoding[:-1]


    def same_summarization(self, other):
        '''
        Checks the equality between two Super Lanes.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param other: The other summarizing Super Lane
        :type other: SuperLane
        :return: Whether the Super Lanes have the same object type and elements
        :rtype: bool
        '''
        if(other.object_type != self.object_type or len(self.elements) != len(other.elements)):
            return False
        else:
            result = True
            for i in range(len(self.elements)):
                result = result and self.elements[i] == other.elements[i]
            return result
    
    
    def subsumed_summarization(self, other):
        '''
        Checks whether either of the Super Lanes is subsumed in the other.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param other: The other summarizing Super Lane
        :type other: SuperLane
        :return: Whether the Super Lanes have are subsuming each other
        :rtype: bool
        '''
        import copy 
        if(other.object_type != self.object_type):
            return False

        result = False
        self_contains_choice = any(isinstance(x, ChoiceConstruct) for x in self.elements) or any(isinstance(x, OptionalConstruct) for x in self.elements)
        other_contains_choice = any(isinstance(x, ChoiceConstruct) for x in other.elements) or any(isinstance(x, OptionalConstruct) for x in other.elements)

        if(self_contains_choice and not other_contains_choice):
            realizations = self.get_realizations_normalized()
            normalized_other = copy.deepcopy(other).normalize()
            for realization in realizations:
                result = result or realization.same_summarization(normalized_other)

        elif(not self_contains_choice and other_contains_choice):
            realizations = other.get_realizations_normalized()
            normalized_self = copy.deepcopy(self).normalize()
            for realization in realizations:
                result = result or realization.same_summarization(normalized_self)
        else:
            realizations_self = self.get_realizations_normalized()
            realizations_other = other.get_realizations_normalized()
            subsumed_in_other = True
            subsumed_in_self = True
            for realization in realizations_self:
                subsumed_in_other = subsumed_in_other and any([realization.same_summarization(other) for other in realizations_other])
            for realization in realizations_other:
                subsumed_in_self = subsumed_in_self and any([realization.same_summarization(other) for other in realizations_self])
            result = (subsumed_in_other or subsumed_in_self)
                
        return result

    def normalize(self, offset = 0):
        '''
        Creates an abstraction of the Super Lane, shifting the positions to their normalized values starting from an offset value.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param offset: The starting index of the normalized Super Lane, defaulted at 0
        :type offset: int
        :return: The corresponding normalized Super Lane
        :rtype: SuperLane
        '''
        import copy 
        elements = copy.deepcopy(self.elements)
        index = offset
        for element in elements:
            if(type(element) == CommonConstruct or type(element) == InteractionConstruct):
                element.position = index
                index += 1
            elif(type(element) == ChoiceConstruct or type(element) == OptionalConstruct):
                normalized_options = []
                end_index = index
                for option in element.options:
                    normalized_options.append(option.normalize(index))
                    if(isinstance(normalized_options[-1].elements[-1], CommonConstruct)):
                        end_index = max(end_index, normalized_options[-1].elements[-1].position)
                    elif(isinstance(normalized_options[-1].elements[-1], GeneralChoiceStructure)):
                        end_index = max(end_index, normalized_options[-1].elements[-1].position_end)
                element.position_start = index
                element.position_end = end_index
                index += end_index - index + 1
            
        return SuperLane(0, "normalization", self.object_type, elements, None, 0)


    def get_realizations_normalized(self):
        '''
        Generates all realizations of a Super Lane with normalized positions starting from 0.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :return: The list of all realizations
        :rtype: list of type SuperLane
        '''
        import copy
        realizations = []
        realizations.append([])

        for elem in self.elements:
            element = copy.deepcopy(elem)

            if(type(element) == CommonConstruct or type(element) == InteractionConstruct):
                realizations = [realization + [element] for realization in realizations]

            elif(type(element) == ChoiceConstruct or type(element) == OptionalConstruct):
                intermediate_result = []
                for i in range(len(element.choices)):
                    for sublist in element.choices[i].get_realizations_normalized(element.start):
                        intermediate_result.extend([realization + sublist.elements for realization in realizations])
                if(type(element) == OptionalConstruct):
                    intermediate_result.extend(realizations)
                realizations = intermediate_result

        result = []
        for i in range(len(realizations)):
            index = 0
            for element in realizations[i]:
                element.position = index
                index += 1
            result.append(SuperLane(i, "realization " + str(i), self.object_type, realizations[i], None, 0))

        return result

    def get_realizations(self):
        '''
        Generates all realizations of a Super Lane.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :return: The list of all realizations
        :rtype: list of type SuperLane
        '''
        import copy
        realizations = []
        realizations.append([])

        for elem in self.elements:
            element = copy.deepcopy(elem)

            if(type(element) == CommonConstruct or type(element) == InteractionConstruct):
                realizations = [realization + [element] for realization in realizations]

            elif(type(element) == ChoiceConstruct or type(element) == OptionalConstruct):
                intermediate_result = []
                for i in range(len(element.choices)):

                    for sublist in element.choices[i].get_realizations():
                        intermediate_result.extend([realization + sublist.elements for realization in realizations])

                if(type(element) == OptionalConstruct):
                    intermediate_result.extend(realizations)
                realizations = intermediate_result

        result = []
        #TODO frequency and count are not the
        for i in range(len(realizations)):
            frequency = 1
            for elem in realizations[i]:
                frequency = frequency*elem.frequency
            frequency = self.frequency
            frequency = frequency/len(realizations)
            elements = []
            for elem in realizations[i]:
                elements.append(copy.deepcopy(elem))
                elements[-1].frequency = frequency
            result.append(SuperLane(i, "realization " + str(i), self.object_type, elements, self.cardinality, frequency))

        return result

   
    def get_element(self, position, highlevel = True, option_id = None):
        '''
        Extracts the element of the Super Lane at the given position.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param position: The positional index of the element
        :type position: int
        :param highlevel: Whether to return the high-level element or extract the sub-element from choice structures, default True
        :type highlevel: bool
        :param option_id: Only used for a non-highlevel setting. The id of the lane in a choice to consider, otherwise all choices are considered, default None 
        :type option_id: int
        :return: The element at the given position
        :rtype: SummarizationElement
        '''
        for element in self.elements:
            if((type(element) == CommonConstruct or type(element) == InteractionConstruct) and element.position == position):
                return element
            if((type(element) == ChoiceConstruct or type(element) == OptionalConstruct) and position >= element.position_start and position <= element.position_end):
                if(not highlevel):
                    if(option_id):
                        return element.choices[option_id].get_element(position)
                    else:
                        return_options = [option.get_element(position) for option in element.choices if option.get_element(position)]
                        if(return_options != []):
                            return return_options[0]
                        else:
                            return None
                else:
                    return element
        return None


    def contains_activity(self, activity_label):
        '''
        Checks whether the given activity label occurs in the Super Lane.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param activity_label: The label of the activity
        :type activity_label: str
        :return: Whether the activity is contained in the Super Lane
        :rtype: bool
        '''
        for element in self.elements:
            if((type(element) == CommonConstruct or type(element) == InteractionConstruct) and element.activity == activity_label):
                return True
            elif((type(element) == ChoiceConstruct or type(element) == OptionalConstruct)):

                for choice in element.choices:
                    if (choice.contains_activity(activity_label)):
                        return True

        return False

    def count_activity(self, activity_label):
        '''
        Extracts the number of times the given activity label occurs in the Super Lane.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param activity_label: The label of the activity
        :type activity_label: str
        :return: The count of occurences
        :rtype: int
        '''
        count = 0
        for element in self.elements:
            if((type(element) == CommonConstruct or type(element) == InteractionConstruct) and element.activity == activity_label):
                count += 1
            elif((type(element) == ChoiceConstruct or type(element) == OptionalConstruct)):

                for choice in element.choices:
                    count += choice.count_activity(activity_label)

        return count
    
    
    def shift_lane(self, start_element, offset, index = None):
        '''
        Shifts the positions of the Super Lane by an offset starting from a given start element.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param start_element: The first element that requires shifting
        :type start_element: SummarizationConstruct
        :param offset: The offset of the shift
        :type offset: int
        :param index: The index of the starting element in the list of elements
        :type index: int
        '''
        if(index == None):
            index = self.elements.index(start_element)
        for i in range(index, len(self.elements)):
            if(type(self.elements[i]) == CommonConstruct or type(self.elements[i]) == InteractionConstruct):
                self.elements[i].position += offset
            elif(type(self.elements[i]) == ChoiceConstruct or type(self.elements[i]) == OptionalConstruct):
                self.elements[i].position_start += offset
                self.elements[i].position_end += offset 
                for choice in self.elements[i].choices:
                    choice.shift_lane(choice.elements[0], offset)


    def shift_lane_exact(self, start_position, offset, choice_id = 0):
        '''
        Shifts the positions of the Super Lane by an offset starting from a given start position.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param start_position: The position from which the shifting should begin
        :type start_position: int
        :param offset: The offset of the shift
        :type offset: int
        :param choice_id: The id of the choice in which the shift should begin
        :type choice_id: int
        :return: Whether the shift affected an element partially anf the corresponding start and end positions of that element before the shift
        :rtype: bool, int, int
        '''

        for i in range(len(self.elements)):

            # Case 1: Start shifting from a Common Activity
            if((type(self.elements[i]) == InteractionConstruct) and self.elements[i].position == start_position):
                self.shift_lane(self.elements[i], offset, i)
                return False, i, start_position, start_position
        
            # Case 2: Start shifting from a Generic Choice Structure
            elif((type(self.elements[i]) == ChoiceConstruct or type(self.elements[i]) == OptionalConstruct) and self.elements[i].position_end >= start_position and self.elements[i].position_start <= start_position):

                start_position_before_shift = self.elements[i].position_start
                end_position_before_shift = self.elements[i].position_end
                
                self.elements[i].choices[choice_id].shift_lane_exact(start_position, offset)

                all_start_positions = []
                all_end_positions = []

                for choice in self.elements[i].choices:
                    if(isinstance(choice.elements[0], CommonConstruct)):
                        all_start_positions.append(choice.elements[0].position)
                    elif(isinstance(choice.elements[0], GeneralChoiceStructure)):
                        all_start_positions.append(choice.elements[0].position_start)

                    if(isinstance(choice.elements[-1], CommonConstruct)):
                        all_end_positions.append(choice.elements[-1].position)
                    elif(isinstance(choice.elements[-1], GeneralChoiceStructure)):
                        all_end_positions.append(choice.elements[-1].position_end)
                        

                self.elements[i].position_start = min(all_start_positions)
                self.elements[i].position_end = max(all_end_positions)
                
                if(i < len(self.elements)-1):
                    self.shift_lane(self.elements[i+1], self.elements[i].position_end - end_position_before_shift, i+1)

                return True, i, start_position_before_shift, end_position_before_shift
                


    def remove_non_common_elements(self):
        '''
        Returns the Super Lane with only the elements that are not indicating choices.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :return: The Super Lane with only the desired subset of elements
        :rtype: SuperLane
        '''
        new_elements = []
        for elem in self.elements:
            if(isinstance(elem, CommonConstruct)):
                new_elements.append(elem)
        return SuperLane(self.lane_id, self.lane_name, self.object_type, new_elements, self.cardinality, self.frequency)


    def make_optional(self, position, empty_frequency, choice_id = None):
        '''
        Shifts the positions of the Super Lane by an offset starting from a given start position.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param position: The position of the element that is to be made optional
        :type position: int
        :param empty_frequency: The counter-frequency of the optional element that is subtracted from the current element frequency
        :type lane: float
        :param choice_id: The id of the choice in which an element should be made optional
        :type choice_id: int
        :return: The modified Super Lane and the modified element
        :rtype: SuperLane, OptionalChoiceConstruct
        '''
        for i in range(len(self.elements)):
            if (isinstance(self.elements[i], InteractionConstruct) and self.elements[i].position == position):
                self.elements[i] = self.elements[i].make_optional(self, empty_frequency)
                return self, self.elements[i]
            elif(isinstance(self.elements[i], GeneralChoiceStructure) and self.elements[i].position_start <= position and self.elements[i].position_end >= position):
                if(choice_id):
                    self.elements[i].choices[choice_id], element = self.elements[i].choices[choice_id].make_optional(position, empty_frequency)
                    return self, element
                else:
                    self.elements[i].choices[choice_id], element = self.elements[i].choices[0].make_optional(position, empty_frequency)
                    return self, element
        return self, None

    
    def add_optional_activity(self, position, activity, choice_id = 0):
        '''
        Inserts an optional element into the Super Lane at the given position.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param position: The position at which the optional element should be inserted
        :type position: int
        :param activity: The optional element that should be inserted
        :type activity: OptionalConstruct
        :param choice_id: The id of the choice in which the activity should be added
        :type choice_id: int
        :return: The modified Super Lane
        :rtype: SuperLane
        '''

        activity.position_start = position
        activity.position_end = position
        activity.choices[0].elements[0].position = position 

        for i in range(len(self.elements)):
            if (isinstance(self.elements[i], CommonConstruct) and self.elements[i].position >= position):
                self.shift_lane(self.elements[i], 1, i)
                predecessors = []
                if(i > 0):
                    predecessors = self.elements[:i]
                successors = self.elements[i:]
                self.elements = predecessors + [activity] + successors
                return self

            elif(isinstance(self.elements[i], GeneralChoiceStructure) and self.elements[i].position_start <= position and self.elements[i].position_end >= position):

                self.elements[i].choices[choice_id] = self.elements[i].choices[choice_id].add_optional_activity(position, activity)

                all_end_positions = []
                for choice in self.elements[i].choices:
                    if(isinstance(choice.elements[-1], CommonConstruct)):
                        all_end_positions.append(choice.elements[-1].position)
                    elif(isinstance(choice.elements[-1], GeneralChoiceStructure)):
                        all_end_positions.append(choice.elements[-1].position_end)

                new_end = max(all_end_positions)
                length_difference = new_end - self.elements[i].position_end
                self.elements[i].position_end = new_end

                if(i < len(self.elements)-1):
                    self.shift_lane(self.elements[i+1], length_difference, i+1)

                return self

        self.elements = self.elements + [activity]
        return self

    # Might need an update for nested structures
    def shift_activities_up(self, up_to = None):
        '''
        Shifts all non-interaction elements up to the next element's position.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :param up_to: The position to which the lane should be shifted
        :type up_to: int
        :return: The modified Super Lane
        :rtype: SuperLane
        '''

        # Shift last element 
        if(isinstance(self.elements[-1], GeneralChoiceStructure)):

            for j in range(len(self.elements[-1].choices)):
                if(up_to):
                    self.elements[-1].choices[j] = self.elements[-1].choices[j].shift_activities_up(up_to)
                else: 
                    self.elements[-1].choices[j] = self.elements[-1].choices[j].shift_activities_up(self.elements[-1].position_end)

            all_start_positions = []
            all_end_positions = []

            for choice in self.elements[-1].choices:
                if(isinstance(choice.elements[0], CommonConstruct)):
                    all_start_positions.append(choice.elements[0].position)
                elif(isinstance(choice.elements[0], GeneralChoiceStructure)):
                    all_start_positions.append(choice.elements[0].position_start)

                if(isinstance(choice.elements[-1], CommonConstruct)):
                    all_end_positions.append(choice.elements[-1].position)
                elif(isinstance(choice.elements[-1], GeneralChoiceStructure)):
                    all_end_positions.append(choice.elements[-1].position_end)
                        

            self.elements[-1].position_start = min(all_start_positions)
            self.elements[-1].position_end = max(all_end_positions)

        else:
            if(up_to):
                self.elements[-1].position = up_to

        # Continue to shift up each element to its successor element
        for i in range(len(self.elements) - 1):
            index = len(self.elements) - 1 - i
            if (isinstance(self.elements[index-1], CommonConstruct) and not isinstance(self.elements[index-1], InteractionConstruct)):

                if (isinstance(self.elements[index], CommonConstruct)):
                    offset = self.elements[index].position - self.elements[index-1].position - 1
                elif (isinstance(self.elements[index], GeneralChoiceStructure)):
                    offset = self.elements[index].position_start - self.elements[index-1].position - 1
                else:
                    offset = 0

                self.elements[index-1].position += offset


            elif(isinstance(self.elements[index-1], GeneralChoiceStructure)):

                if (isinstance(self.elements[index], CommonConstruct)):
                    offset = self.elements[index].position
                elif (isinstance(self.elements[index], GeneralChoiceStructure)):
                    offset = self.elements[index].position_start
                else:
                    offset = 0

                for j in range(len(self.elements[index-1].choices)):
                    self.elements[index-1].choices[j] = self.elements[index-1].choices[j].shift_activities_up(max(offset-1,0))

                all_start_positions = []
                all_end_positions = []

                for choice in self.elements[index-1].choices:
                    if(isinstance(choice.elements[0], CommonConstruct)):
                        all_start_positions.append(choice.elements[0].position)
                    elif(isinstance(choice.elements[0], GeneralChoiceStructure)):
                        all_start_positions.append(choice.elements[0].position_start)

                    if(isinstance(choice.elements[-1], CommonConstruct)):
                        all_end_positions.append(choice.elements[-1].position)
                    elif(isinstance(choice.elements[-1], GeneralChoiceStructure)):
                        all_end_positions.append(choice.elements[-1].position_end)
                        

                self.elements[index-1].position_start = min(all_start_positions)
                self.elements[index-1].position_end = max(all_end_positions)


        return self

    def contains_interaction_point(self):
        '''
        Determines whether the Super Lane contains an interaction point.
        :param self: The summarizing Super Lane
        :type self: SuperLane
        :return: Whether the Super Lane contains an InteractionConstruct element
        :rtype: bool
        '''
        for element in self.elements:
            if (isinstance(element, InteractionConstruct)):
                return True
            elif(isinstance(element, GeneralChoiceStructure)):
                for option in element.choices:
                    if (option.contains_interaction_point()):
                        return True
        return False



class OptionalSuperLane(SuperLane):
    '''The data structure of a subclass of Super Lanes that is entirely optional'''

    def __str__(self):
        result_string = f"Optional ID: {self.lane_id}, Name: {self.lane_name}, Cardinality: {self.cardinality}:  ["
        for i in range(len(self.elements)):
            result_string += str(self.elements[i]) + ","       
        result_string = result_string[:-1]
        return result_string + "]"



class SummarizationElement:
    '''The data structure the elements of a summarized variant'''


class CommonConstruct(SummarizationElement):
    '''The data structure of common activities in a summarized variant'''
    activity = ""
    frequency = 0
    position = 0
    
    def __init__(self, activity, frequency, position):
        self.activity = activity
        self.frequency = frequency
        self.position = position
        
    def __str__(self):
        return f"(Pos {self.position}: {self.activity})"
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.activity == other.activity
        return False

    def make_optional(self, lane, empty_frequency):
        '''
        Converts the element to an element within an optional construct.
        :param self: The common or interaction element
        :type self: CommonConstruct
        :param lane The corresponding SuperLane 
        :type lane: SuperLane
        :param empty_frequency: The counter-frequency of the optional element that is subtracted from the current element frequency
        :type lane: float
        :return: the optional element
        :rtype: OptionalConstruct
        '''
        self.frequency -= empty_frequency
        option = SuperLane(0, "option 0", lane.object_type, [self], 1, self.frequency)
        return OptionalConstruct([option], self.position, self.position)


class InteractionConstruct(CommonConstruct):
    
    def __str__(self):
        return f"(Pos {self.position}: Interaction {self.activity})"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.activity == other.activity
        return False

    
class GeneralChoiceStructure(SummarizationElement):
    '''The data structure of an choices of activity sequences in a summarized variant'''
    choices = []
    position_start = 0
    position_end = 0
    
    def __init__(self, choices, start, end):
        self.choices = choices
        self.position_start = start
        self.position_end = end
    
    def __eq__(self, other):
        import copy
        if isinstance(other, self.__class__):
            self_encoded_choices = copy.deepcopy(self.choices)
            self_encoded_choices = [choice.encode_lexicographically() for choice in self_encoded_choices]
            self_encoded_choices.sort()

            other_encoded_choices = copy.deepcopy(other.choices)
            other_encoded_choices = [choice.encode_lexicographically() for choice in other_encoded_choices]
            other_encoded_choices.sort()
            
            if(len(self_encoded_choices) != len(other_encoded_choices)):
                return False

            equal = True
            for i in range(len(self_encoded_choices)):
                equal = equal and (self_encoded_choices[i] == other_encoded_choices[i])
            return equal
            
        return False


    def get_vertical_height(self):
        vertical_height = len(self.choices)

        for choice in self.choices:
            maximal_choice_height = 1
            for element in choice.elements:
                if(isinstance(element, GeneralChoiceStructure)):
                    maximal_choice_height = max(maximal_choice_height, element.get_vertical_height())
            vertical_height += maximal_choice_height - 1
        
        return vertical_height



class OptionalConstruct(GeneralChoiceStructure):
    '''The data structure of an optional choices of activity sequences in a summarized variant'''
    
    def __str__(self):
        result_string = f"(Pos: {self.position_start} - {self.position_end}: Optional Choices "
        result_string += "("
        for choice in self.choices:
            result_string += str(choice) + ", "
        result_string = result_string[:-2] + ")"
        return result_string

class ChoiceConstruct(GeneralChoiceStructure):
    '''The data structure of a choice of activities in a summarized variant'''
    
    def __str__(self):
        result_string = f"(Pos: {self.position_start} - {self.position_end}: Choices "
        result_string += "("
        for choice in self.choices:
            result_string += str(choice) + ", "
        result_string = result_string[:-2] + ")"
        return result_string


def is_interaction_point(interactions, lane, position):
    '''
    Determines whether one of the merged original activities of a summarized activity is an interaction point.
    :param interactions: The interaction points of the variant
    :type interaction: list of type InteractionPoint
    :param activity_name: The name of the activity that is checked
    :type activity_name: str
    :param positions: The original indices of the merged activities
    :type positions: tuple
    :return: Whether the activity at any of the given positions is listed as an interaction point
    :rtype: bool
    '''
    for interaction in interactions:
        if lane in interaction.interaction_lanes and interaction.index_in_lanes == position:
            return True, interaction
    return False, None


def summarized_variant_layouting(summarized_variant):
    '''
    Formats a summarized vatriant into a visualization layout.
    :param summarized_variant: The summarized variant that requires reformatting
    :type summarized_variant: SummarizedVariant
    :return: A list of all elements and their positions with references to the involved lanes
    :rtype: list
    '''
    items = {}
    
    # Create dictionary of objects
    for type in summarized_variant.object_types:
        object_lanes = [lane for lane in summarized_variant.lanes if lane.object_type == type]
        for lane in object_lanes:
            items[lane.lane_id] = (type, lane.lane_name, lane.cardinality)
    
    # Create list of activities and their indices
    activities = []
    for lane in summarized_variant.lanes:
        for elem in lane.elements:

            interactions = [lane.lane_id]

            if(isinstance(elem,InteractionConstruct)):
                for interactionPoint in summarized_variant.interaction_points:
                    if(lane.lane_id in interactionPoint.interaction_lanes and elem.position == interactionPoint.index_in_lanes):
                        interactions.extend(interactionPoint.interaction_lanes)

            if(isinstance(elem,CommonConstruct) or isinstance(elem,InteractionConstruct)):
                activities.append([elem,[[elem.position, elem.position],list(set(interactions))]])
            else:
                activities.append([elem,[[elem.position_start, elem.position_end],list(set(interactions))]])
    
    # Remove duplicate activities that are interaction points
    unique_activities = []
    for activity in activities:
        identical_activities = [u_activity for u_activity in unique_activities if activity[1][0][0] == u_activity[1][0][0] and activity[1][1] == u_activity[1][1]]
        if (len(identical_activities) < 1):
            unique_activities.append(activity)
    
    return[unique_activities,items]