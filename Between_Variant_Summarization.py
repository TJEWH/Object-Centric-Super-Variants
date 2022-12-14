import Super_Variant_Definition as SVD
import Super_Variant_Visualization as WVV

def join_super_variants(summarization1, summarization2, remaining_lanes1, remaining_lanes2, current_mapping):
    WVV.visualize_super_variant_summarization(summarization1)
    WVV.visualize_super_variant_summarization(summarization2)
    #super_lane_edit_distance(summarization1.lanes[0], summarization2.lanes[0])
    #print(summarization1.lanes[0])
    #print(summarization2.lanes[1])
    return

def super_lane_edit_distance(lane1, lane2):

    import math
    if (lane1.object_type != lane2.object_type):
        return math.inf, None

    else:
            __get_optimal_alignment_mapping(lane1, lane2)
            #print(common_activities)
            #cost = 0 

            # Initializing the values for the summarized lanes object
            #elements = []
            #object_type = lane1.object_type
            #lane_name = lane1.object_type + " i"
            #lane_id = (lane1.lane_id, lane2.lane_id)
            
            #new_interaction_points_mapping = {}
            #current_horizontal_index = 0
            
            # Keep track of indices
            #positions_in_lane1 = (0, list(common_activities.values())[0][0])
            #positions_in_lane2 = (0, list(common_activities.values())[0][1])

                
            #for i in range(len(common_activities)-1):
                
                # Determine all interval subprocesses and summarize them
                #interval_subprocesses = [lane1.elements[positions_in_lane1[0]:positions_in_lane1[1]], lane2.elements[positions_in_lane2[0]:positions_in_lane2[1]]]
                #if(interval_subprocesses != [[],[]]):
                    #print(interval_subprocesses)
                    #interval_elements, interval_mappings, cost = determine_edit_distance(interval_subprocesses)
                    #elements.append(interval_elements)
                #print(lane1.elements[positions_in_lane1[1]])
                #positions_in_lane1 = (positions_in_lane1[1]+1, list(common_activities.values())[i+1][0])
                #positions_in_lane2 = (positions_in_lane2[1]+1, list(common_activities.values())[i+1][1])

                
def determine_edit_distance(subprocesses):
    return 

def __get_optimal_alignment_mapping(lane1, lane2):
    '''
    Extracts the longest sequence of activities found in both, preserving their order and computes the optimal alignment of elements among the two lanes based on that
    :param lane1: A lane from a Super Variant 
    :type lane1: Super Lane
    :param lane2: A lane from another Super Variant 
    :type lane1: Super Lane
    :return: the longest order preserving common activity sequence and their indices in the variant
    :rtype: dict
    '''
    # Initialization, copy elements
    lane1_realizations = lane1.get_realizations()
    lane2_realizations = lane2.get_realizations()
    activity_sets = []
    
    for lane1 in lane1_realizations:

        for lane2 in lane2_realizations:

            # Retrieves all common sublists that ensure the precise order
            for i in range(len(lane1.elements)):
                current_index_lane_2 = 0
        
                # Keeping track of the original indices and the remaining sublists
                set = dict()
        
                # For each activity in base lane as starting point find the list of activities that appear in the other lane
                for j in range(i,len(lane1.elements)):
            
                    if (any(element.activity == lane1.elements[j].activity and type(element) == type(lane1.elements[j]) for element in lane2.elements[current_index_lane_2:])):
   
                        # Add the corresponding index for the lanes
                        for k in range(len(lane2.elements)):
                            if (lane2.elements[k].activity == lane1.elements[j].activity):
                                indices = (lane1.elements[j].position, lane2.elements[k].position)
                                current_index_lane_2 = k + 1
                                break
                
                        # Enumerate duplicate activity labels
                        duplicate_key_set = [key for key in list(set.keys()) if key[1] == lane1.elements[j].activity]
                        if (len(duplicate_key_set) > 0):
                            maximum = max([key[0] for key in duplicate_key_set])
                            set[maximum+1, lane1.elements[j].activity] = indices
                        else:
                            set[0, lane1.elements[j].activity] = indices
                activity_sets.append(set)
        
    # The maximal list of activities for optimality
    best_order_preserving_sequence = max(activity_sets, key=len)

    result_mapping = []
    index_in_lane1 = 0
    index_in_lane2 = 0
    for key in best_order_preserving_sequence.keys():
        lane1_position = best_order_preserving_sequence[key][0]
        lane2_position = best_order_preserving_sequence[key][1]
        lane1_element = None
        lane2_element = None
        lane1_precedence = []
        lane2_precedence = []

        # Get elements of both positions
        for i in range(index_in_lane1, len(lane1.elements)):
            if((isinstance(lane1.elements[i], SVD.CommonConstruct) or isinstance(lane1.elements[i], SVD.InteractionConstruct)) and lane1.elements[i].position == lane1_position):
                lane1_element = lane1.elements[i]
                index_in_lane1 = i+1
                break
            elif(isinstance(lane1.elements[i], SVD.GeneralChoiceStructure) and lane1.elements[i].start_position <= lane1_position and lane1.elements[i].end_position >= lane1_position):
                lane1_element = lane1.elements[i]
                index_in_lane1 = i+1
                break
            else: lane1_precedence.append(lane1.elements[i])

        for i in range(index_in_lane2, len(lane2.elements)):
            if(isinstance(lane2.elements[i], SVD.CommonConstruct or isinstance(lane1.elements[i], SVD.InteractionConstruct)) and lane2.elements[i].position == lane2_position):
                lane2_element = lane2.elements[i]
                index_in_lane2 = i+1
                break
            elif(isinstance(lane2.elements[i], SVD.GeneralChoiceStructure) and lane2.elements[i].start_position <= lane2_position and lane2.elements[i].end_position >= lane2_position):
                lane2_element = lane2.elements[i]
                index_in_lane2 = i+1
                break
            else: lane2_precedence.append(lane2.elements[i])


        for elem in lane1_precedence:
            print(elem)
        for elem in lane2_precedence:
            print(elem)
        print("--------")
        print(lane1_element)
        print(lane2_element)
        print("-----------------------------------------")

        
        




