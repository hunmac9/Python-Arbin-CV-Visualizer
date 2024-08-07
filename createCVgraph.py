import matplotlib.pyplot as plt
from itertools import cycle
import matplotlib.font_manager as fm
import os
import matplotlib.ticker as ticker
import configparser
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import re

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

def extract_run_from_filename(filename):
    match = re.search(r'Run(\d+)', filename)
    return f"Run {match.group(1)}" if match else None

def parse_temperature_key(temp):
    temp_parts = temp.split(" - ")
    temperature = re.findall(r'\d+', temp_parts[0])[0]
    run = temp_parts[1].split()[1] if len(temp_parts) > 1 else 0
    return int(temperature), int(run)

def create_cv_graph(cycle_data, temperature, scan_rate, cycle_list, colors, graph_params, run_info=None):
    # Use values from graph_params
    font_family = graph_params["font_family"]
    font_size = graph_params["font_size"]
    tick_font_size = graph_params["tick_font_size"]
    legend_font_size = graph_params["legend_font_size"]
    x_min = graph_params["x_min"]
    x_max = graph_params["x_max"]
    y_min = graph_params["y_min"]
    y_max = graph_params["y_max"]
    show_grid = graph_params["show_grid"]
    output_dir = graph_params["output_dir"]
    filename_template = graph_params["filename_template"]
    line_weight = graph_params["line_weight"]
    axis_line_weight = graph_params["axis_line_weight"]
    major_tick_interval = graph_params["major_tick_interval"]
    minor_tick_interval = graph_params["minor_tick_interval"]
    width = graph_params["width"]
    height = graph_params["height"]
    dpi = graph_params["dpi"]
    tick_length = graph_params["tick_length"]
    tick_width = graph_params["tick_width"]

    y_bounds = (float(y_min), float(y_max)) if y_min != 'auto' and y_max != 'auto' else None
    x_bounds = (x_min, x_max)

    os.makedirs(output_dir, exist_ok=True)

    if not colors:
        raise ValueError("No colors provided for plotting.")
    if not (isinstance(colors, list) and all(isinstance(c, str) and c.startswith('#') for c in colors)):
        raise ValueError("Invalid color values provided. All colors should be hex strings starting with '#'.")

    prop_bold = fm.FontProperties(family=font_family, size=font_size, weight='bold')
    prop_regular = fm.FontProperties(family=font_family, size=font_size)
    tick_prop = fm.FontProperties(family=font_family, size=tick_font_size)
    legend_prop = fm.FontProperties(family=font_family, size=legend_font_size)

    fig, ax = plt.subplots(figsize=(width, height))

    if len(cycle_list) == 1:
        color = colors[0]
    else:
        cmap = LinearSegmentedColormap.from_list("custom_gradient", colors)
        norm = plt.Normalize(vmin=min(cycle_list), vmax=max(cycle_list))
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])

    for cycle_index in cycle_list:
        if cycle_index in cycle_data:
            data = cycle_data[cycle_index]
            if len(cycle_list) == 1:
                ax.plot(data['Voltage(V)'], data['Smoothed Current Density (mA g^-1)'],
                        label=f'Cycle {cycle_index}', color=color, linewidth=line_weight)
            else:
                cycle_color = cmap(norm(cycle_index))
                ax.plot(data['Voltage(V)'], data['Smoothed Current Density (mA g^-1)'],
                        label=f'Cycle {cycle_index}', color=cycle_color, linewidth=line_weight)
        else:
            print(f"Cycle {cycle_index} not found in data.")

    ax.set_xlabel('Potential / V', fontsize=font_size, fontproperties=prop_bold, labelpad=20)
    ax.set_ylabel(r'Current Density / mA g$^{\mathbf{-1}}$', fontsize=font_size, fontproperties=prop_bold, labelpad=20)

    ax.tick_params(axis='both', which='major', labelsize=tick_font_size, length=tick_length, width=tick_width)
    ax.tick_params(axis='both', which='minor', labelsize=tick_font_size, length=tick_length / 2, width=tick_width)

    if len(cycle_list) <= 8:
        ax.legend(loc='upper left', prop=legend_prop, frameon=False)

    scan_rate_text = f'${scan_rate} \\ \\mathrm{{mV}} \\ \\mathrm{{s}}^{{-1}}$'
    ax.text(0.03, 0.03, scan_rate_text, transform=ax.transAxes, fontsize=font_size, fontproperties=prop_regular)

    temp_label = temperature if run_info is None else f'{temperature} - {run_info}'
    ax.text(0.97, 0.03, f'{temp_label}', transform=ax.transAxes, fontsize=font_size, fontproperties=prop_bold, horizontalalignment='right')

    ax.set_xlim(x_bounds)
    if y_bounds:
        ax.set_ylim(y_bounds)

    ax.xaxis.set_major_locator(ticker.MultipleLocator(0.2))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(major_tick_interval))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(minor_tick_interval))

    ax.spines['top'].set_linewidth(axis_line_weight)
    ax.spines['bottom'].set_linewidth(axis_line_weight)
    ax.spines['left'].set_linewidth(axis_line_weight)
    ax.spines['right'].set_linewidth(axis_line_weight)

    if show_grid:
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    else:
        ax.grid(False)

    if len(cycle_list) > 8:
        cbar = fig.colorbar(sm, ax=ax, orientation='vertical')
        cbar.set_label('Cycle Number', fontsize=font_size, fontproperties=prop_bold)
        cbar.ax.tick_params(labelsize=tick_font_size)
        cbar.set_ticks(np.arange(min(cycle_list), max(cycle_list) + 1, max(1, (max(cycle_list) - min(cycle_list)) // 8)))

    fig.tight_layout()

    output_path = create_unique_filename(output_dir, filename_template, temperature)
    plt.savefig(output_path, dpi=dpi)
    print(f"Graph saved to {output_path}")
    plt.close()

def create_cv_graph_compare(cycle_data_dict, cycle_list, scan_rate, colors, graph_params):
    for cycle_number in cycle_list:
        # Use values from graph_params
        font_family = graph_params["font_family"]
        font_size = graph_params["font_size"]
        tick_font_size = graph_params["tick_font_size"]
        legend_font_size = graph_params["legend_font_size"]
        x_min = graph_params["x_min"]
        x_max = graph_params["x_max"]
        y_min = graph_params["y_min"]
        y_max = graph_params["y_max"]
        show_grid = graph_params["show_grid"]
        output_dir = graph_params["output_dir"]
        filename_template = graph_params["filename_template"]
        line_weight = graph_params["line_weight"]
        axis_line_weight = graph_params["axis_line_weight"]
        major_tick_interval = graph_params["major_tick_interval"]
        minor_tick_interval = graph_params["minor_tick_interval"]
        width = graph_params["width"]
        height = graph_params["height"]
        dpi = graph_params["dpi"]
        tick_length = graph_params["tick_length"]
        tick_width = graph_params["tick_width"]

        y_bounds = (float(y_min), float(y_max)) if y_min != 'auto' and y_max != 'auto' else None
        x_bounds = (x_min, x_max)

        os.makedirs(output_dir, exist_ok=True)
        print(f"Comparing cycles for cycle number: {cycle_number}")

        if not colors:
            raise ValueError("No colors provided for plotting.")
        for idx, color in enumerate(colors):
            if not isinstance(color, str) or not color.startswith('#'):
                raise ValueError(f"Invalid color value at index {idx}: {color}")

        prop_bold = fm.FontProperties(family=font_family, size=font_size, weight='bold')
        prop_regular = fm.FontProperties(family=font_family, size=font_size)
        tick_prop = fm.FontProperties(family=font_family, size=tick_font_size)
        legend_prop = fm.FontProperties(family=font_family, size=legend_font_size)

        fig, ax = plt.subplots(figsize=(width, height))

        # Adjust sorting so that temperatures with runs are handled properly
        sorted_temps = sorted(cycle_data_dict.keys(), key=lambda x: parse_temperature_key(x))
        color_cycle = cycle(colors)
        
        for temperature in sorted_temps:
            cycle_data = cycle_data_dict[temperature]
            if cycle_number in cycle_data:
                data = cycle_data[cycle_number]
                color = next(color_cycle)

                run_info = extract_run_from_filename(cycle_data["filename"])
                temp_label = temperature  # temperature string already includes run info if applicable
                ax.plot(data['Voltage(V)'], data['Smoothed Current Density (mA g^-1)'],
                        label=f'{temp_label}', color=color, linewidth=line_weight)
            else:
                print(f"Cycle {cycle_number} not found in data for temperature {temperature}.")

        ax.set_xlabel('Potential / V', fontsize=font_size, fontproperties=prop_bold, labelpad=20)
        ax.set_ylabel(r'Current Density / mA g$^{\mathbf{-1}}$', fontsize=font_size, fontproperties=prop_bold, labelpad=20)

        ax.tick_params(axis='both', which='major', labelsize=tick_font_size, length=tick_length, width=tick_width)
        ax.tick_params(axis='both', which='minor', labelsize=tick_font_size, length=tick_length / 2, width=tick_width)

        ax.legend(loc='upper left', prop=legend_prop, frameon=False)

        scan_rate_text = f'${scan_rate} \\ \\mathrm{{mV}} \\ \\mathrm{{s}}^{{-1}}$'
        ax.text(0.03, 0.03, scan_rate_text, transform=ax.transAxes, fontsize=font_size, fontproperties=prop_regular)

        ax.text(0.97, 0.03, f'Cycle {cycle_number}', transform=ax.transAxes, fontsize=font_size, fontproperties=prop_bold, horizontalalignment='right')

        ax.set_xlim(x_bounds)
        if y_bounds:
            ax.set_ylim(y_bounds)

        ax.xaxis.set_major_locator(ticker.MultipleLocator(0.2))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(major_tick_interval))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(minor_tick_interval))

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
