import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from matplotlib import colors

import Input_Extraction_Definition as IED

DEFAULT_CHEVRON_LENGTH = 15.
DEFAULT_CHEVRON_HEIGHT = 4.

def __chevron_at_position( horizontal_index, vertical_index, length, height):
    
    from matplotlib.path import Path
    verts = [
       (horizontal_index, vertical_index),  # Left bottom coner
       (horizontal_index + DEFAULT_CHEVRON_LENGTH * length, vertical_index),  # Right bottom corner
       (horizontal_index + DEFAULT_CHEVRON_LENGTH * length + 1.2, vertical_index + height/2), # Outer tip of chevron
       (horizontal_index + DEFAULT_CHEVRON_LENGTH * length, vertical_index + height),  # Right top coner
       (horizontal_index, vertical_index + height),  # Left bottom coner
       (horizontal_index + 1.2, vertical_index + height/2), # Inner top of chevron
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


def __activity_chevron(ax, activity, horizontal_index, vertical_index, color):

    from matplotlib.path import Path
    import matplotlib.patches as patches

    ax.text(horizontal_index * DEFAULT_CHEVRON_LENGTH + 2.0, vertical_index * DEFAULT_CHEVRON_HEIGHT + 0.3 * DEFAULT_CHEVRON_HEIGHT, activity, zorder = 10)
    ax.add_patch(patches.PathPatch(__chevron_at_position(horizontal_index * DEFAULT_CHEVRON_LENGTH, vertical_index * DEFAULT_CHEVRON_HEIGHT, 1, DEFAULT_CHEVRON_HEIGHT), facecolor = color, lw = 1.3, ls = '-', zorder = 5))
    return ax  

def __interaction_activity_chevron(ax, activity, horizontal_index, vertical_index, colors, interaction_point):

    from matplotlib.path import Path
    import matplotlib.patches as patches

    number_sub_chevrons = len(interaction_point.interaction_lanes)
    length_sub_chevron = (1/number_sub_chevrons)

  
    ax.text(horizontal_index * DEFAULT_CHEVRON_LENGTH + 2.0, vertical_index * DEFAULT_CHEVRON_HEIGHT + 0.3 * DEFAULT_CHEVRON_HEIGHT, activity, zorder = 10)

    for i in range(len(interaction_point.interaction_lanes)):
        ax.add_patch(patches.PathPatch(__chevron_at_position(horizontal_index * DEFAULT_CHEVRON_LENGTH + i*length_sub_chevron*DEFAULT_CHEVRON_LENGTH, vertical_index * DEFAULT_CHEVRON_HEIGHT, length_sub_chevron, DEFAULT_CHEVRON_HEIGHT), facecolor = colors[interaction_point.interaction_lanes[i]], lw = 0, ls = '-', zorder = 5))
    ax.add_patch(patches.PathPatch(__chevron_at_position(horizontal_index * DEFAULT_CHEVRON_LENGTH, vertical_index * DEFAULT_CHEVRON_HEIGHT, 1, DEFAULT_CHEVRON_HEIGHT), facecolor="None", lw = 1.3, ls = '-', zorder = 7))
    return ax


def scale_lightness(rgb, scale_l):
    import colorsys
    h, l, s = colorsys.rgb_to_hls(*rgb)
    return colorsys.hls_to_rgb(h, min(1, l * scale_l), s = s)


def visualize_variant(variant):

    if(len(variant.lanes) > 20):
        print("Summarization too large, cannot be visualized.")
        return
     
    # Defining the colors and heights for each lane
    all_colors = ['orange','limegreen', 'cornflowerblue', 'gold', 'crimson']
    objects = list(variant.object_types)
    objects.sort()
    number_of_object_types = len(objects)
    type_colors = all_colors[:number_of_object_types]
    color_assignment_types = dict(zip(objects, type_colors))
    color_assignment_lanes = dict()
    maximal_lane_length = 1
    for type in variant.object_types:
        type_lanes = [lane for lane in variant.lanes if lane.object_type == type]
        color = colors.to_rgb(color_assignment_types[type])
        offset = 0.15
        scale = 0.9
        for lane in type_lanes:
            color_assignment_lanes[lane.lane_id] = scale_lightness(color, scale)
            scale += offset
            maximal_lane_length = max(maximal_lane_length, max(lane.horizontal_indices))

    
    fig, ax = plt.subplots()
    current_vertical_position = 0
    for i in range(len(variant.lanes)):
        color = color_assignment_lanes[variant.lanes[i].lane_id]
        ax.text(-7.5, current_vertical_position * DEFAULT_CHEVRON_HEIGHT + 0.3 * DEFAULT_CHEVRON_HEIGHT, variant.lanes[i].lane_name, zorder = 10)
        ax.add_patch(patches.Rectangle((-8.0, current_vertical_position * DEFAULT_CHEVRON_HEIGHT), (maximal_lane_length+2) * DEFAULT_CHEVRON_LENGTH, DEFAULT_CHEVRON_HEIGHT, color = color, alpha = 0.8, zorder = 0))
        for j in range(len(variant.lanes[i].horizontal_indices)):
            is_interacting_activity, interaction_point = IED.is_interaction_point(variant.interaction_points, variant.lanes[i].lane_id, variant.lanes[i].horizontal_indices[j]) 
            if (is_interacting_activity):
                ax = __interaction_activity_chevron(ax, variant.lanes[i].activities[j], variant.lanes[i].horizontal_indices[j], current_vertical_position, color_assignment_lanes, interaction_point)
            else:
                ax = __activity_chevron(ax, variant.lanes[i].activities[j], variant.lanes[i].horizontal_indices[j], current_vertical_position, color)
        current_vertical_position += 1

    ax.set_aspect('equal')
    ax.set_xlim(-10, (maximal_lane_length + 1)*DEFAULT_CHEVRON_LENGTH+2)
    ax.set_ylim(-2, current_vertical_position*DEFAULT_CHEVRON_HEIGHT+2)
    plt.axis('off')
    plt.show()
