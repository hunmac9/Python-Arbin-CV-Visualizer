import matplotlib.pyplot as plt
from itertools import cycle
import matplotlib.font_manager as fm
import os
import matplotlib.ticker as ticker
import configparser

def create_unique_filename(directory, filename_template, temperature):
    base_filename = filename_template.format(temperature=temperature)
    filename = f"{base_filename}.png"
    counter = 1
    while os.path.exists(os.path.join(directory, filename)):
        filename = f"{base_filename}_{counter}.png"
        counter += 1
    return os.path.join(directory, filename)

def create_cv_graph(cycle_data, temperature, scan_rate, cycle_list, colors, config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    
    font_family = config['DEFAULT']['fontfamily']
    font_size = int(config['DEFAULT']['fontsize'])
    tick_font_size = int(config['DEFAULT']['tickfontsize'])
    legend_font_size = int(config['DEFAULT']['legendfontsize'])
    x_min = float(config['DEFAULT']['xaxismin'])
    x_max = float(config['DEFAULT']['xaxismax'])
    y_min = config['DEFAULT']['yaxismin']
    y_max = config['DEFAULT']['yaxismax']
    show_grid = config['DEFAULT'].getboolean('showgrid')
    output_dir = config['DEFAULT']['outputdirectory']
    filename_template = config['DEFAULT']['filenametemplate']
    line_weight = float(config['DEFAULT']['lineweight'])
    axis_line_weight = float(config['DEFAULT']['axislineweight'])
    
    y_bounds = (float(y_min), float(y_max)) if y_min != 'auto' and y_max != 'auto' else None
    x_bounds = (x_min, x_max)

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    print(f"Creating CV graphs for temperature: {temperature}")

    # Check and log colors
    if not colors:
        raise ValueError("No colors provided for plotting.")
    for idx, color in enumerate(colors):
        if not isinstance(color, str) or not color.startswith('#'):
            raise ValueError(f"Invalid color value at index {idx}: {color}")

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

    for idx, cycle_index in enumerate(cycle_list):
        if cycle_index in cycle_data:
            data = cycle_data[cycle_index]
            color = colors[idx % len(colors)]
            plt.plot(data['Voltage(V)'], data['Smoothed Current Density (mA g^-1)'],
                     label=f'Cycle {cycle_index}', color=color, linewidth=line_weight)
        else:
            print(f"Cycle {cycle_index} not found in data.")

    plt.xlabel('Potential / V', fontsize=font_size, fontproperties=prop_bold, labelpad=20)
    plt.ylabel(r'Current Density / mA g$^{\mathbf{-1}}$', fontsize=font_size, fontproperties=prop_bold, labelpad=20)

    plt.xticks(fontsize=tick_font_size, fontproperties=tick_prop)
    plt.yticks(fontsize=tick_font_size, fontproperties=tick_prop)

    plt.legend(loc='upper left', prop=legend_prop, frameon=False)

    # Add scan rate without bold superscript
    scan_rate_text = f'${scan_rate} \\mathrm{{mV}} \\ \\mathrm{{s}}^{{-1}}$'
    plt.text(0.03, 0.03, scan_rate_text, transform=plt.gca().transAxes, fontsize=font_size, fontproperties=prop_regular)

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

    # Set axis line weight
    plt.gca().spines['top'].set_linewidth(axis_line_weight)
    plt.gca().spines['bottom'].set_linewidth(axis_line_weight)
    plt.gca().spines['left'].set_linewidth(axis_line_weight)
    plt.gca().spines['right'].set_linewidth(axis_line_weight)

    if show_grid:
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    else:
        plt.grid(False)

    plt.tight_layout()

    output_path = create_unique_filename(output_dir, filename_template, temperature)
    plt.savefig(output_path, dpi=600)
    print(f"Graph saved to {output_path}")
    plt.close()
