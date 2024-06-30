import matplotlib.pyplot as plt
from itertools import cycle
import matplotlib.font_manager as fm
import os
import matplotlib.ticker as ticker
import configparser
from matplotlib.colors import LinearSegmentedColormap
import numpy as np


def create_unique_filename(directory, filename_template, temperature, cycle_number=None):
    base_filename = filename_template.format(temperature=temperature)
    if cycle_number is not None:
        base_filename += f"_Cycle{cycle_number}"
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
    major_tick_interval = float(config['DEFAULT']['majortickinterval'])
    minor_tick_interval = major_tick_interval / 2
    width = float(config['DEFAULT']['width'])
    height = float(config['DEFAULT']['height'])
    dpi = int(config['DEFAULT']['dpi'])
    tick_length = float(config['DEFAULT']['ticklength'])
    tick_width = float(config['DEFAULT']['tickwidth'])
    
    y_bounds = (float(y_min), float(y_max)) if y_min != 'auto' and y_max != 'auto' else None
    x_bounds = (x_min, x_max)

    # Ensure the output directory exists while avoiding race conditions
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
    legend_prop = fm.FontProperties(family=font_family, size=legend_font_size)

    fig, ax = plt.subplots(figsize=(width, height))

    # Create a color map for the gradient
    cmap = LinearSegmentedColormap.from_list("custom_gradient", colors)
    norm = plt.Normalize(vmin=min(cycle_list), vmax=max(cycle_list))
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    for idx, cycle_index in enumerate(cycle_list):
        if cycle_index in cycle_data:
            data = cycle_data[cycle_index]
            color = cmap(norm(cycle_index))
            ax.plot(data['Voltage(V)'], data['Smoothed Current Density (mA g^-1)'],
                    label=f'Cycle {cycle_index}', color=color, linewidth=line_weight)
        else:
            print(f"Cycle {cycle_index} not found in data.")

    ax.set_xlabel('Potential / V', fontsize=font_size, fontproperties=prop_bold, labelpad=20)
    ax.set_ylabel(r'Current Density / mA g$^{\mathbf{-1}}$', fontsize=font_size, fontproperties=prop_bold, labelpad=20)

    ax.tick_params(axis='both', which='major', labelsize=tick_font_size, length=tick_length, width=tick_width)
    ax.tick_params(axis='both', which='minor', labelsize=tick_font_size, length=tick_length / 2, width=tick_width)

    if len(cycle_list) <= 8:
        ax.legend(loc='upper left', prop=legend_prop, frameon=False)

    # Add scan rate without bold superscript
    scan_rate_text = f'${scan_rate} \\ \\mathrm{{mV}} \\ \\mathrm{{s}}^{{-1}}$'
    ax.text(0.03, 0.03, scan_rate_text, transform=ax.transAxes, fontsize=font_size, fontproperties=prop_regular)

    if temperature != 'auto':
        ax.text(0.97, 0.03, f'{temperature}', transform=ax.transAxes, fontsize=font_size, fontproperties=prop_bold, horizontalalignment='right')

    # Apply axis bounds
    ax.set_xlim(x_bounds)
    if y_bounds:
        ax.set_ylim(y_bounds)

    # Add major and minor ticks
    ax.xaxis.set_major_locator(ticker.MultipleLocator(0.2))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(major_tick_interval))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(minor_tick_interval))

    # Set axis line weight
    ax.spines['top'].set_linewidth(axis_line_weight)
    ax.spines['bottom'].set_linewidth(axis_line_weight)
    ax.spines['left'].set_linewidth(axis_line_weight)
    ax.spines['right'].set_linewidth(axis_line_weight)

    if show_grid:
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    else:
        ax.grid(False)

    if len(cycle_list) > 8:
        # Add a color bar with whole number ticks
        cbar = fig.colorbar(sm, ax=ax, orientation='vertical')
        cbar.set_label('Cycle Number', fontsize=font_size, fontproperties=prop_bold)
        cbar.ax.tick_params(labelsize=tick_font_size)
        cbar.set_ticks(np.arange(min(cycle_list), max(cycle_list) + 1, max(1, (max(cycle_list) - min(cycle_list)) // 8)))

    fig.tight_layout()

    output_path = create_unique_filename(output_dir, filename_template, temperature)
    plt.savefig(output_path, dpi=dpi)
    print(f"Graph saved to {output_path}")
    plt.close()


def create_cv_graph_compare(cycle_data_dict, cycle_number, scan_rate, colors, config_file):
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
    major_tick_interval = float(config['DEFAULT']['majortickinterval'])
    minor_tick_interval = major_tick_interval / 2
    width = float(config['DEFAULT']['width'])
    height = float(config['DEFAULT']['height'])
    dpi = int(config['DEFAULT']['dpi'])
    tick_length = float(config['DEFAULT']['ticklength'])
    tick_width = float(config['DEFAULT']['tickwidth'])

    y_bounds = (float(y_min), float(y_max)) if y_min != 'auto' and y_max != 'auto' else None
    x_bounds = (x_min, x_max)

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    print(f"Comparing cycles for cycle number: {cycle_number}")

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
    legend_prop = fm.FontProperties(family=font_family, size=legend_font_size)

    fig, ax = plt.subplots(figsize=(width, height))

    for temperature, cycle_data in cycle_data_dict.items():
        if cycle_number in cycle_data:
            data = cycle_data[cycle_number]
            color = colors.pop(0)
            ax.plot(data['Voltage(V)'], data['Smoothed Current Density (mA g^-1)'],
                    label=f'{temperature}', color=color, linewidth=line_weight)
        else:
            print(f"Cycle {cycle_number} not found in data for temperature {temperature}.")

    ax.set_xlabel('Potential / V', fontsize=font_size, fontproperties=prop_bold, labelpad=20)
    ax.set_ylabel(r'Current Density / mA g$^{\mathbf{-1}}$', fontsize=font_size, fontproperties=prop_bold, labelpad=20)

    ax.tick_params(axis='both', which='major', labelsize=tick_font_size, length=tick_length, width=tick_width)
    ax.tick_params(axis='both', which='minor', labelsize=tick_font_size, length=tick_length / 2, width=tick_width)

    ax.legend(loc='upper left', prop=legend_prop, frameon=False)

    # Add scan rate without bold superscript
    scan_rate_text = f'${scan_rate} \\ \\mathrm{{mV}} \\ \\mathrm{{s}}^{{-1}}$'
    ax.text(0.03, 0.03, scan_rate_text, transform=ax.transAxes, fontsize=font_size, fontproperties=prop_regular)

    # Add cycle number in the bottom right
    ax.text(0.97, 0.03, f'Cycle {cycle_number}', transform=ax.transAxes, fontsize=font_size, fontproperties=prop_bold, horizontalalignment='right')

    # Apply axis bounds
    ax.set_xlim(x_bounds)
    if y_bounds:
        ax.set_ylim(y_bounds)

    # Add major and minor ticks
    ax.xaxis.set_major_locator(ticker.MultipleLocator(0.2))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(major_tick_interval))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(minor_tick_interval))

    # Set axis line weight
    ax.spines['top'].set_linewidth(axis_line_weight)
    ax.spines['bottom'].set_linewidth(axis_line_weight)
    ax.spines['left'].set_linewidth(axis_line_weight)
    ax.spines['right'].set_linewidth(axis_line_weight)

    if show_grid:
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    else:
        ax.grid(False)

    fig.tight_layout()

    output_path = create_unique_filename(output_dir, filename_template, 'Comparison', cycle_number)
    plt.savefig(output_path, dpi=dpi)
    print(f"Graph saved to {output_path}")
    plt.close()
