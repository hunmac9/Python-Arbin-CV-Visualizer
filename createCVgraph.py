import matplotlib.pyplot as plt
from itertools import cycle
import matplotlib.font_manager as fm
import os
import matplotlib.ticker as ticker

def create_cv_graph(cycle_data, temperature, scan_rate, cycle_list, color_palette, output_dir):
    print(f"Creating CV graphs for temperature: {temperature}")
    
    palettes = {
        'Default': ['#1b2c2d', '#083c40', '#266E70', '#3C8D8E', '#5BB8BD', '#7DE4E6'],
        'Palette 1': ['#003f5c', '#2f4b7c', '#665191', '#a05195', '#d45087', '#f95d6a'],
        'Palette 2': ['#2b2d42', '#8d99ae', '#edf2f4', '#ef233c', '#d90429'],
        'Palette 3': ['#264653', '#2a9d8f', '#e9c46a', '#f4a261', '#e76f51'],
    }

    colors = cycle(palettes[color_palette])

    # Load the custom font
    font_path = os.path.join(os.path.dirname(__file__), 'artrbdo.ttf')
    prop = fm.FontProperties(fname=font_path)

    pixel_width, pixel_height = 6432, 4923
    fig_ratio = pixel_width / pixel_height
    fig_height = 8
    fig_width = fig_height * fig_ratio

    plt.figure(figsize=(fig_width, fig_height))

    for cycle_index in cycle_list:
        if cycle_index in cycle_data:
            data = cycle_data[cycle_index]
            color = next(colors)
            plt.plot(data['Voltage(V)'], data['Smoothed Current Density (mA g^-1)'],
                     label=f'Cycle {cycle_index}', color=color)
        else:
            print(f"Cycle {cycle_index} not found in data.")

    plt.xlabel('Potential / V', fontsize=20, fontweight='bold', fontproperties=prop)
    plt.ylabel('Current Density / mA g$^{-1}$', fontsize=20, fontweight='bold', fontproperties=prop)

    plt.xticks(fontsize=18, fontproperties=prop)
    plt.yticks(fontsize=18, fontproperties=prop)

    plt.legend(loc='upper left', prop=prop)

    plt.text(0.03, 0.03, f'{scan_rate} mV s$^{-1}$', transform=plt.gca().transAxes, fontsize=18, fontweight='bold', fontproperties=prop)

    if temperature != 'auto':
        plt.text(0.97, 0.03, temperature, transform=plt.gca().transAxes, fontsize=18, fontweight='bold', fontproperties=prop, horizontalalignment='right')

    plt.xlim([0, 1.8])
    plt.xticks([i * 0.2 for i in range(10)])
    plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
    plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(0.2))

    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    plt.tight_layout()

    output_path = f'{output_dir}/{temperature}_CV-Graph.png'
    plt.savefig(output_path, dpi=600)
    print(f"Graph saved to {output_path}")
    plt.close()
