import Super_Variant_Definition as SVD

class VariantLane:
    '''The data structure of a lane of a variant correponding to the activity execution of an object instance'''
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
        '''
        Determines whether the lane corresponds to an object instances of the given type
        :param self: The lane
        :type self: VariantLane
        :param input_type: The object type label
        :type input_type: str
        :return: Whether the object type of the lane equals the given object type
        :rtype: bool
        '''
        return self.object_type == input_type

    def to_super_lane(self, interactions):
        ''' 
        Converts a variant lane into a Super Lane.
        :param self: The variant lane
        :type self: VariantLane
        :param interactions: The interactions of the variant
        :type interactions: set of type InteractionPoints
        :return: The corresponding Super Lane
        :rtype: SuperLane
        '''
        elements = []
        for i in range(len(self.activities)):
            position = self.horizontal_indices[i]
            activity_label = self.activities[i]
            is_interaction_point = False
            for interaction_point in interactions:
                if(interaction_point.index_in_lanes == position and self.lane_id in interaction_point.interaction_lanes):
                    interaction_point = interaction_point
                    is_interaction_point = True
                    break
            if(is_interaction_point):
                elements.append(SVD.InteractionConstruct(activity_label, 1, position))

            else:
                elements.append(SVD.CommonConstruct(activity_label, 1, position))

        return SVD.SuperLane(self.lane_id, self.lane_name, self.object_type, elements, "1", 1)


class InteractionPoint:
    '''The data structure of an Interaction Point'''
    activity_name = ""
    interaction_lanes = []
    interacting_types = {}
    index_in_lanes = 0
    
    def __init__(self, activity_label, lanes, types, index):
        self.activity_name = activity_label                                                                    
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
        '''
        Returns all lanes of the variant that correspond to object instances of the given object type
        :param self: The variant
        :type variant: ExtractedVariant
        :param object_type: The object type label
        :type object_type: str
        :return: A list of type VariantLane
        :rtype: list
        '''
        return [lane for lane in self.lanes if lane.object_type == object_type]
    
    def get_lane(self, lane_id):
        '''
        Returns the lane of the variant with the given lane id
        :param self: The variant
        :type variant: ExtractedVariant
        :param lane_id: The lane id
        :type lane_id: int
        :return: The VariantLane with the given id
        :rtype: VariantLane
        '''
        for lane in self.lanes:
            if (lane.lane_id == lane_id):
                return lane
        return None

    def to_super_variant(self):
        return SVD.SummarizedVariant([lane.to_super_lane(self.interaction_points) for lane in self.lanes], self.object_types, self.interaction_points, self.frequency)


def extract_lanes(variant, frequency):
    '''
    Extracts the variant from the corresponding variant layouting and its frequency
    :param variant: The layouting of a variant
    :type variant: dict
    :param frequency: The relative frequency of the variant
    :type frequency: float
    :return: The extracted variant
    :rtype: ExtractedVariant
    '''

    objects = variant[1]
    events = sorted(variant[0],key=lambda x: (x[1][0]))
    
    extracted_lanes = []
            
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


def is_interaction_point(interactions, lane, position):
    '''
    Determines whether the activity in a certain lane at a given position is an interaction point
    :param interactions: The interaction points of the corresponding variant
    :type interaction: list of type InteractionPoint
    :param lane: The lane id
    :type lane: int
    :param position: The position index
    :type position: int
    :return: Whether the activity at the position is an interaction point, The corresponding interaction point
    :rtype: bool, InteractionType
    '''
    for interaction in interactions:
        if lane in interaction.interaction_lanes and interaction.index_in_lanes == position:
            return True, interaction
    return False, None