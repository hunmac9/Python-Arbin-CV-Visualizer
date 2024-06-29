import matplotlib.pyplot as plt
from itertools import cycle
import matplotlib.font_manager as fm
import os

def create_cv_graph(cycle_data, temperature, output_dir):
    print(f"Creating CV graphs for temperature: {temperature}")

    # Define a more distinguishable color palette
    custom_colors = [
        '#1b2c2d',  # Dark green
        '#083c40',  # Dark blue
        '#266E70',  # Medium sea green
        '#3C8D8E',  # Medium teal
        '#5BB8BD',  # Light sea green
        '#7DE4E6'   # Light teal
    ]
    colors = cycle(custom_colors)

    # Load the custom font
    font_path = os.path.join(os.path.dirname(__file__), 'artrbdo.ttf')
    prop = fm.FontProperties(fname=font_path)

    # Set the figure size to match the pixel dimensions ratio
    pixel_width, pixel_height = 6432, 4923
    fig_ratio = pixel_width / pixel_height
    fig_height = 8  # Choose a base height
    fig_width = fig_height * fig_ratio

    plt.figure(figsize=(fig_width, fig_height))  # Maintain the aspect ratio as specified

    for cycle_index, data in cycle_data.items():
        color = next(colors)
        plt.plot(data['Voltage(V)'], data['Smoothed Current Density (mA g^-1)'],
                 label=f'Cycle {cycle_index}', color=color)

    plt.xlabel('Potential / V', fontsize=18, fontweight='bold', fontproperties=prop)
    plt.ylabel('Current Density / mA g$^{-1}$', fontsize=18, fontweight='bold', fontproperties=prop)

    plt.xticks(fontsize=16, fontproperties=prop)
    plt.yticks(fontsize=16, fontproperties=prop)

    plt.legend(loc='upper right', prop=prop)

    # Place scan rate label at the bottom-left corner and make it bold
    plt.text(0.03, 0.03, '0.2 mV s$^{-1}$', transform=plt.gca().transAxes, fontsize=16, fontweight='bold', fontproperties=prop)

    # Place temperature label at the bottom-right corner and make it bold
    plt.text(0.97, 0.03, temperature, transform=plt.gca().transAxes, fontsize=16, fontweight='bold', fontproperties=prop, horizontalalignment='right')

    plt.xlim([0, 1.8])
    plt.xticks([i * 0.2 for i in range(10)])

    plt.grid(False)  # Remove internal grid lines

    plt.tight_layout()

    output_path = f'{output_dir}/{temperature}_CV-Graph.png'
    plt.savefig(output_path, dpi=600)
    print(f"Graph saved to {output_path}")
    plt.close()
