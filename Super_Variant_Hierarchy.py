import Super_Variant_Visualization as SVV
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch

MODE = SVV.MODE.LANE_FREQUENCY

def explore_hierarchy_bottom_up(super_variants):
    visualize_super_variant_layer(super_variants, 0, 0)

def explore_hierarchy_top_down(super_variants):
    visualize_single_summarization_step()

def visualize_super_variant_layer(super_variants, current_layer, current_start_index):

    current_layer = max(0, current_layer)
    current_layer = min(len(super_variants), current_layer)
    current_super_variants = super_variants[current_layer]

    maximal_index = len(current_super_variants)
    start_index = current_start_index % maximal_index
    end_index = (current_start_index + 3) % maximal_index

    if(maximal_index <= 3):
        visible_super_variants = current_super_variants

    elif(end_index > start_index):
        visible_super_variants = current_super_variants[start_index: end_index]

    else: 
        visible_super_variants = current_super_variants[start_index:] + current_super_variants[:end_index]


    fig, ax = plt.subplots(1, 3, figsize=(20,10), sharey = True) 
    ax = list(ax)

    current_annotations = []

    for i in range(3):

        length = visible_super_variants[i].get_length()
        ax[i], width, height = SVV.arrange_super_variant(visible_super_variants[i], ax[i], 0, 0, "*", SVV.MODE.NO_FREQUENCY, 4.5 , 4.5, int(13 * 9 / length))
    
        ax[i].set_xlim(-15, width + 2)
        ax[i].set_ylim(-2, height + 2)

        ax[i].set_aspect('equal')
        ax[i].axis('off')

        current_annotations.append(ax[i].annotate("See Super Variant " + str(visible_super_variants[i].id) + " in Detail", (0, 0), xytext = (0, 10), textcoords = 'offset points', color = 'w', ha = 'center', fontsize = 8, fontweight = 'bold', 
                                                    bbox = dict(boxstyle='round, pad = .5', fc = (.1, .1, .1, .8), ec = (0., 0, 0), lw = 0, zorder = 50)))
        ax[i].figure.texts.append(ax[i].texts.pop())


    ax = tuple(ax)
    fig.subplots_adjust(wspace=0.03, hspace=0)


    def hover_info(event):

        for i in range(3):
            annotate = current_annotations[i]
            annotation_visbility = annotate.get_visible()
            if event.inaxes == ax[i]:
                            
                event_position = (round(event.xdata), round(event.ydata))
                annotate.xy = event_position
                annotate.set_visible(True)
                fig.canvas.draw_idle()

            elif(annotation_visbility):
                annotate.set_visible(False)
                fig.canvas.draw_idle()


    def click(event):

        for i in range(3):
            if event.inaxes == ax[i]:
                SVV.visualize_super_variant(visible_super_variants[i], mode = MODE)

    def go_left_right(event):

        if(event.key == 'a'):
            visualize_super_variant_layer(super_variants, current_layer, current_start_index - 1)
            plt.close(fig)

        elif(event.key == 'd'):
            visualize_super_variant_layer(super_variants, current_layer, current_start_index + 1)
            plt.close(fig)

        elif(event.key == 'w'):
            visualize_super_variant_layer(super_variants, current_layer + 1, 0)
            plt.close(fig)

        elif(event.key == 's'):
            visualize_super_variant_layer(super_variants, current_layer - 1, 0)
            plt.close(fig)
                
                            
    fig.canvas.mpl_connect('motion_notify_event', hover_info)
    fig.canvas.mpl_connect('button_press_event', click)
    fig.canvas.mpl_connect('key_press_event', go_left_right)

    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    plt.show()

    fig.savefig("SuperVariantsLayer/Layer_" + str(current_layer) + "_" + str(start_index) + "_to_" + str((current_start_index + 2) % maximal_index) + ".svg")


def visualize_single_summarization_step(super_variant_1, super_variant_2, new_super_variant):

    if(MODE == SVV.MODE.LANE_FREQUENCY):
        mode = SVV.MODE.ACTIVITY_FREQUENCY
    else:
        mode = MODE

    fig = plt.figure(figsize=(8,2))
    current_annotations = []

    gs = fig.add_gridspec(2,2)
    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[1, 1])
    ax3 = fig.add_subplot(gs[0, :])


    length1 = super_variant_1[0].get_length()
    ax1, width1, height1 = SVV.arrange_super_variant(super_variant_1[0], ax1, 0, 0, "*", mode, 7, 7, int(9 * 13 / length1))
    
    ax1.set_aspect('equal')
    ax1.set_xlim(-15, width1 + 2)
    ax1.set_ylim(-2, height1 + 2)
    ax1.axis('off')

    if(super_variant_1[1] != None and super_variant_1[2] != None):
        current_annotations.append(ax1.annotate("See Details on this Super Variants Summarization", (0, 0), xytext = (0, 10), textcoords = 'offset points', color = 'w', ha = 'center', fontsize = 8, fontweight = 'bold', 
                                                    bbox = dict(boxstyle='round, pad = .5', fc = (.1, .1, .1, .8), ec = (0., 0, 0), lw = 0, zorder = 50)))
    else:
        current_annotations.append(ax1.annotate("See Super Variant " + str(super_variant_1[0].id) + " in Detail", (0, 0), xytext = (0, 10), textcoords = 'offset points', color = 'w', ha = 'center', fontsize = 8, fontweight = 'bold', 
                                                    bbox = dict(boxstyle='round, pad = .5', fc = (.1, .1, .1, .8), ec = (0., 0, 0), lw = 0, zorder = 50)))
        
    ax1.figure.texts.append(ax1.texts.pop())

    length2 = super_variant_2[0].get_length()
    ax2, width2, height2 = SVV.arrange_super_variant(super_variant_2[0], ax2, 0, 0, "*", mode, 7, 7, int(9 * 13 / length2))
    
    ax2.set_aspect('equal')
    ax2.set_xlim(-15, width2 + 2)
    ax2.set_ylim(-2, height2 + 2)
    ax2.axis('off')

    if(super_variant_2[1] != None and super_variant_2[2] != None):
        current_annotations.append(ax2.annotate("See Details on this Super Variants Summarization", (0, 0), xytext = (0, 10), textcoords = 'offset points', color = 'w', ha = 'center', fontsize = 8, fontweight = 'bold', 
                                                    bbox = dict(boxstyle='round, pad = .5', fc = (.1, .1, .1, .8), ec = (0., 0, 0), lw = 0, zorder = 50)))
    else:
        current_annotations.append(ax2.annotate("See Super Variant " + str(super_variant_2[0].id) + " in Detail", (0, 0), xytext = (0, 10), textcoords = 'offset points', color = 'w', ha = 'center', fontsize = 8, fontweight = 'bold', 
                                                    bbox = dict(boxstyle='round, pad = .5', fc = (.1, .1, .1, .8), ec = (0., 0, 0), lw = 0, zorder = 50)))
        
    ax2.figure.texts.append(ax2.texts.pop())

    ax3, width3, height3 = SVV.arrange_super_variant(new_super_variant, ax3, 0, 0, "*", mode, 9, 9, 13)
    
    ax3.set_aspect('equal')
    ax3.set_xlim(-15, width3 + 2)
    ax3.set_ylim(-2, height3 + 2)
    ax3.axis('off')

    def hover_info(event):

        annotate = current_annotations[0]
        annotation_visbility = annotate.get_visible()
        if event.inaxes == ax1:
                            
            event_position = (round(event.xdata), round(event.ydata))
            annotate.xy = event_position
            annotate.set_visible(True)
            fig.canvas.draw_idle()

        elif(annotation_visbility):
            annotate.set_visible(False)
            fig.canvas.draw_idle()

        annotate = current_annotations[1]
        annotation_visbility = annotate.get_visible()
        if event.inaxes == ax2:
                            
            event_position = (round(event.xdata), round(event.ydata))
            annotate.xy = event_position
            annotate.set_visible(True)
            fig.canvas.draw_idle()

        elif(annotation_visbility):
            annotate.set_visible(False)
            fig.canvas.draw_idle()

    def click(event):

        if event.inaxes == ax1:
            if(super_variant_1[1] != None and super_variant_1[2] != None):
                visualize_single_summarization_step(super_variant_1[1], super_variant_1[2], super_variant_1[0])

            else:
                SVV.visualize_super_variant(super_variant_1[0], mode = MODE)

        elif event.inaxes == ax2:
            if(super_variant_2[1] != None and super_variant_2[2] != None):
                visualize_single_summarization_step(super_variant_2[1], super_variant_2[2], super_variant_2[0])

            else:
                SVV.visualize_super_variant(super_variant_2[0], mode = MODE)


    fig.subplots_adjust(wspace=0.03, hspace=0)

    fig.canvas.mpl_connect('motion_notify_event', hover_info)
    fig.canvas.mpl_connect('button_press_event', click)

    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    plt.show()