import Super_Variant_Visualization as SVV
'''
import matplotlib
matplotlib.use('TkAgg')'''
import matplotlib.pyplot as plt


MODE = SVV.Mode.LANE_FREQUENCY
TOOLTIPS = False
SAVE_FILE = False


def explore_hierarchy_bottom_up(super_variants):
    """
    Visualizes the layer of a generated Super Variant hierarchy, allowing the navigation among Super Variants within a layer and between the layers.
    :param super_variants: The Super Variant hierarchy with a key-value pair for each layer of the hierarchy. The key indicates the layer index
    :type super_variants: dict
    """
    layers = []
    for i in range(len(list(super_variants.keys()))):
        layers.append([super_variant[0] for super_variant in super_variants[i][0]])

    visualize_super_variant_layer(layers, 0, 0)


def explore_hierarchy_top_down(final_super_variant):
    """
    Visualizes a Super Variant and its two direct predecessors in the generation, allowing to navigate the Super Variants top-down from this starting point.
    :param final_super_variant: The starting Super Variant and its underlying direct predecessors
    :type final_super_variant: tuple
    """
    if final_super_variant[1] is None and final_super_variant[2] is None:
        SVV.visualize_super_variant(final_super_variant[0])
    else:
        visualize_single_summarization_step(final_super_variant[1], final_super_variant[2], final_super_variant[0])


def visualize_super_variant_layer(super_variants, current_layer, current_start_index):
    """
    Visualizes up to 3 Super Variants in a single layer of a generated Super Variant hierarchy, allowing the navigation among Super Variants within a layer and between the layers.
    :param super_variants: The Super Variant hierarchy with a key-value pair for each layer of the hierarchy. The key indicates the layer index
    :type super_variants: dict
    :param current_layer: The index of the layer currently visualized
    :type current_layer: int
    :param current_start_index: The index of the first Super Variant in the current layer that is to be visualized
    :type current_start_index: int
    """
    current_layer = max(0, current_layer)
    current_layer = min(len(super_variants) - 1, current_layer)
    current_super_variants = super_variants[current_layer]

    maximal_index = len(current_super_variants)
    start_index = current_start_index % maximal_index
    end_index = (current_start_index + 3) % maximal_index

    if maximal_index <= 3:
        visible_super_variants = current_super_variants

    elif end_index > start_index:
        visible_super_variants = current_super_variants[start_index: end_index]

    else:
        visible_super_variants = current_super_variants[start_index:] + current_super_variants[:end_index]

    number_of_plots = min(3, len(visible_super_variants))
    current_annotations = []

    if number_of_plots > 1:
        fig, ax = plt.subplots(1, number_of_plots, figsize=(20, 10), sharey=True)
        ax = list(ax)

        for i in range(number_of_plots):
            length = visible_super_variants[i].get_length()
            ax[i], width, height = SVV.arrange_super_variant(
                visible_super_variants[i],
                ax[i], 0, 0, "*",
                SVV.Mode.NO_FREQUENCY,
                4.5 * 3 / number_of_plots,
                4.5 * 3 / number_of_plots,
                int((13 * 9 / length)))

            ax[i].set_xlim(-15, width + 2)
            ax[i].set_ylim(-2, height + 2)

            ax[i].set_aspect('equal')
            ax[i].axis('off')

            if TOOLTIPS:
                append_annotation(
                    current_annotations,
                    ax[i],
                    "See Super Variant " + str(visible_super_variants[i].id) + " in Detail")
                ax[i].figure.texts.append(ax[i].texts.pop())

        ax = tuple(ax)
        fig.subplots_adjust(wspace=0.03, hspace=0)

    else:
        fig, ax = plt.subplots()
        if MODE == SVV.Mode.LANE_FREQUENCY:
            mode = SVV.Mode.ACTIVITY_FREQUENCY
        else:
            mode = MODE
        ax, width, height = SVV.arrange_super_variant(visible_super_variants[0], ax, 0, 0, "*", mode, 9, 9, 13)
        ax.set_aspect('equal')
        ax.set_xlim(-20, width + 2)
        ax.set_ylim(-2, height + 2)
        plt.axis('off')

    def hover_info(event):
        if number_of_plots > 1:
            for i in range(number_of_plots):
                annotate = current_annotations[i]
                annotation_visibility = annotate.get_visible()

                if event.inaxes == ax[i]:
                    event_position = (round(event.xdata), round(event.ydata))
                    annotate.xy = event_position
                    annotate.set_visible(True)
                    fig.canvas.draw_idle()

                elif annotation_visibility:
                    annotate.set_visible(False)
                    fig.canvas.draw_idle()

    def click(event):
        if number_of_plots > 1:
            for i in range(number_of_plots):
                if event.inaxes == ax[i]:
                    SVV.visualize_super_variant(visible_super_variants[i], mode=MODE)

    def go_left_right(event):
        if event.key == 'left':
            if len(current_super_variants) > 3:
                visualize_super_variant_layer(super_variants, current_layer, current_start_index - 1)
                plt.close(fig)

        elif event.key == 'right':
            if len(current_super_variants) > 3:
                visualize_super_variant_layer(super_variants, current_layer, current_start_index + 1)
                plt.close(fig)

        elif event.key == 'up':
            if current_layer < len(super_variants) - 1:
                visualize_super_variant_layer(super_variants, current_layer + 1, 0)
                plt.close(fig)

        elif event.key == 'down':
            if current_layer > 0:
                visualize_super_variant_layer(super_variants, current_layer - 1, 0)
                plt.close(fig)

    if TOOLTIPS:
        fig.canvas.mpl_connect('motion_notify_event', hover_info)

    fig.canvas.mpl_connect('button_press_event', click)
    fig.canvas.mpl_connect('key_press_event', go_left_right)

    manager = plt.get_current_fig_manager()
    # manager.pyplot_show()
    plt.show()

    if SAVE_FILE:
        fig.savefig("Visualizations/SuperVariantsLayer/Layer_" + str(current_layer) + "_" + str(start_index) + "_to_" +
                    str((current_start_index + 2) % maximal_index) + ".svg")


def visualize_single_summarization_step(super_variant_1, super_variant_2, new_super_variant):
    """
    Visualizes up to 3 Super Variants in a single layer of a generated Super Variant hierarchy, allowing the navigation among Super Variants within a layer and between the layers.
    :param super_variant_1: One of the direct predecessors of the given Super Variant
    :type super_variant_1: tuple
    :param super_variant_2: The other direct predecessors of the given Super Variant
    :type super_variant_2: tuple
    :param new_super_variant: The Super Variant as a result of the other given two Super Variants
    :type new_super_variant: tuple
    """

    if MODE == SVV.Mode.LANE_FREQUENCY:
        mode = SVV.Mode.ACTIVITY_FREQUENCY
    else:
        mode = MODE

    fig = plt.figure(figsize=(8, 2))
    current_annotations = []

    gs = fig.add_gridspec(2, 2)
    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[1, 1])
    ax3 = fig.add_subplot(gs[0, :])

    plot_axis(super_variant_1[0], ax1, mode, current_annotations, super_variant_2)
    plot_axis(super_variant_2[0], ax2, mode, current_annotations, super_variant_2)
    plot_axis(new_super_variant, ax3, mode, current_annotations)

    def hover_info(event):
        for i, ax in enumerate([ax1, ax2, ax3]):
            annotate = current_annotations[i]
            annotation_visibility = annotate.get_visible()

            if event.inaxes == ax:
                event_position = (round(event.xdata), round(event.ydata))
                annotate.xy = event_position
                annotate.set_visible(True)
                fig.canvas.draw_idle()
            elif annotation_visibility:
                annotate.set_visible(False)
                fig.canvas.draw_idle()

    def click(event):
        if event.inaxes == ax1:
            if super_variant_1[1] is not None and super_variant_1[2] is not None:
                visualize_single_summarization_step(
                    super_variant_1[1],
                    super_variant_1[2],
                    super_variant_1[0])
            else:
                SVV.visualize_super_variant(super_variant_1[0], mode=MODE)

        elif event.inaxes == ax2:
            if super_variant_2[1] is not None and super_variant_2[2] is not None:
                visualize_single_summarization_step(
                    super_variant_2[1],
                    super_variant_2[2],
                    super_variant_2[0])
            else:
                SVV.visualize_super_variant(super_variant_2[0], mode=MODE)

        elif event.inaxes == ax3:
            SVV.visualize_super_variant(new_super_variant, mode=MODE)

    fig.subplots_adjust(wspace=0.03, hspace=0)

    if TOOLTIPS:
        fig.canvas.mpl_connect('motion_notify_event', hover_info)
    fig.canvas.mpl_connect('button_press_event', click)

    manager = plt.get_current_fig_manager()
    # manager.pyplot_show()
    plt.show()

    if SAVE_FILE:
        fig.savefig("Visualizations/SuperVariantsCompositions/SuperVariant_" + str(new_super_variant.id) + "_from" +
                    str(super_variant_1[0].id) + "_and_" + str(super_variant_2[0].id) + ".svg")


def append_annotation(current_annotations, ax, message):
    current_annotations.append(
        ax.annotate(
            message,
            (0, 0),
            xytext=(0, 10),
            textcoords='offset points',
            color='w',
            ha='center',
            fontsize=8,
            fontweight='bold',
            bbox=dict(boxstyle='round, pad = .5', fc=(.1, .1, .1, .8), ec=(0., 0, 0), lw=0, zorder=50)))


def plot_axis(super_variant, ax, mode, current_annotations=None, sv_2=None):
    length = super_variant.get_length()
    cut_off_point = int(9 * 13 / length) if current_annotations else 13

    ax, width, height = SVV.arrange_super_variant(
        super_variant,
        ax, 0, 0, "*", mode, 7, 7,
        cut_off_point)

    ax.set_aspect('equal')
    ax.set_xlim(-15, width + 2)
    ax.set_ylim(-2, height + 2)
    ax.axis('off')

    if TOOLTIPS:
        message = "See Super Variant " + str(super_variant.id) + " in Detail"
        if sv_2:
            if sv_2[1] is not None and sv_2[2] is not None:
                message = "See Details on this Super Variants Summarization"
            append_annotation(current_annotations, ax, message)
            ax.figure.texts.append(message)
        else:
            append_annotation(current_annotations, ax, message)
            ax.figure.texts.append(message)
