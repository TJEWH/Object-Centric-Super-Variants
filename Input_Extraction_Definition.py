class VariantLane:
    '''The data structure of one lane of a variant'''
    lane_id = 0
    object_type = ""
    lane_name = ""
    activities = []
    horizontal_indices = []
    
    def __init__(self, lane_id, object_type, name, activities, indices):
        self.lane_id = lane_id
        self.object_type = object_type
        self.lane_name = name
        self.activities = activities
        self.horizontal_indices = indices
    
    def __str__(self):
        result_string = f"ID: {self.lane_id}, Name: {self.lane_name}: ["
        for i in range(len(self.activities)):
            result_string += "(Pos: " + str(self.horizontal_indices[i]) + ", " + self.activities[i] + "),"       
        result_string = result_string[:-1]
        return result_string + "]"
    
    def has_type(self, input_type):
        return self.object_type == input_type


class InteractionPoint:
    '''The data structure of an Interaction Point'''
    activity_name = ""
    interaction_lanes = []
    interacting_types = {}
    index_in_lanes = 0
    
    def __init__(self, name, lanes, types, index):
        self.activity_name = name                                                                      
        self.interaction_lanes = lanes                                                                      
        self.interacting_types = types
        self.index_in_lanes = index
        
    def __str__(self):
        return f"Interaction Point: {self.activity_name} at Pos: {self.index_in_lanes}"


class ExtractedVariant:
    '''The data structure of a variant with extracted lanes'''
    object_types  = {}
    lanes = []
    interaction_points = {}
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
    
    def get_lanes_of_type(self, object_type):
        return [lane for lane in self.lanes if lane.object_type == object_type]
    
    def get_lane(self, lane_id):
        return [lane for lane in self.lanes if lane.lane_id == lane_id][0]


def extract_lanes(variant, frequency):
    '''
    Converts a layouted variant into another format used by the summarization methods
    :param variant: The single flattened lane of one involved object
    :type variant: List
    :return: The conversion of the input variant into the ExtractedVariant format
    :rtype: ExtractedVariant
    '''
    
    # Separate event elements and objects
    objects = variant[1]
    events = sorted(variant[0],key=lambda x: (x[1][0]))
    
    # Store the interaction points for preservation
    extracted_lanes = []
            
    # Create element for each lane in the variant, storing a lists of activities
    # and the object specification
    for i in range(len(objects)):
        lane = []
        positions = []
        for j in range(len(events)):
            if(i in events[j][1][1]):
                lane.append(events[j][0])
                positions.append(events[j][1][0][0])    
        
        extracted_lanes.append(VariantLane(i, objects[i][0], objects[i][1], lane, positions))
        
    extracted_interactions = []
    for i in range(len(events)):
        if (len(events[i][1][1]) > 1):
            types = []
            for j in range(len(events[i][1][1])):
                types.append(objects[events[i][1][1][j]][0])
            extracted_interactions.append(InteractionPoint((events[i][0]), events[i][1][1], set(types), events[i][1][0][0]))
    
    extracted_types = set([object[0] for object in objects.values()])
    extracted_variant = ExtractedVariant(extracted_lanes, extracted_types, extracted_interactions, frequency)
    return extracted_variant


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
            return True, interaction
    return False, None