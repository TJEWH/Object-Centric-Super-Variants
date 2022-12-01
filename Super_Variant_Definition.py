class SummarizedVariant:
    '''The data structure of a summarized object-centric variant'''
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
        for lane in self.lanes:
            if(lane.lane_id == lane_id):
                lane.lane_name = new_name
    
    def equals(self, other):
        return ((self.encode_lexicographically()) == (other.encode_lexicographically()))

    def encode_lexicographically(self):

        mapping = {}
        
        total_order_objects = [str(object) for object in list(self.object_types)]
        total_order_objects.sort()

        encoded_result = []
        for object in total_order_objects:

            object_lanes = [lane for lane in self.lanes if lane.object_type == object]
            encoded_lanes = []
            id = 0
            for lane in object_lanes:
                encoding = f"CAR {lane.cardinality}: "
                for element in lane.elements:
                    if(type(element) == CommonConstruct):
                        encoding += f"CO[{element.position}:{element.position}, {element.activity}] "

                    elif(type(element) == InteractionConstruct):
                        encoding += f"IP[{element.position}:{element.position}, {element.activity}] "
                        
                    else:
                        choices = []
                        for choice in element.choices:
                            sequence = ""
                            for i in range(len(choice)):
                                sequence += str(choice[i])
                            choices.append(sequence)
                        choices_encoding = ""
                        for choice in choices:
                            choices_encoding += choice
                            choices_encoding += ", "
                        choices_encoding = choices_encoding[:-2]

                        if(type(element) == ChoiceConstruct):
                            encoding += f"CH[{element.position_start}:{element.position_end}, [{choices_encoding}]] "
                        
                        elif(type(element) == OptionalConstruct):
                            encoding += f"OP[{element.position_start}:{element.position_end}, [{choices_encoding}]] "
        

                encoded_lanes.append(str(id) + encoding)
                mapping[str(id) + encoding] = (lane.lane_id,0)
                id += 1

            encoded_lanes.sort(key = lambda x: x[1:])

            for i in range(len(encoded_lanes)):
                lane_id = mapping[encoded_lanes[i]][0]
                mapping[encoded_lanes[i]]= (lane_id, object + " " + str(i))
                self.rename_lane(lane_id, object + " " + str(i))
                encoded_lanes[i] = object + " " + str(i) + ": " + encoded_lanes[i][1:]

            encoded_result.extend(encoded_lanes)

        mapping = dict((x, y) for x, y in list(mapping.values()))

        interactions_result = []
        for interaction in self.interaction_points:
            interacting_lanes = [mapping[lane_id] for lane_id in interaction.interaction_lanes]
            interacting_lanes.sort()
            lanes_encoding = "".join(str(x)+", " for x in interacting_lanes)
            lanes_encoding = lanes_encoding[:-2]
            encoding = f"IP[{interaction.index_in_lanes},[{lanes_encoding}]] "
            interactions_result.append(encoding)
        
        interactions_result.sort() 

        result = ""
        for encoded_lane in encoded_result:
            result += encoded_lane
        result += "- "
        for encoded_ip in interactions_result:
            result += encoded_ip
        
        self.lanes.sort(key = lambda x: x.lane_name)
        return result
 
class SuperVariant(SummarizedVariant):
     
    id = 0

    def __init__(self, id, lanes, object_types, interaction_points, frequency):
        self.lanes = lanes
        self.object_types = object_types
        self.interaction_points = interaction_points
        self.frequency = frequency
        self.id = id

    def __str__(self):
        result_string = "Super Variant " + str(id) + "\n Lanes: \n"
        for i in range(len(self.lanes)):
            result_string += str(self.lanes[i]) + "\n"
        result_string += "\nInvolved Objects: \n" + str(self.object_types) +"\n"
        result_string += "\nInteraction Points: \n"
        for i in range(len(self.interaction_points)):
            result_string += str(self.interaction_points[i]) + "\n"
        return result_string + "Frequency: " + str(self.frequency)
    
    
class SuperLane:
    '''The data structure of a summarized object-centric variant'''
    lane_id = ()
    object_type = ""
    lane_name = ""
    elements = []
    cardinality = "0" 
    
    def __init__(self, lane_id, name, object_type, elements, cardinality):
        self.lane_id = lane_id
        self.object_type = object_type
        self.lane_name = name
        self.elements = elements
        self.cardinality = cardinality
    
    def __str__(self):
        result_string = f"ID: {self.lane_id}, Name: {self.lane_name}, Cardinality: {self.cardinality}:  ["
        for i in range(len(self.elements)):
            result_string += str(self.elements[i]) + ","       
        result_string = result_string[:-1]
        return result_string + "]"


    def same_summarization(self, summarization):
        if(summarization.object_type != self.object_type or len(self.elements) != len(summarization.elements)):
            return False
        else:
            result = True
            for i in range(len(self.elements)):
                result = result and self.elements[i] == summarization.elements[i]
            return result
    
    def subsumed_summarization(self, summarization):
        if(summarization.object_type != self.object_type or len(self.elements) != len(summarization.elements)):
            return False
        result = False
        self_contains_choice = any(isinstance(x, ChoiceConstruct) for x in self.elements) or any(isinstance(x, OptionalConstruct) for x in self.elements)
        other_contains_choice = any(isinstance(x, ChoiceConstruct) for x in summarization.elements) or any(isinstance(x, OptionalConstruct) for x in summarization.elements)
        if(self_contains_choice and not other_contains_choice):
            realizations = self.get_realizations()
            for realization in realizations:
                result = result or realization.same_summarization(summarization)
        elif(not self_contains_choice and other_contains_choice):
            realizations = summarization.get_realizations()
            for realization in realizations:
                result = result or realization.same_summarization(self)
        else:
            realizations1 = self.get_realizations()
            realizations2 = summarization.get_realizations()
            subsumed_in_2 = True
            subsumed_in_1 = True
            for realization in realizations1:
                subsumed_in_2 = subsumed_in_2 and any([realization.same_summarization(other) for other in realizations2])
            for realization in realizations2:
                subsumed_in_1 = subsumed_in_1 and any([realization.same_summarization(other) for other in realizations1])
            result = (subsumed_in_2 or subsumed_in_1)
                
        return result

    def get_realizations(self):
        realizations = []
        realizations.append([])
        for element in self.elements:
            if(type(element) == CommonConstruct or type(element) == InteractionConstruct):
                realizations = [realization + [element] for realization in realizations]
            if(type(element) == ChoiceConstruct or type(element) == OptionalConstruct):
                intermediate_result = []
                for choice in element.choices:
                    sublist = [CommonConstruct(choice[i], None, 0) for i in range(len(choice))]
                    intermediate_result.extend([realization + sublist for realization in realizations])
                realizations = intermediate_result
        result = []
        for i in range(len(realizations)):
            index = 0
            for element in realizations[i]:
                element.position = index
                index += 1
            result.append(SuperLane(i, "realization " + str(i), self.object_type, realizations[i], None))
        return result


    def get_element(self, position):
        for element in self.elements:
            if((type(element) == CommonConstruct or type(element) == InteractionConstruct) and element.position == position):
                return element
            if((type(element) == ChoiceConstruct or type(element) == OptionalConstruct) and position >= element.position_start and position <= element.position_end):
                return element
        return None

    
    def shift_lane(self, start_element, offset):
        index = self.elements.index(start_element)
        for i in range(index, len(self.elements)):
            if(type(self.elements[i]) == CommonConstruct or type(self.elements[i]) == InteractionConstruct):
                self.elements[i].position += offset
            if(type(self.elements[i]) == ChoiceConstruct or type(self.elements[i]) == OptionalConstruct):
                self.elements[i].position_start += offset
                self.elements[i].position_end += offset      

class OptionalSuperLane(SuperLane):

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

class InteractionConstruct(CommonConstruct):
    
    def __str__(self):
        return f"(Pos {self.position}: Interaction {self.activity})"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.activity == other.activity
        return False

class GeneralChoiceStructure(SummarizationElement):
    choices = []
    frequencies = []
    position_start = 0
    position_end = 0
    
    def __init__(self, choices, frequencies, start, end):
        self.choices = choices
        self.frequencies = frequencies
        self.position_start = start
        self.position_end = end
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.choices == other.choices
        return False

class OptionalConstruct(GeneralChoiceStructure):
    '''The data structure of an optional activity in a summarized variant'''
    
    def __str__(self):
        return f"(Pos: {self.position_start} - {self.position_end}: Optional {self.choices})"


    
class ChoiceConstruct(GeneralChoiceStructure):
    '''The data structure of a choice of activities in a summarized variant'''
    
    def __str__(self):
        return f"(Pos: {self.position_start} - {self.position_end}: Choice {self.choices})"


def convert_to_summarized_format(lane):
    '''
    Converts a single lane that needs no summarization to the desired format
    :param lane: The single flattened lane of one involved object
    :type lane: Lane
    :return: single lane converted into a summarized format
    :rtype: SummarizedLane
    '''
    elements = []
    for i in range(len(lane.activities)):
        elements.append(CommonConstruct(lane.activities[i], 1, i))
    
    result = SuperLane(tuple()+(lane.lane_id,), lane.object_type ,lane.object_type, elements)
    return result


def is_interaction_point(interactions, lane, position):
    '''
    Determines whether one of the merged original activities of a summarized activity is an interaction point
    :param interactions: The interaction points of the variant
    :type interaction: List of type InteractionPoint
    :param activity_name: The name of the activity that is checked
    :type activity_name: String
    :param positions: The original indices of the merged activities
    :type positions: Tuple
    :return: Whether the activity at any of the given positions is listed as an interaction point
    :rtype: Boolean
    '''
    for interaction in interactions:
        if lane in interaction.interaction_lanes and interaction.index_in_lanes == position:
            return True, interaction
    return False, None


def summarized_variant_layouting(summarized_variant):
    '''
    Formats a summary of a variant based on its visualization
    :param summarized_variant: The summarized variant that requires reformatting
    :type summarized_variant: SummarizedVariant
    :return: A list of all elements and their positions with references to the involved lanes
    :rtype: List
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