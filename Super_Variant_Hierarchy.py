import Super_Variant_Visualization as SVV
import matplotlib.pyplot as plt

def visualize_super_variant_layer(super_variants):

    fig, ax = plt.subplots(1, len(super_variants), figsize=(8,2)) 
    ax = list(ax)

    for i in (range(len(super_variants))):

        ax[i], width, height = SVV.arrange_super_variant(super_variants[i], ax[i], 0, 0, "*")
    
        ax[i].set_aspect('equal')
        ax[i].set_xlim(-15, width + 2)
        ax[i].set_ylim(-2, height + 2)
        ax[i].axis('off')

    ax = tuple(ax)
    fig.subplots_adjust(wspace=0.03, hspace=0)
    plt.show()


def visualize_single_super_variant_hierarchy(super_variant_1, super_variant_2, new_super_variant):
    import matplotlib.pyplot as plt
    from matplotlib.patches import ConnectionPatch

    fig = plt.figure(figsize=(8,2))

    gs = fig.add_gridspec(2,2)
    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[1, 1])
    ax3 = fig.add_subplot(gs[0, :])


    ax1, width1, height1 = SVV.arrange_super_variant(super_variant_1, ax1, 0, 0, "*")
    
    ax1.set_aspect('equal')
    ax1.set_xlim(-15, width1 + 2)
    ax1.set_ylim(-2, height1 + 2)
    ax1.axis('off')

    ax2, width2, height2 = SVV.arrange_super_variant(super_variant_2, ax2, 0, 0, "*")
    
    ax2.set_aspect('equal')
    ax2.set_xlim(-15, width2 + 2)
    ax2.set_ylim(-2, height2 + 2)
    ax2.axis('off')

    ax3, width3, height3 = SVV.arrange_super_variant(new_super_variant, ax3, 0, 0, "*")
    
    ax3.set_aspect('equal')
    ax3.set_xlim(-15, width3 + 2)
    ax3.set_ylim(-2, height3 + 2)
    ax3.axis('off')

    #ax1.plot([width1/2, 0], "o")
    #ax2.plot([width2/2, 0], "o")
    #ax3.plot([width3/2, 0], "o")
    #connection1 = ConnectionPatch(xyA=(0, width1/2), coordsA=ax1.transAxes, xyB=(0, width3/2), coordsB=ax3.transAxes, arrowstyle="-")
    #fig.add_artist(connection1)

    fig.subplots_adjust(wspace=0.03, hspace=0)

    plt.show()