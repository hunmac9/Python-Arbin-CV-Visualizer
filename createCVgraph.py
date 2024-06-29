import matplotlib.pyplot as plt
from itertools import cycle
import matplotlib.font_manager as fm
import os
import matplotlib.ticker as ticker
import configparser

def create_cv_graph(cycle_data, temperature, scan_rate, cycle_list, color_palette, config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    
    font_family = config['DEFAULT']['FontFamily']
    font_size = int(config['DEFAULT']['FontSize'])
    tick_font_size = int(config['DEFAULT']['TickFontSize'])
    legend_font_size = int(config['DEFAULT']['LegendFontSize'])
    x_min = float(config['DEFAULT']['XAxisMin'])
    x_max = float(config['DEFAULT']['XAxisMax'])
    y_min = config['DEFAULT']['YAxisMin']
    y_max = config['DEFAULT']['YAxisMax']
    show_grid = config['DEFAULT'].getboolean('ShowGrid')
    output_dir = config['DEFAULT']['OutputDirectory']

    y_bounds = (float(y_min), float(y_max)) if y_min != 'auto' and y_max != 'auto' else None
    x_bounds = (x_min, x_max)

    print(f"Creating CV graphs for temperature: {temperature}")

    palettes = {
        'Default': ['#1b2c2d', '#083c40', '#266E70', '#3C8D8E', '#5BB8BD', '#7DE4E6'],
        'Palette 1': ['#003f5c', '#2f4b7c', '#665191', '#a05195', '#d45087', '#f95d6a'],
        'Palette 2': ['#2b2d42', '#8d99ae', '#edf2f4', '#ef233c', '#d90429', '#fff000'],
        'Palette 3': ['#264653', '#2a9d8f', '#e9c46a', '#f4a261', '#e76f51'],
    }

    colors = cycle(palettes[color_palette])

    # Load the Arial font
    prop_bold = fm.FontProperties(family=font_family, size=font_size, weight='bold')
    prop_regular = fm.FontProperties(family=font_family, size=font_size)
    tick_prop = fm.FontProperties(family=font_family, size=tick_font_size)
    legend_prop = fm.FontProperties(family=font_family, size=legend_font_size, weight='bold')

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

    plt.xlabel('Potential / V', fontsize=font_size, fontproperties=prop_bold, labelpad=20)
    plt.ylabel(r'Current Density / mA g$^{\mathbf{-1}}$', fontsize=font_size, fontproperties=prop_bold, labelpad=20)

    plt.xticks(fontsize=tick_font_size, fontproperties=tick_prop)
    plt.yticks(fontsize=tick_font_size, fontproperties=tick_prop)

    plt.legend(loc='upper left', prop=legend_prop, frameon=False)

    plt.text(0.03, 0.03, f'${scan_rate} \\mathrm{{mV}} \\ \\mathrm{{s}}^{{-1}}$', transform=plt.gca().transAxes, fontsize=font_size, fontproperties=prop_bold)

    if temperature != 'auto':
        plt.text(0.97, 0.03, f'{temperature}', transform=plt.gca().transAxes, fontsize=font_size, fontproperties=prop_bold, horizontalalignment='right')

    # Apply axis bounds
    plt.xlim(x_bounds)
    if y_bounds:
        plt.ylim(y_bounds)

    # Add major and minor ticks
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(0.2))
    plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
    plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(50))
    plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(25))

    if show_grid:
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    else:
        plt.grid(False)

    plt.tight_layout()

    output_path = f'{output_dir}/{temperature}_CV-Graph.png'
    plt.savefig(output_path, dpi=600)
    print(f"Graph saved to {output_path}")
    plt.close()
