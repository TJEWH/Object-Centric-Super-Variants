import Super_Variant_Definition as SVD
import Super_Variant_Visualization as WVV

def get_optimal_super_variant(summarizations):
    id = 0
    init_super_variant = summarizations[0].to_super_variant(id)
    super_variants = join_into_super_variant(init_super_variant, summarizations[10])
    #print(super_variants)
    # Join first two summarizations
    # Join third summarization with all super variants from the first join etc -> spanning -> Select optimal/smallest alignment cost
    return

def join_into_super_variant(super_variant, summarization):

    print("Joining into Super Variant")
    WVV.visualize_super_variant_summarization(super_variant)
    WVV.visualize_super_variant_summarization(summarization)

    get_lane_mappings(super_variant, summarization, super_variant.lanes, summarization.lanes, [])


def get_lane_mappings(super_variant, summarization, lanes_super_variant, lanes_summarization, current_mapping):

    # Initialize current lane candidate
    import copy
    current_lane = lanes_summarization.pop()
    print("Lane " + str(current_lane) + " requires matching.")
    current_type = current_lane.object_type
    propagatative_mapping = copy.deepcopy(current_mapping)
    print("So far, we have the following matches: " + str(propagatative_mapping) + ".")

    # Determine matching corresponding candidates
    possible_joining_candidates = [lane for lane in lanes_super_variant if lane.object_type == current_type]
    print("This lane can be matched with the following lanes of the Super Variant:")
    for lane in possible_joining_candidates:
        print(lane)

    # Remove the current candidate from the list of remaining matches
    remaining_lanes_summarization = [lane for lane in lanes_summarization if lane.lane_id != current_lane.lane_id]
    print("After this match, it remains to match the following remaining lanes of the summarization:")
    for lane in remaining_lanes_summarization:
        print(lane)

    # Determine all interacting lanes that still require matching
    all_interacting_lanes = []
    for interaction in summarization.interaction_points:
        if (current_lane.lane_id in interaction.interaction_lanes):
            all_interacting_lanes.extend(interaction.interaction_lanes)
    all_interacting_lanes = list(set(all_interacting_lanes))

    remaining_interacting_lanes = [lane for lane in lanes_summarization if lane.lane_id in all_interacting_lanes]
    print("This lane is interacting with lanes " + str(all_interacting_lanes) + ".")
    print("From those, the following lanes still require matching:")
    for lane in remaining_interacting_lanes:
        print(lane)
    

    if(len(possible_joining_candidates) == 0):
        # Lane has no counterpart in the Super Variant, must be entirely optional
        print("There exists no matching candidate for the current lane, thus, it is entirely optional.")
        print("Adding the matching " + str((current_lane.lane_id, None)) + ".")
        propagatative_mapping.append((current_lane.lane_id, None))
        remaining_lanes_super_variant = lanes_super_variant

        # Propagate optionality among interactions, if no propagation required
        remaining_lanes_summarization, propagatative_mapping = propagate_optionality(summarization, remaining_interacting_lanes, remaining_lanes_summarization, propagatative_mapping)

        # if no other lanes require matching, return, otherwise recurse with the next candidate
        #if (remaining_lanes_summarization == []):
            #return propagatative_mapping
        #else:
            #print("Recursing on the next candidate...")
            #return get_lane_mappings(super_variant, summarization, remaining_lanes_super_variant, remaining_lanes_summarization, propagatative_mapping)


    else: 
        # Create Super Variant for each combination of lane candidates
        for candidate in possible_joining_candidates:
            propagatative_mapping = copy.deepcopy(current_mapping)
            print("Exploring the possible matching " + str((current_lane.lane_id, candidate.lane_id)) + ".")

            # Add the matching and remove the lane from the remaining lanes
            propagatative_mapping.append((current_lane.lane_id, candidate.lane_id))
            remaining_lanes_super_variant = [lane for lane in lanes_super_variant if lane.lane_id != candidate.lane_id]

            # Propagate join, if no propagation required, continue with next lane or return full mapping
            remaining_lanes_summarization, remaining_lanes_super_variant, mapping = propagate_match(super_variant, summarization, remaining_interacting_lanes, remaining_lanes_summarization, propagatative_mapping)

            # if remaining_lanes_summarization != [] recursive call else return append mapping
            # IS PROPAGATION ALONE ENOUGH?

        # Concatenate all individual mappings and return


def propagate_optionality(summarization, remaining_interacting_lanes, remaining_lanes_summarization, current_mapping):

    print("Propagating...")
    while remaining_interacting_lanes:
        print("It remains to propagate the optionality to the following lanes:")
        for lane in remaining_interacting_lanes:
            print(lane)

        # Add the matching and remove the lane from the remaining lanes
        prop_lane = remaining_interacting_lanes.pop()
        print("Adding the matching " + str((prop_lane.lane_id, None)) + ".")
        current_mapping.append((prop_lane.lane_id, None))
        remaining_lanes_summarization = [lane for lane in remaining_lanes_summarization if lane.lane_id != prop_lane.lane_id]
        remaining_interacting_id = [lane.lane_id for lane in remaining_lanes_summarization]

        # Continuing propagation
        for interaction in summarization.interaction_points:
            if (prop_lane.lane_id in interaction.interaction_lanes):
                for id in interaction.interaction_lanes:
                    if(id != prop_lane.lane_id and id not in remaining_interacting_lanes and id in remaining_interacting_id):
                        remaining_interacting_lanes.append(summarization.get_lane(id))

        return remaining_lanes_summarization, current_mapping


def propagate_match(summarization, remaining_interacting_lanes, remaining_lanes_summarization, current_mapping):

    print("Propagating...")
    while remaining_interacting_lanes:
        print("It remains to propagate the optionality to the following lanes:")
        for lane in remaining_interacting_lanes:
            print(lane)

        # Add the matching and remove the lane from the remaining lanes
        prop_lane = remaining_interacting_lanes.pop()
        print("Adding the matching " + str((prop_lane.lane_id, None)) + ".")
        current_mapping.append((prop_lane.lane_id, None))
        remaining_lanes_summarization = [lane for lane in remaining_lanes_summarization if lane.lane_id != prop_lane.lane_id]
        remaining_interacting_id = [lane.lane_id for lane in remaining_lanes_summarization]

        # Continuing propagation
        for interaction in summarization.interaction_points:
            if (prop_lane.lane_id in interaction.interaction_lanes):
                for id in interaction.interaction_lanes:
                    if(id != prop_lane.lane_id and id not in remaining_interacting_lanes and id in remaining_interacting_id):
                        remaining_interacting_lanes.append(summarization.get_lane(id))

        return remaining_lanes_summarization, current_mapping