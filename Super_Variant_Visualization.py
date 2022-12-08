import Super_Variant_Definition as SVD

import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from matplotlib import colors

DEFAULT_CHEVRON_LENGTH = 15.
DEFAULT_CHEVRON_HEIGHT = 4.

def __chevron_at_position(horizontal_index, vertical_index, length, height):
    
    from matplotlib.path import Path
    verts = [
       (horizontal_index, vertical_index),  # Left bottom coner
       (horizontal_index + DEFAULT_CHEVRON_LENGTH * length, vertical_index),  # Right bottom corner
       (horizontal_index + DEFAULT_CHEVRON_LENGTH * length + 1.25, vertical_index + height/2), # Outer tip of chevron
       (horizontal_index + DEFAULT_CHEVRON_LENGTH * length, vertical_index + height),  # Right top coner
       (horizontal_index, vertical_index + height),  # Left bottom coner
       (horizontal_index + 1.25, vertical_index + height/2), # Inner top of chevron
       (horizontal_index, vertical_index),  # Left bottom coner
    ]

    codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
        Path.CLOSEPOLY,
    ]

    return Path(verts, codes)


def __interaction_activity_chevron(ax, lane, element, lane_properties, interaction_points, current_vertical_position):

    from matplotlib.path import Path
    import matplotlib.patches as patches

    interacting_lanes = [lane]
    for interaction in interaction_points:
        if (interaction.index_in_lanes == element.position and lane in interaction.interaction_lanes):
            interacting_lanes = interaction.interaction_lanes
    number_sub_chevrons = len(interacting_lanes)
    length_sub_chevron = (1/number_sub_chevrons)
    frequency = lane_properties[lane]["Frequency"]
    interacting_lanes.sort(key = lambda x: lane_properties[x]["Height"], reverse=True)

    label = element.activity
    label = label + " (" + str(frequency) + ")"
    ax.text(element.position * DEFAULT_CHEVRON_LENGTH + 2.0, current_vertical_position * DEFAULT_CHEVRON_HEIGHT + 0.5 * DEFAULT_CHEVRON_HEIGHT * lane_properties[lane]["Height"] - 0.3, label, zorder = 10)

    for i in range(len(interacting_lanes)):
        ax.add_patch(patches.PathPatch(__chevron_at_position(element.position * DEFAULT_CHEVRON_LENGTH + i * length_sub_chevron * DEFAULT_CHEVRON_LENGTH, current_vertical_position * DEFAULT_CHEVRON_HEIGHT, length_sub_chevron, lane_properties[lane]["Height"]  * DEFAULT_CHEVRON_HEIGHT), facecolor = lane_properties[interacting_lanes[i]]["Color"], lw = 0, ls = '-', zorder = 5))
    ax.add_patch(patches.PathPatch(__chevron_at_position(element.position * DEFAULT_CHEVRON_LENGTH, current_vertical_position * DEFAULT_CHEVRON_HEIGHT, 1, lane_properties[lane]["Height"]  * DEFAULT_CHEVRON_HEIGHT), facecolor="None", lw = 1.3, ls = '-', zorder = 7))
    return ax

def __summarized_activity_chevron(ax, element, lane_property, color, current_vertical_position):
    
    from matplotlib.path import Path
    import matplotlib.patches as patches
        
    if (isinstance(element, SVD.CommonConstruct)):
        label = element.activity
        label = label + " (" + str(element.frequency) + ")"
        ax.text(element.position * DEFAULT_CHEVRON_LENGTH + 2.0, current_vertical_position * DEFAULT_CHEVRON_HEIGHT + 0.5 * DEFAULT_CHEVRON_HEIGHT * lane_property["Height"] - 0.3, label, zorder = 10)
        ax.add_patch(patches.PathPatch(__chevron_at_position(element.position * DEFAULT_CHEVRON_LENGTH, current_vertical_position * DEFAULT_CHEVRON_HEIGHT, 1, lane_property["Height"]  * DEFAULT_CHEVRON_HEIGHT), facecolor = color, lw = 1.3, ls = '-', zorder = 5))
        return ax
        
    elif (isinstance(element, SVD.GeneralChoiceStructure)): 
        if(isinstance(element, SVD.OptionalConstruct)):
            line_style = '--'
            margin_length = 0.0
        else:
            line_style = '-'
            margin_length = 0.3

        ax.add_patch(patches.PathPatch(__chevron_at_position(element.position_start * DEFAULT_CHEVRON_LENGTH, current_vertical_position * DEFAULT_CHEVRON_HEIGHT, (element.position_end - element.position_start) + 1, lane_property["Height"]  * DEFAULT_CHEVRON_HEIGHT), facecolor = "None", lw = 1.3, ls = "-", zorder = 5))

        sub_default_chevron_lenght = ((((element.position_end - element.position_start) + 1) * DEFAULT_CHEVRON_LENGTH) - 2.5) / ((element.position_end - element.position_start) + 1)
        sub_default_chevron_lenght -= margin_length / ((element.position_end - element.position_start) + 1)
        sub_default_chevron_heigth = DEFAULT_CHEVRON_HEIGHT * 5/6
        margin_height = DEFAULT_CHEVRON_HEIGHT * 1/12

        for i in range(len(element.choices)):
            vertical_position = (current_vertical_position * DEFAULT_CHEVRON_HEIGHT) + i * DEFAULT_CHEVRON_HEIGHT
            length_of_choice = len(element.choices[i])
       
            horizontal_start_position = (element.position_start * DEFAULT_CHEVRON_LENGTH) + 1.25 + margin_length + (((element.position_end - element.position_start) + 1) * (sub_default_chevron_lenght) - (length_of_choice * sub_default_chevron_lenght + margin_length)) / 2
            for j in range(len(element.choices[i])):
                label = str(element.choices[i][j])
                label = label + " (" + str(element.frequencies[i]) + ")"
                ax.text(horizontal_start_position + j * sub_default_chevron_lenght + 2.0, vertical_position + margin_height + 0.5 * sub_default_chevron_heigth - 0.3, label, zorder = 10)
                ax.add_patch(patches.PathPatch(__chevron_at_position(horizontal_start_position + j * sub_default_chevron_lenght, vertical_position + margin_height, sub_default_chevron_lenght/DEFAULT_CHEVRON_LENGTH, sub_default_chevron_heigth), facecolor = color, lw = 1.3, ls = line_style, zorder = 7))

        return ax  


def scale_lightness(rgb, scale_l):
    import colorsys
    h, l, s = colorsys.rgb_to_hls(*rgb)
    return colorsys.hls_to_rgb(h, min(1, l * scale_l), s = s)


def visualize_super_variant_summarization(summarization):
    if(len(summarization.lanes) > 20):
        print("Summarization too large, cannot be visualized.")
        return
     
    # Defining the colors and heights for each lane
    all_colors = [(1,0.71,0.44), (0.56,0.81,0.56), (0.38,0.57,0.8), (1,0.87,143), (0.56,0.89,0.97)]
    objects = list(summarization.object_types)
    objects.sort()
    number_of_object_types = len(objects)
    type_colors = all_colors[:number_of_object_types]
    color_assignment_types = dict(zip(objects, type_colors))

    lane_properties = dict()
    maximal_lane_length = 1
    for type in summarization.object_types:
        type_lanes = [lane for lane in summarization.lanes if lane.object_type == type]
        color = color_assignment_types[type]
        offset = 0.15
        scale = 0.9
        for lane in type_lanes:
            lane_properties[lane.lane_id] = dict()
            lane_properties[lane.lane_id]["Color"] = scale_lightness(color, scale)
            scale += offset
            vertical_height = 1
            frequency = 0
            for elem in lane.elements:
                if (isinstance(elem, SVD.GeneralChoiceStructure)):
                    vertical_height = max(vertical_height, len(elem.choices))
                    maximal_lane_length = max(maximal_lane_length, elem.position_end)
                else:
                    maximal_lane_length = max(maximal_lane_length, elem.position)
                    frequency = elem.frequency
            lane_properties[lane.lane_id]["Height"] = vertical_height
            lane_properties[lane.lane_id]["Frequency"] = frequency

    
    fig, ax = plt.subplots()
    current_vertical_position = 0
    for i in range(len(summarization.lanes)):
        color = lane_properties[summarization.lanes[i].lane_id]["Color"]
        ax.text(-10, current_vertical_position * DEFAULT_CHEVRON_HEIGHT + 0.5 * lane_properties[summarization.lanes[i].lane_id]["Height"] * DEFAULT_CHEVRON_HEIGHT - 0.3, summarization.lanes[i].cardinality, zorder = 10)
        ax.text(-7.5, current_vertical_position * DEFAULT_CHEVRON_HEIGHT + 0.5 * lane_properties[summarization.lanes[i].lane_id]["Height"] * DEFAULT_CHEVRON_HEIGHT - 0.3, summarization.lanes[i].lane_name, zorder = 10)
        ax.add_patch(patches.Rectangle((-8.0, current_vertical_position * DEFAULT_CHEVRON_HEIGHT), (maximal_lane_length+2) * DEFAULT_CHEVRON_LENGTH, lane_properties[summarization.lanes[i].lane_id]["Height"] * DEFAULT_CHEVRON_HEIGHT, color = color, alpha = 0.8, zorder = 0))
        for elem in summarization.lanes[i].elements:
            if (isinstance(elem,SVD.InteractionConstruct)):
                ax = __interaction_activity_chevron(ax, summarization.lanes[i].lane_id, elem, lane_properties, summarization.interaction_points, current_vertical_position)
            else:
                ax = __summarized_activity_chevron(ax, elem, lane_properties[summarization.lanes[i].lane_id], color, current_vertical_position)
        current_vertical_position += lane_properties[summarization.lanes[i].lane_id]["Height"]

    ax.set_aspect('equal')
    ax.set_xlim(-10, (maximal_lane_length+1)*DEFAULT_CHEVRON_LENGTH+2)
    ax.set_ylim(-2, current_vertical_position*DEFAULT_CHEVRON_HEIGHT+2)
    plt.axis('off')
    plt.show()

