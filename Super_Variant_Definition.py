class SummarizedVariant:
    '''The data structure of a summarized object-centric variant'''
    object_types = {}
    lanes = []
    interaction_points = []
    
    def __init__(self, lanes, object_types, interaction_points):
        self.lanes = lanes
        self.object_types = object_types
        self.interaction_points = interaction_points
    
    def __str__(self):
        result_string = "Lanes: \n"
        for i in range(len(self.lanes)):
            result_string += str(self.lanes[i]) + "\n"
        result_string += "\nInvolved Objects: \n" + str(self.object_types) +"\n"
        result_string += "\nInteraction Points: \n"
        for i in range(len(self.interaction_points)):
            result_string += str(self.interaction_points[i]) + "\n"
        return result_string
    
    def __eq__(self, other):
        return
    
    
class SummarizedLane:
    '''The data structure of a summarized object-centric variant'''
    lane_id = ()
    object_type = ""
    lane_name = ""
    elements = []
    cardinality = 0 
    
    def __init__(self, lane_id, name, object_type, elements, cardinality):
        self.lane_id = lane_id
        self.object_type = object_type
        self.lane_name = name
        self.elements = elements
        self.cardinality = cardinality
    
    def __str__(self):
        result_string = f"ID: {self.lane_id}, Name: {self.lane_name}: ["
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
        #else:
            #realizations1 = self.get_realizations()
            #realizations2 = summarization.get_realizations()

            #result1 = []
            #for i in range(len(realizations1)):
            #    sequence_list = [element.activity for element in realizations1[i].elements]
            #    result1.append(sequence_list)

            #result2 = []
            #for i in range(len(realizations2)):
            #    sequence_list = [element.activity for element in realizations2[i].elements]
            #    result2.append(sequence_list)

            #result = set(result1) == set(result2)
                
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
            result.append(SummarizedLane(i, "realization " + str(i), self.object_type, realizations[i], None))
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
        
        

                    


            
class VariantElement:
    '''The data structure the elements of a summarized variant'''

class CommonConstruct(VariantElement):
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

    
class OptionalConstruct(VariantElement):
    '''The data structure of an optional activity in a summarized variant'''
    choices = []
    frequencies = []
    position_start = 0
    position_end = 0
    
    def __init__(self, options, frequencies, start, end):
        self.options = options
        self.frequencies = frequencies
        self.position_start = start
        self.position_end = end
    
    def __str__(self):
        return f"(Pos: {self.position_start} - {self.position_end}: Optional {self.options})"
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.options == other.options
        return False

    
class ChoiceConstruct(VariantElement):
    '''The data structure of a choice of activities in a summarized variant'''
    choices = []
    frequencies = []
    position_start = 0
    position_end = 0
    
    def __init__(self, choices, frequencies, start, end):
        self.choices = choices
        self.frequencies = frequencies
        self.position_start = start
        self.position_end = end
        
    def __str__(self):
        return f"(Pos: {self.position_start} - {self.position_end}: Optional {self.choices})"
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.choices == other.choices
        return False


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
    
    result = SummarizedLane(tuple()+(lane.lane_id,), lane.object_type ,lane.object_type, elements)
    return result


def is_interaction_point(interactions, activity_name, positions):
    '''
    Determines whether the merged set of activities was an interaction point
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
        if interaction.activity_name == activity_name and interaction.index_in_lanes in positions:
            return True  
    return False


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
            items[lane.lane_id] = (type, lane.lane_name, lane.frequency)
    
    # Create list of activities and their indices
    activities = []
    for lane in summarized_variant.lanes:
        for i in range(len(lane.elements)):
            if(type(lane.elements[i]) == CommonConstruct):
                interactions = [lane.lane_id]
                for interactionPoint in summarized_variant.interaction_points:
                    if(lane.lane_id in interactionPoint.interaction_lanes and lane.elements[i].position == interactionPoint.index_in_lanes):
                        interactions.extend(interactionPoint.interaction_lanes)

            activities.append([lane.elements[i],[[lane.elements[i].position, lane.elements[i].position],list(set(interactions))]])
    
    # Remove duplicate activities that are interaction points
    unique_activities = []
    for activity in activities:
        identical_activities = [u_activity for u_activity in unique_activities if activity[1][0][0] == u_activity[1][0][0] and activity[1][1] == u_activity[1][1]]
        if (len(identical_activities) < 1):
            unique_activities.append(activity)
    
    return[unique_activities,items]