import Summarization_Utils as SU
import Super_Variant_Definition as SVD

def summarize_variant(variant, print_result = True):
    '''
    
    '''
    # Initialize result variables
    result_lanes = []
    updated_interaction_points = []
    object_types = variant.object_types
    remaining_lanes = [lane.lane_id for lane in variant.lanes]
    
    interaction_points_mapping = []
    
    # Initialize keeping track of the sets of lanes that require summarization
    initial_candidate_set = [lane.lane_id for lane in variant.get_lanes_of_type(variant.lanes[0].object_type)]
    to_be_summarized = [initial_candidate_set]
    i = 0 
    
    while to_be_summarized:
        if(print_result):
            print('─' * 40)
            print("Iteration: " + str(i))
        summarization_candidates = to_be_summarized.pop()
        if(print_result):
            print("Summarizing lanes of type " + variant.get_lane(summarization_candidates[0]).object_type + ":")  
            print(summarization_candidates)
            print("\n")
        
        # Keeping track of the remaining lanes that need to be summarized
        remaining_lanes = [lane for lane in remaining_lanes if lane not in summarization_candidates]
            
        # Determine all involved interaction_points of the summarization
        involved_interaction_points = []
        involved_lanes = []
        for interaction_point in variant.interaction_points:
            if any(elem in summarization_candidates for elem in interaction_point.interaction_lanes):
                involved_interaction_points.append(interaction_point)
                involved_lanes.extend(interaction_point.interaction_lanes)
        
        involved_lanes = set(involved_lanes)
        
        lanes = [variant.get_lane(candidate) for candidate in summarization_candidates]
        summarized_lane, new_mappings = SU.summarize_lanes(lanes,involved_interaction_points, print_result)
        interaction_points_mapping.append((summarized_lane.lane_id,new_mappings))
        result_lanes.append(summarized_lane)
        if(print_result):
            print("\n")
            print("Intermediate Result:")
            print("\n")
            print(result_lanes[-1])
            print("\n")
        
        # Determine the next summarization candidates by extracting all still not summarized involved lanes
        external_involved_lanes = [elem for elem in remaining_lanes if elem in involved_lanes]
        for type in object_types:
            next_candidates = [lane_id for lane_id in external_involved_lanes if variant.get_lane(lane_id).object_type == type]
            
            # Cluster the candidates by type and add to list
            if len(next_candidates)>0 :
                if(print_result):
                    print("Adding involved lanes of type " + str(type) + " to the candidate list of the next iterations.")
                to_be_summarized.append(next_candidates)
                if(print_result):
                    print("These are: \n")
                    print(to_be_summarized[-1])
                    print("\n")
            
        i += 1
    if(print_result):
        print('─' * 40)
        print("Aligning the lanes:")
        print("\n")
    result_lanes, result_interaction_points = SU.re_align_lanes(result_lanes, interaction_points_mapping, print_result)
    return SVD.SummarizedVariant(result_lanes,object_types,result_interaction_points)