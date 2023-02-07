import Super_Variant_Visualization as SVV
import matplotlib.pyplot as plt

def visualize_Super_Variant_layer(super_variants):
    vertical_position = 0
    horizontal_position = 0
    final_heigth = 0
    final_width = 0
    fig, ax = plt.subplots()
    for super_variant in super_variants:
        ax, width, height = SVV.arrange_super_variant(super_variant, ax, vertical_position, horizontal_position, "*")
        final_heigth = max(final_heigth, height + 4)
        horizontal_position += width + 17
        final_width = horizontal_position

    ax.set_aspect('equal')
    ax.set_xlim(-15, horizontal_position + 2)
    ax.set_ylim(-2, final_heigth + 2)
    plt.axis('off')
    plt.show()