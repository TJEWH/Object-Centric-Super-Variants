import Super_Variant_Definition as SVD

DEFAULT_CHEVRON_LENGTH = 7.
DEFAULT_CHEVRON_HEIGHT = 4.

def chevron_at_position(vertical_index, horizontal_index, length, height):
    
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

def add_chevron_divider_full(vertical_index, horizontal_index, length):
    
    from matplotlib.path import Path
    verts = [
       (horizontal_index, vertical_index),  # Left starting point
       (horizontal_index + DEFAULT_CHEVRON_LENGTH * length, vertical_index),  # Right ending point
    ]

    codes = [
        Path.MOVETO,
        Path.LINETO,
    ]
    return Path(verts, codes)

def add_chevron_divider_dotted(vertical_index, horizontal_index, length):
    
    from matplotlib.path import Path
    total_distance = (DEFAULT_CHEVRON_LENGTH * length)/10
    dotted_distance = total_distance/3
    non_dotted_distance = 2*total_distance/3
    verts = [
       (horizontal_index, vertical_index),  # Left starting point
       (horizontal_index + non_dotted_distance, vertical_index),  
       (horizontal_index + total_distance, vertical_index),
       (horizontal_index + total_distance + non_dotted_distance, vertical_index),  
       (horizontal_index + 2*total_distance, vertical_index),
       (horizontal_index + 2*total_distance + non_dotted_distance, vertical_index),  
       (horizontal_index + 3*total_distance, vertical_index),
       (horizontal_index + 3*total_distance + non_dotted_distance, vertical_index),  
       (horizontal_index + 4*total_distance, vertical_index),
       (horizontal_index + 4*total_distance + non_dotted_distance, vertical_index),  
       (horizontal_index + 5*total_distance, vertical_index),
       (horizontal_index + 5*total_distance + non_dotted_distance, vertical_index),  
       (horizontal_index + 6*total_distance, vertical_index),
       (horizontal_index + 6*total_distance + non_dotted_distance, vertical_index),  
       (horizontal_index + 7*total_distance, vertical_index),
       (horizontal_index + 7*total_distance + non_dotted_distance, vertical_index),  
       (horizontal_index + 8*total_distance, vertical_index),
       (horizontal_index + 8*total_distance + non_dotted_distance, vertical_index),  
       (horizontal_index + 9*total_distance, vertical_index),
       (horizontal_index + 9*total_distance + non_dotted_distance, vertical_index),  
       (horizontal_index + 10*total_distance, vertical_index),
        
    ]

    codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.MOVETO,
        Path.LINETO,
        Path.MOVETO,
        Path.LINETO,
        Path.MOVETO,
        Path.LINETO,
        Path.MOVETO,
        Path.LINETO,
        Path.MOVETO,
        Path.LINETO,
        Path.MOVETO,
        Path.LINETO,
        Path.MOVETO,
        Path.LINETO,
        Path.MOVETO,
        Path.LINETO,
        Path.MOVETO,
        Path.LINETO,
        Path.MOVETO,
    ]
    return Path(verts, codes)

def activity_chevron(ax, activity, lane_property, color):
    
    import math
    from matplotlib.path import Path
    import matplotlib.patches as patches
    line_style = '-'
    label = activity[0]
    ax.text(activity[1][0][0]*DEFAULT_CHEVRON_LENGTH+2.5, lane_property[1]+(1/2)*lane_property[0] - 0.4, label)
    ax.add_patch(patches.PathPatch(chevron_at_position(lane_property[1], activity[1][0][0]*DEFAULT_CHEVRON_LENGTH, 1, lane_property[0]), facecolor=color, lw=2, ls = line_style))
    return ax  

def summarized_activity_chevron(ax, activity, lane_property, color):
    
    import math
    from matplotlib.path import Path
    import matplotlib.patches as patches
    line_style = '-'
    label = ""
    
    # Define label and line type for each type of construct
    if (type(activity[0]) == SVD.OptionalConstruct):
        line_style = '--'
        # Write each optional choice and seperate by a line
        is_choice = len(activity[0].options) >1
        if(is_choice):
            offset = lane_property[0]/len(activity[0].options)
            for i in range(len(activity[0].options)):
                label = activity[0].options[i]
                label = label + " (" + str(activity[0].frequencies[i]) + ")"
                ax.text(activity[1][0][0]*DEFAULT_CHEVRON_LENGTH+2.5, 1.5+lane_property[1]+offset*i, label)
                above_halfways = lane_property[1] + lane_property[1]+offset*i >= lane_property[1] + 0.5*lane_property[0]
                horizontal_shift = 0.1
                if(above_halfways):
                    ax.add_patch(patches.PathPatch(add_chevron_divider_dotted(lane_property[1] + lane_property[1]+offset*i, activity[1][0][0]*DEFAULT_CHEVRON_LENGTH+1.2-horizontal_shift*i,1),lw=2,zorder=10))
                else:
                    ax.add_patch(patches.PathPatch(add_chevron_divider_dotted(lane_property[1] + lane_property[1]+offset*i, activity[1][0][0]*DEFAULT_CHEVRON_LENGTH+horizontal_shift*i,1),lw=2,zorder=10))
        else:
            label = activity[0].options[0]
            label = label + " (" + str(activity[0].frequencies[0]) + ")"
            ax.text(activity[1][0][0]*DEFAULT_CHEVRON_LENGTH+2.5, lane_property[1]+(1/2)*lane_property[0] - 0.4, label)
        
    elif (type(activity[0]) == SVD.CommonConstruct):
        label = activity[0].activity
        label = label + " (" + str(lane_property[2]) + ")"
        ax.text(activity[1][0][0]*DEFAULT_CHEVRON_LENGTH+2.5, lane_property[1]+(1/2)*lane_property[0] - 0.4, label)
        
    else: 
        # Write each choice and seperate by a line
        offset = lane_property[0]/len(activity[0].choices)
        for i in range(len(activity[0].choices)):
            label = activity[0].choices[i]
            label = label + " (" + str(activity[0].frequencies[i]) + ")"
            ax.text(activity[1][0][0]*DEFAULT_CHEVRON_LENGTH+2.5, 1.5+lane_property[1]+offset*i, label)
            above_halfways = lane_property[1] + lane_property[1]+offset*i >= lane_property[1] + 0.5*lane_property[0]
            horizontal_shift = 0.1
            if(above_halfways):
                ax.add_patch(patches.PathPatch(add_chevron_divider_full(lane_property[1] + lane_property[1]+offset*i, activity[1][0][0]*DEFAULT_CHEVRON_LENGTH+1.2-horizontal_shift*i,1),lw=2,zorder=10))
            else:
                ax.add_patch(patches.PathPatch(add_chevron_divider_full(lane_property[1] + lane_property[1]+offset*i, activity[1][0][0]*DEFAULT_CHEVRON_LENGTH+horizontal_shift*i,1),lw=2,zorder=10))
    
    ax.add_patch(patches.PathPatch(chevron_at_position(lane_property[1], activity[1][0][0]*DEFAULT_CHEVRON_LENGTH, 1, lane_property[0]), facecolor=color, lw=2, ls = line_style))
    return ax  

def visualize_variant(variant):
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    import matplotlib.patches as patches
     
    # Defining the colors for each lane
    colors = ['peachpuff','palegoldenrod', 'thistle', 'plum', 'moccasin', 'lightgrey','palegreen', 'lightpink']
    number_of_lanes = len(variant[1].keys())
    colors = colors[:number_of_lanes]
    colors = dict(zip(variant[1].keys(), colors))
    interaction_point_color = 'orangered'
    
    # Determine the required height of each lane
    lane_properties = dict.fromkeys(variant[1].keys(), (DEFAULT_CHEVRON_HEIGHT, 0))    
    activities = variant[0]
    largest_horizontal_position = 0
    for i in range(len(activities)):
        largest_horizontal_position = max(largest_horizontal_position, activities[i][1][0][0])
    
    # Determining the resulting vertical position of the lane
    sum = 0
    largest_vertical_position = 0
    for key in lane_properties.keys():
        height = lane_properties[key][0]
        lane_properties[key] = (height, sum)
        sum += height
        largest_vertical_position = sum

    # Create chevrons for each activity
    fig, ax = plt.subplots()
    for i in range(len(activities)):
        # No interaction point
        if(len(activities[i][1][1]) == 1):
            ax = activity_chevron(ax, activities[i], lane_properties[activities[i][1][1][0]], colors[activities[i][1][1][0]])
        else:
            # Interaction point
            for j in range(len(activities[i][1][1])):
                ax = activity_chevron(ax, activities[i], lane_properties[activities[i][1][1][j]], interaction_point_color)
    
    # Define visible axis area            
    ax.set_xlim(-2, largest_horizontal_position*DEFAULT_CHEVRON_LENGTH+8.5)
    ax.set_ylim(-2, largest_vertical_position+1)

    ax.set_aspect('equal')
    plt.axis('off')
    plt.show()


def visualize_summarized_variant(variant):
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    import matplotlib.patches as patches
     
    # Defining the colors for each lane
    colors = ['peachpuff','palegoldenrod', 'thistle', 'plum', 'moccasin', 'lightgrey','palegreen', 'lightpink']
    number_of_lanes = len(variant[1].keys())
    colors = colors[:number_of_lanes]
    colors = dict(zip(variant[1].keys(), colors))
    interaction_point_color = 'orangered'
    
    # Determine the required height of each lane
    lane_properties = dict.fromkeys(variant[1].keys(), (DEFAULT_CHEVRON_HEIGHT, 0))

    activities = variant[0]
    largest_horizontal_position = 0
    for i in range(len(activities)):
        largest_horizontal_position = max(largest_horizontal_position, activities[i][1][0][0])
        if(type(activities[i][0]) == SVD.ChoiceConstruct):
            for key in activities[i][1][1]:
                lane_properties[key] = (max(lane_properties[key][0],len(activities[i][0].choices)*DEFAULT_CHEVRON_HEIGHT),0)
    
    for key in variant[1].keys():
        lane_properties[key] = lane_properties[key] + (variant[1][key][2],)
        
    # Determining the resulting vertical position of the lane
    sum = 0
    largest_vertical_position = 0
    for key in lane_properties.keys():
        height = lane_properties[key][0]
        frequency = lane_properties[key][2]
        lane_properties[key] = (height, sum, frequency)
        sum += height
        largest_vertical_position = sum

    # Create chevrons for each activity
    fig, ax = plt.subplots()
    for i in range(len(activities)):
        if(len(activities[i][1][1]) == 1):
            ax = summarized_activity_chevron(ax, activities[i], lane_properties[activities[i][1][1][0]], colors[activities[i][1][1][0]])
        else:
            for j in range(len(activities[i][1][1])):
                ax = summarized_activity_chevron(ax, activities[i], lane_properties[activities[i][1][1][j]], interaction_point_color)
    
    # Give overall frequencies 
    for key in variant[1].keys():
        if( lane_properties[key][2] > 1):
            ax.text(-2, lane_properties[key][1]+0.5*lane_properties[key][0], "n")
        else:
            ax.text(-2, lane_properties[key][1]+0.5*lane_properties[key][0], lane_properties[key][2])
            
        
    # Define visible axis area            
    ax.set_xlim(0, largest_horizontal_position*DEFAULT_CHEVRON_LENGTH+8.5)
    ax.set_ylim(0, largest_vertical_position+1)

    ax.set_aspect('equal')
    plt.axis('off')
    plt.show()