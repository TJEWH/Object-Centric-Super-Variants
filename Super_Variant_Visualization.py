import matplotlib.pyplot as plt
import matplotlib.patches as patches
import Super_Variant_Definition as SVD
import Input_Extraction_Definition as IED

DEFAULT_CHEVRON_LENGTH = 15.
DEFAULT_CHEVRON_HEIGHT = 6.

def visualize_super_variant(super_variant, suppression_char = "*"):
    '''
    Visualizes a Super Variant using sequentially aligned chevrons.
    :param super_variant: The Super Variant that should be visualized
    :type super_variant: SummarizedVariant
    :param suppression_char: The character used to suppress cardinalities greater 1
    :type suppression_char: str
    '''
    if(len(super_variant.lanes) > 20):
        print("Summarization too large, cannot be visualized.")
        return
     
    else:
        fig, ax = plt.subplots()
        ax, width, height = arrange_super_variant(super_variant, ax, 0, 0, suppression_char)
        ax.set_aspect('equal')
        ax.set_xlim(-15, width + 2)
        ax.set_ylim(-2, height + 2)
        plt.axis('off')
        plt.show()


def visualize_variant(variant):
    '''
    Visualizes a variant using sequentially aligned chevrons.
    :param ariant: The variant that should be visualized
    :type variant: ExtractedVariant
    '''
    if(len(variant.lanes) > 20):
        print("Summarization too large, cannot be visualized.")
        return
     
    else:
        super_variant = variant.to_super_variant()
        fig, ax = plt.subplots()
        ax, width, height =  arrange_super_variant(super_variant, ax, 0, 0, "")
        ax.set_aspect('equal')
        ax.set_xlim(-15, width + 2)
        ax.set_ylim(-2, height + 2)
        plt.axis('off')
        plt.show()


def arrange_super_variant(super_variant, ax, vertical_start_position, horizontal_start_position, suppression_char):
    '''
    Generates the visualization of a Super Variant.
    :param super_variant: The Super Variant that should be visualized
    :type super_variant: SummarizedVariant
    :param ax: The visualization region in which the Super Variant should be visualized
    :type ax: axes
    :param vertical_start_position: The y-value of the lower-left corner of the first activity chevron
    :type vertical_start_position: float
    :param horizontal_start_position: The x-value of the lower-left corner of the first activity chevron
    :type horizontal_start_position: float
    :param suppression_char: The character used to suppress cardinalities greater 1
    :type suppression_char: str
    :return: The visualization region with the added Super Variant visualization elements as well as its width and height
    :rtype: axes, float, float
    '''
    import copy
    all_colors = [(1,0.71,0.44), (0.56,0.81,0.56), (0.38,0.57,0.8), (1,0.87,143), (0.56,0.89,0.97)]
    objects = list(super_variant.object_types)
    objects.sort()
    number_of_object_types = len(objects)
    type_colors = all_colors[:number_of_object_types]
    color_assignment_types = dict(zip(objects, type_colors))

    lane_properties = dict()
    maximal_lane_length = 1
    for type in super_variant.object_types:
        type_lanes = [lane for lane in super_variant.lanes if lane.object_type == type]
        color = color_assignment_types[type]
        offset = 0.09
        scale = 0.9
        for lane in type_lanes:
            lane_properties[lane.lane_id] = dict()
            lane_properties[lane.lane_id]["Color"] = scale_lightness(color, scale)
            scale += offset
            vertical_height = 1
            for elem in lane.elements:
                if (isinstance(elem, SVD.GeneralChoiceStructure)):
                    vertical_height = max(vertical_height, elem.get_vertical_height())
                    maximal_lane_length = max(maximal_lane_length, elem.index_end)
                else:
                    maximal_lane_length = max(maximal_lane_length, elem.index)
            lane_properties[lane.lane_id]["Height"] = vertical_height
            lane_properties[lane.lane_id]["IsOptional"] = isinstance(lane, SVD.OptionalSuperLane)

    
    current_vertical_position = vertical_start_position

    for i in range(len(super_variant.lanes)):

        lane_id = super_variant.lanes[i].lane_id
        color = lane_properties[lane_id]["Color"]
        if(super_variant.lanes[i].cardinality != "1"):
            cardinality = suppression_char
        else:
            cardinality = super_variant.lanes[i].cardinality

        ax.text(-15 + horizontal_start_position, current_vertical_position * DEFAULT_CHEVRON_HEIGHT + 0.5 * lane_properties[lane_id]["Height"] * DEFAULT_CHEVRON_HEIGHT - 0.3, cardinality, zorder = 10)
        ax.text(-12.5 + horizontal_start_position, current_vertical_position * DEFAULT_CHEVRON_HEIGHT + 0.5 * lane_properties[lane_id]["Height"] * DEFAULT_CHEVRON_HEIGHT - 0.3, super_variant.lanes[i].lane_name, zorder = 10)
        
        if(lane_properties[lane_id]["IsOptional"]):
            ax.add_patch(patches.Rectangle((-13 + horizontal_start_position, current_vertical_position * DEFAULT_CHEVRON_HEIGHT), (maximal_lane_length+2) * DEFAULT_CHEVRON_LENGTH, lane_properties[lane_id]["Height"] * DEFAULT_CHEVRON_HEIGHT, color = color, alpha = 0.8, zorder = 0, hatch='///'))
        else:
            ax.add_patch(patches.Rectangle((-13 + horizontal_start_position, current_vertical_position * DEFAULT_CHEVRON_HEIGHT), (maximal_lane_length+2) * DEFAULT_CHEVRON_LENGTH, lane_properties[lane_id]["Height"] * DEFAULT_CHEVRON_HEIGHT, color = color, alpha = 0.8, zorder = 0))
        
        properties = copy.deepcopy(lane_properties)
        ax = __visualize_lane_elements(ax, lane_id, super_variant.lanes[i].elements, properties, super_variant.interaction_points, current_vertical_position, horizontal_start_position)
        current_vertical_position += lane_properties[lane_id]["Height"]
    

    ax.text(-13 + horizontal_start_position, current_vertical_position * DEFAULT_CHEVRON_HEIGHT + 0.7, "Frequency: " + str(round(super_variant.frequency, 3)), zorder = 10)

    width = (maximal_lane_length + 1) * DEFAULT_CHEVRON_LENGTH - horizontal_start_position
    height = current_vertical_position * DEFAULT_CHEVRON_HEIGHT - vertical_start_position
    return ax, width, height

def __visualize_lane_elements(ax, lane, elements, lane_properties, interaction_points, current_vertical_position, current_horizontal_position, chevron_length = DEFAULT_CHEVRON_LENGTH, chevron_height = DEFAULT_CHEVRON_HEIGHT, offset = 0, frequency = False, fontsize = 9, original_lane = None, original_lane_properties = None):
    '''
    Generates the chevrons for a single SuperLane at a given position.
    :param ax: The visualization region in which the Super Variant should be visualized
    :type ax: axes
    :param lane: The id of the lane that contains the given elements, used as a key for the dictionary
    :type lane: int
    :param element: The elements that should be visualized
    :type element: list of type SummarizationElement
    :param lane_properties: Relevent "Height", "Color" and "IsOptional" information for each lane in the Super Variant
    :type lane_properties: dict
    :param interaction_points: The interaction points involved in the Super Variant
    :type interaction_points: list of type InteractionPoint
    :param vertical_start_position: The y-value of the lower-left corner of the first activity chevron
    :type vertical_start_position: float
    :param horizontal_start_position: The x-value of the lower-left corner of the first activity chevron
    :type horizontal_start_position: float
    :param chevron_length: The length of one unit of a chevron
    :type chevron_length: float
    :param chevron_height: The hight of one unit of a chevron
    :type chevron_height: float
    :param offset: The offset substracted from the element indices
    :type offset: int
    :param frequency: Whether the frequency of the elements should be displayed
    :type frequency: bool
    :param fontsize: The fontsize for the activity label
    :type fontsize: int
    :return: The visualization region with the added sequential activity chevrons
    :rtype: axes
    '''
    import copy

    if(original_lane == None):
        original_lane = lane
    if(original_lane_properties == None):
        original_lane_properties = lane_properties

    for element in elements:
        properties = copy.deepcopy(lane_properties)
        if(isinstance(element, SVD.InteractionConstruct)):
            ax = __interaction_activity_chevron(ax, lane, element, element.index - offset, properties, interaction_points, current_vertical_position, current_horizontal_position, chevron_length, chevron_height, frequency, fontsize, original_lane, original_lane_properties)
        elif(isinstance(element, SVD.CommonConstruct)):
            ax = __common_activity_chevron(ax, lane, element, element.index - offset, properties, current_vertical_position, current_horizontal_position, chevron_length, chevron_height, frequency, fontsize)
        else:
            ax = __choice_structure_chevron(ax, lane, element, element.index_start - offset, properties, interaction_points, current_vertical_position, current_horizontal_position, chevron_length, chevron_height, fontsize, original_lane, original_lane_properties)
    return ax


def __interaction_activity_chevron(ax, lane, element, index, lane_properties, interaction_points, current_vertical_position, current_horizontal_position, chevron_length, chevron_height, frequency, fontsize, original_lane, original_lane_properties, overall_line_style = '-'):
    '''
    Generates the chevrons for a single InteractionConstruct element of a lane.
    :param ax: The visualization region in which the chevron should be visualized
    :type ax: axes
    :param lane: The id of the lane that contains the given element, used as a key for the dictionary
    :type lane: int
    :param element: The element that should be visualized
    :type element: InteractionConstruct
    :param index: The horizontal index of the element
    :type index: int
    :param lane_properties: Relevent "Height", "Color" and "IsOptional" information for each lane in the Super Variant
    :type lane_properties: dict
    :param interaction_points: The interaction points involved in the Super Variant
    :type interaction_points: list of type InteractionPoint
    :param vertical_start_position: The y-value offset for the position
    :type vertical_start_position: float
    :param horizontal_start_position: The x-value offset for the position
    :type horizontal_start_position: float
    :param chevron_length: The length of one unit of a chevron
    :type chevron_length: float
    :param chevron_height: The hight of one unit of a chevron
    :type chevron_height: float
    :param frequency: The frequency label of the activity
    :type frequency: str
    :param fontsize: The fontsize for the activity label
    :type fontsize: bool
    :param overall_line_style: The line style of the chevron outline
    :type overall_line_style: str
    :return: The visualization region with the added chevron
    :rtype: axes
    '''
    import matplotlib.patches as patches
    if(lane_properties[lane]["IsOptional"]):
        overall_line_style = '--'


    is_interacting, interaction_point = IED.is_interaction_point(interaction_points, original_lane, element.position)
    
    interacting_lanes = interaction_point.interaction_lanes

    number_sub_chevrons = len(interacting_lanes)
    length_sub_chevron = (1 / number_sub_chevrons)
   
    interacting_lanes.sort(key = lambda x: original_lane_properties[x]["Color"])

    label = element.activity
    offset = 0.3

    possible_splitting_indices = []
    if(len(label) > 14):
        for i in range(len(label)):
            if (label[i] == " "):
                possible_splitting_indices.append(i)
    possible_splitting_indices.append(len(label))
    splitting_index = min(possible_splitting_indices, key = lambda x: abs(x - (len(label)/2)))
    label = label[:splitting_index] + "\n" + label[splitting_index + 1:]

    longest_section = 0
    for i in range(len(label.split("\n"))):
        longest_section = max(longest_section, len(label.split("\n")[i]))
    sizing_factor = min(14 / longest_section , 1)
    if (label[-1] == "\n"):
        label = label[:-1]
    else:
        offset += 0.7

    if(frequency):
        label += "\n " + str(round(element.frequency * 100, 2)) + "%"
        offset += 0.7
    ax.text(index * chevron_length+ 2.0 + current_horizontal_position, current_vertical_position * chevron_height + 0.5 * chevron_height * lane_properties[lane]["Height"] - offset, label, zorder = 15, fontsize = fontsize * sizing_factor)

    for i in range(len(interacting_lanes)):
        color = original_lane_properties[interacting_lanes[i]]["Color"]
        ax.add_patch(patches.PathPatch(__chevron_at_position(current_horizontal_position + index * chevron_length + i * length_sub_chevron * chevron_length, current_vertical_position * chevron_height, length_sub_chevron * chevron_length/DEFAULT_CHEVRON_LENGTH, lane_properties[lane]["Height"]  * chevron_height), facecolor = color, lw = 0, ls = overall_line_style, zorder = 10))
    ax.add_patch(patches.PathPatch(__chevron_at_position(current_horizontal_position + index * chevron_length, current_vertical_position * chevron_height, chevron_length/DEFAULT_CHEVRON_LENGTH, lane_properties[lane]["Height"]  * chevron_height), facecolor = "None", lw = 1.3, ls = overall_line_style, zorder = 12))
    
    return ax

def __common_activity_chevron(ax, lane, element, index, lane_properties, current_vertical_position, current_horizontal_position, chevron_length, chevron_height, frequency, fontsize, overall_line_style = '-'):
    '''
    Generates the chevrons for a single CommonConstruct element of a lane.
    :param ax: The visualization region in which the chevron should be visualized
    :type ax: axes
    :param lane: The id of the lane that contains the given element, used as a key for the dictionary
    :type lane: int
    :param element: The element that should be visualized
    :type element: CommonConstruct
    :param index: The horizontal index of the element
    :type index: int
    :param lane_properties: Relevent "Height", "Color" and "IsOptional" information for each lane in the Super Variant
    :type lane_properties: dict
    :param vertical_start_position: The y-value offset for the position
    :type vertical_start_position: float
    :param horizontal_start_position: The x-value offset for the position
    :type horizontal_start_position: float
    :param chevron_length: The length of one unit of a chevron
    :type chevron_length: float
    :param chevron_height: The hight of one unit of a chevron
    :type chevron_height: float
    :param frequency: The frequency label of the activity
    :type frequency: bool
    :param fontsize: The fontsize for the activity label
    :type fontsize: int
    :param overall_line_style: The line style of the chevron outline
    :type overall_line_style: str
    :return: The visualization region with the added chevron
    :rtype: axes
    '''
    import matplotlib.patches as patches

    if(lane_properties[lane]["IsOptional"]):
        overall_line_style = '--'
        
    label = element.activity
    offset = 0.3

    possible_splitting_indices = []
    if(len(label) > 14):
        for i in range(len(label)):
            if (label[i] == " "):
                possible_splitting_indices.append(i)
    possible_splitting_indices.append(len(label))
    splitting_index = min(possible_splitting_indices, key = lambda x: abs(x - (len(label)/2)))
    label = label[:splitting_index] + "\n" + label[splitting_index + 1:]

    longest_section = 0
    for i in range(len(label.split("\n"))):
        longest_section = max(longest_section, len(label.split("\n")[i]))
    sizing_factor = min(14 / longest_section , 1)
    if (label[-1] == "\n"):
        label = label[:-1]
    else:
        offset += 0.7

    if(frequency):
        label += "\n " + str(round(element.frequency * 100, 2)) + "%"
        offset += 0.7
    ax.text(current_horizontal_position + index * chevron_length + 2.0, current_vertical_position * chevron_height + 0.5 * chevron_height * lane_properties[lane]["Height"] - offset, label, zorder = 15, fontsize = fontsize*sizing_factor)
    ax.add_patch(patches.PathPatch(__chevron_at_position(current_horizontal_position + index * chevron_length, current_vertical_position * chevron_height, chevron_length/DEFAULT_CHEVRON_LENGTH, lane_properties[lane]["Height"]  * chevron_height), facecolor = lane_properties[lane]["Color"], lw = 1.3, ls = overall_line_style, zorder = 10))
    return ax

def __choice_structure_chevron(ax, lane, element, index, lane_properties, interaction_points, current_vertical_position, current_horizontal_position, chevron_length, chevron_height, fontsize, original_lane, original_lane_properties, overall_line_style = '-'):
    '''
    Generates the chevrons for a single GenericChoiceStructure element of a lane.
    :param ax: The visualization region in which the chevron should be visualized
    :type ax: axes
    :param lane: The id of the lane that contains the given element, used as a key for the dictionary
    :type lane: int
    :param element: The element that should be visualized
    :type element: GenericChoiceStructure
    :param index: The horizontal index of the element
    :type index: int
    :param lane_properties: Relevent "Height", "Color" and "IsOptional" information for each lane in the Super Variant
    :type lane_properties: dict
    :param interaction_points: The interaction points involved in the Super Variant
    :type interaction_points: list of type InteractionPoint
    :param vertical_start_position: The y-value offset for the position
    :type vertical_start_position: float
    :param horizontal_start_position: The x-value offset for the position
    :type horizontal_start_position: float
    :param chevron_length: The length of one unit of a chevron
    :type chevron_length: float
    :param chevron_height: The hight of one unit of a chevron
    :type chevron_height: float
    :param fontsize: The fontsize for the activity label
    :type fontsize: int
    :param overall_line_style: The line style of the chevron outline
    :type overall_line_style: str
    :return: The visualization region with the added chevron
    :rtype: axes
    '''
    import matplotlib.patches as patches

    if(lane_properties[lane]["IsOptional"]):
        overall_line_style = '--'


    if(isinstance(element, SVD.OptionalConstruct)):
        margin_length = 0.0
    else:
        margin_length = 0.3

    print(element)
    print(lane_properties[lane]["Height"])
    margin_height = chevron_height * 1/12
    
    offset = element.index_start - index

    ax.add_patch(patches.PathPatch(__chevron_at_position(current_horizontal_position + index * chevron_length, current_vertical_position * chevron_height, ((element.index_end - element.index_start) + 1) * chevron_length/DEFAULT_CHEVRON_LENGTH, lane_properties[lane]["Height"]  * chevron_height), facecolor = "None", lw = 1.3, ls = overall_line_style, zorder = 5))
    
    overall_line_style = "-"

    choice_properties = dict()
    accumulated_height = 0
    for choice in element.choices:

        choice_properties[choice.lane_id] = dict()
        choice_properties[choice.lane_id]["Color"] = lane_properties[lane]["Color"]
        choice_properties[choice.lane_id]["IsOptional"] = isinstance(element, SVD.OptionalConstruct)
        choice_properties[choice.lane_id]["Frequency"] = choice.frequency

        vertical_height = 1
        for elem in choice.elements:
            if (isinstance(elem, SVD.GeneralChoiceStructure)):
                vertical_height = max(vertical_height, elem.get_vertical_height())

        choice_properties[choice.lane_id]["Height"] = vertical_height
        accumulated_height += vertical_height
    
    height_factor = (lane_properties[lane]["Height"] / accumulated_height)

    sub_default_chevron_length = ((((element.index_end - element.index_start) + 1) * chevron_length) - 2) / ((element.index_end - element.index_start) + 1)
    sub_default_chevron_length -= margin_length / ((element.index_end - element.index_start) + 1)

    sub_default_chevron_height = chevron_height * height_factor
    sub_default_chevron_height -=  1/6 * chevron_height

    vertical_half = 1/2 * lane_properties[lane]["Height"]  * chevron_height
    chevron_vertical_half = current_vertical_position * chevron_height + vertical_half

    vertical_position = (current_vertical_position * chevron_height)
    for i in range(len(element.choices)):

        choice = element.choices[i].lane_id

        if (vertical_position != current_vertical_position * chevron_height):
            if(vertical_position <= chevron_vertical_half):
                line_offset = (vertical_position - current_vertical_position * chevron_height)/vertical_half * 1.25
            else:
                line_offset = 1.25 - (vertical_position - chevron_vertical_half)/vertical_half * 1.25
            ax.add_patch(patches.PathPatch(__line_at_position(current_horizontal_position  + index * chevron_length + line_offset, vertical_position, ((element.index_end - element.index_start) + 1) * chevron_length / DEFAULT_CHEVRON_LENGTH), lw = 1.1, ls = overall_line_style, zorder = 15))

        horizontal_start_position = current_horizontal_position + (index * chevron_length) + 1 + margin_length 

        ax = __visualize_lane_elements(ax, choice, element.choices[i].elements, choice_properties, interaction_points, ((vertical_position + margin_height) / sub_default_chevron_height), horizontal_start_position, chevron_length = sub_default_chevron_length, chevron_height = sub_default_chevron_height, offset = offset + index, frequency = True, fontsize = fontsize * ((sub_default_chevron_length - 2) / DEFAULT_CHEVRON_LENGTH) + 1, original_lane = original_lane, original_lane_properties = original_lane_properties)
        vertical_position += choice_properties[choice]["Height"] * chevron_height *height_factor

    return ax  



def scale_lightness(rgb, scale_l):
    '''
    Scales the lightness of a RGB color given a lightness factor.
    :param rgb: The color that is scaled
    :type rgb: tuple
    :param scale_l: The lightness scaling factor
    :type scale_l: float
    :return: The scaled color
    :rtype: tuple
    '''
    import colorsys
    h, l, s = colorsys.rgb_to_hls(*rgb)
    return colorsys.hls_to_rgb(h, min(1, l * scale_l), s = s)


def __chevron_at_position(horizontal_index, vertical_index, length, height):
    '''
    Generates a vector drawing of a chevron at a given position with a given length and height.
    :param horizontal_index: The x-value of the position
    :type horizontal_index: float
    :param vertical_index: The y-value of the position
    :type vertical_index: float
    :param length: A factor scaling the length of the chevron
    :type length: int
    :param height: A factor scaling the height of the chevron
    :type height: int
    :return: The chevron as a path instance
    :rtype: path
    '''
    from matplotlib.path import Path
    verts = [
       (horizontal_index, vertical_index),  # Left bottom coner
       (horizontal_index + DEFAULT_CHEVRON_LENGTH * length, vertical_index),  # Right bottom corner
       (horizontal_index + DEFAULT_CHEVRON_LENGTH * length + 1.25, vertical_index + height / 2), # Outer tip of chevron
       (horizontal_index + DEFAULT_CHEVRON_LENGTH * length, vertical_index + height),  # Right top coner
       (horizontal_index, vertical_index + height),  # Left bottom coner
       (horizontal_index + 1.25, vertical_index + height / 2), # Inner top of chevron
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


def __line_at_position(horizontal_index, vertical_index, length):
    '''
    Generates a vector drawing of a line at a given position with a given length.
    :param horizontal_index: The x-value of the position
    :type horizontal_index: float
    :param vertical_index: The y-value of the position
    :type vertical_index: float
    :param length: A factor scaling the length of the line
    :type length: int
    :return: The line as a path instance
    :rtype: path
    '''
    from matplotlib.path import Path
    verts = [
       (horizontal_index, vertical_index),
       (horizontal_index + DEFAULT_CHEVRON_LENGTH * length, vertical_index),
    ]

    codes = [
        Path.MOVETO,
        Path.LINETO,
    ]

    return Path(verts, codes)




