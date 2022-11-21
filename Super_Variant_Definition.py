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
    horizontal_indices = []
    frequency = 0 
    
    def __init__(self, lane_id, name, object_type, elements, indices, frequency):
        self.lane_id = lane_id
        self.object_type = object_type
        self.lane_name = name
        self.elements = elements
        self.horizontal_indices = indices
        self.frequency = frequency
    
    def __str__(self):
        result_string = f"ID: {self.lane_id}, Name: {self.lane_name}: ["
        for i in range(len(self.elements)):
            result_string += "(Pos: " + str(self.horizontal_indices[i]) + ", " + str(self.elements[i]) + "),"       
        result_string = result_string[:-1]
        return result_string + "]"
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.object_type != other.object_types:
                return False
            elif len(self.elements) == len(other.elements):
                return False
            else:
                result = True
                for i in range(len(self.elements)):
                    result = result and self.elements[i] == other.elements[i]
                result = result and self.horizontal_indices == other.horizontal_indices
                return result
        return False
    
    def update_indices(self, start_index, offset):
        for i in range(start_index, len(self.horizontal_indices)):
            self.horizontal_indices[i] += offset
            
class SummarizedConstruct:
    '''The data structure the elements of a summarized variant'''

class CommonConstruct(SummarizedConstruct):
    '''The data structure of common activities in a summarized variant'''
    activity = ""
    frequency = 0
    
    def __init__(self, activity, frequency):
        self.activity = activity
        self.frequency = frequency
        
    def __str__(self):
        return f"{self.activity}"
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.activity == other.activity
        return False

    
class OptionalConstruct(SummarizedConstruct):
    '''The data structure of an optional activity in a summarized variant'''
    options = []
    frequencies = []
    
    def __init__(self, options, frequencies):
        self.options = options
        self.frequencies = frequencies
    
    def __str__(self):
        return f"Optional {self.options}"
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.options == other.options
        return False

    
class ChoiceConstruct(SummarizedConstruct):
    '''The data structure of a choice of activities in a summarized variant'''
    choices = []
    frequencies = []
    
    def __init__(self, choices, frequencies):
        self.choices = choices
        self.frequencies = frequencies
        
    def __str__(self):
        return f"Choices {self.choices}"
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.choices == other.choices
        return False


def convert_to_summarized_format(lane):
    '''
    Converts a single line that needs no summarization to the desired format
    :param lane: The single flattened lane of one involved object
    :type lane: Lane
    :return: single lane converted into a summarized format
    :rtype:SummarizedLane
    '''
    elements = []
    indices = []
    for i in range(len(lane.activities)):
        elements.append(CommonConstruct(lane.activities[i],1))
        indices.append(lane.horizontal_indices[i])
    
    result = SummarizedLane(tuple()+(lane.lane_id,), lane.object_type ,lane.object_type, elements, indices)
    return result


def is_interaction_point(interactions, activity_name, positions):
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
            interactions = [lane.lane_id]
            for interactionPoint in summarized_variant.interaction_points:
                if(lane.lane_id in interactionPoint.interaction_lanes and lane.horizontal_indices[i] == interactionPoint.index_in_lanes):
                    interactions.extend(interactionPoint.interaction_lanes)

            activities.append([lane.elements[i],[[lane.horizontal_indices[i],lane.horizontal_indices[i]],list(set(interactions))]])
    
    # Remove duplicate activities that are interaction points
    unique_activities = []
    for activity in activities:
        identical_activities = [u_activity for u_activity in unique_activities if activity[1][0][0] == u_activity[1][0][0] and activity[1][1] == u_activity[1][1]]
        if (len(identical_activities) < 1):
            unique_activities.append(activity)
    
    return[unique_activities,items]