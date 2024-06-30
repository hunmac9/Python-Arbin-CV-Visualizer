import os
import pickle
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Canvas, colorchooser
from tkinter.scrolledtext import ScrolledText
import logging
import configparser
import webbrowser
import time
from loadExcel import load_excel_data, parse_temperature_from_filename
from processExcel import process_data, store_processed_data, load_processed_data
from createCVgraph import create_cv_graph, create_cv_graph_compare
from genColors import generate_gradient_colors

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
config_file = 'config.ini'

MAX_PICKLE_FILE_AGE = 3600  # 1 hour in seconds

def get_pickle_filename(file_path):
    directory, file_name = os.path.split(file_path)
    base_name, _ = os.path.splitext(file_name)
    return os.path.join(directory, f"{base_name}_processed.pkl")

def is_pickle_file_relevant(pickle_filename):
    if os.path.exists(pickle_filename):
        file_age = time.time() - os.path.getmtime(pickle_filename)
        return file_age < MAX_PICKLE_FILE_AGE
    return False

def remove_pickle_files(file_paths):
    for file_path in file_paths:
        pickle_filename = get_pickle_filename(file_path)
        if os.path.exists(pickle_filename):
            os.remove(pickle_filename)
            logging.info(f"Deleted pickle file: {pickle_filename}")

def get_color_palettes(config_file, section='PALETTES'):
    section_started = False
    palettes = []
    with open(config_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line == f'[{section}]':
                section_started = True
                continue
            if section_started and line.startswith('['):
                break
            if section_started and '=' in line:
                key = line.split('=', 1)[0].strip()
                palettes.append(key)
    return palettes + ['Custom']

def update_status(message):
    logging.info(message)
    status_label.config(text=message)

def parse_cycle_range(cycle_range):
    cycle_list = []
    if cycle_range:
        for part in cycle_range.split(','):
            if '-' in part:
                start, end = part.split('-')
                cycle_list.extend(range(int(start), int(end) + 1))
            else:
                cycle_list.append(int(part))
    return cycle_list

def create_graph():
    try:
        update_status("Starting graph creation...")
        
        config = configparser.ConfigParser()
        config.read(config_file)

        for file_info in file_infos:
            file_path = file_info['path']
            mass = file_info['mass']
            cycle_list = parse_cycle_range(cycles_var.get())
            scan_rate = scan_rate_var.get()
            temperature = temp_var.get()

            if temperature == 'auto':
                temperature = parse_temperature_from_filename(file_path)

            x_min = x_min_var.get() if x_min_var.get() != 'auto' else config['DEFAULT']['xaxismin']
            x_max = x_max_var.get() if x_max_var.get() != 'auto' else config['DEFAULT']['xaxismax']
            y_min = y_min_var.get() if y_min_var.get() != 'auto' else config['DEFAULT']['yaxismin']
            y_max = y_max_var.get() if y_max_var.get() != 'auto' else config['DEFAULT']['yaxismax']
            show_grid = grid_var.get()
            major_tick_interval = float(major_tick_var.get())
            minor_tick_interval = major_tick_interval / 2
            smoothing_points = int(smoothing_points_var.get())
            output_directory = output_dir.get()
            filename_template = filename_template_var.get()

            pickle_filename = get_pickle_filename(file_path)

            if is_pickle_file_relevant(pickle_filename):
                update_status(f"Loading processed data from {pickle_filename}")
                cycle_data = load_processed_data(pickle_filename)
            else:
                update_status("Loading Excel data...")
                channel_data, _, temp_auto = load_excel_data(file_path)

                update_status("Processing data...")
                cycle_data = process_data(channel_data, mass, smoothing_points)
                store_processed_data(cycle_data, pickle_filename)

            update_status(f"Cycle data has been loaded for file: {file_path}")

            temp = temperature if temperature != 'auto' else temp_auto
            color_palette = palette_var.get()

            if color_palette.lower().startswith('gradient'):
                colors = config['PALETTES'][color_palette].split(',')
                start_color = colors[0]
                end_color = colors[1]
                colors = generate_gradient_colors(start_color, end_color, len(cycle_list))
            elif color_palette.lower() == 'custom':
                start_color = start_color_var.get()
                end_color = end_color_var.get()
                colors = generate_gradient_colors(start_color, end_color, len(cycle_list))
            else:
                colors = config['PALETTES'][color_palette].split(',')

            update_status(f"Creating CV graph for {file_path}...")
            create_cv_graph(cycle_data, temp, scan_rate, cycle_list, colors, config_file)
            update_status(f"Graph saved successfully to {output_directory}")

            output_path = os.path.join(output_directory, filename_template.format(temperature=temp) + ".png")
            webbrowser.open(output_path)
        
        update_status("All graphs created successfully.")
    
    except Exception as e:
        update_status(f"Error: {str(e)}")
        logging.error(str(e))

def compare_cycles():
    try:
        update_status("Starting cycle comparison...")

        cycle_list = parse_cycle_range(cycles_var.get())
        cycle_data_dict = {}

        for file_info in file_infos:
            file_path = file_info['path']
            mass = file_info['mass']
            temperature = parse_temperature_from_filename(file_path)

            config = configparser.ConfigParser()
            config.read(config_file)

            smoothing_points = int(smoothing_points_var.get())

            pickle_filename = get_pickle_filename(file_path)

            if is_pickle_file_relevant(pickle_filename):
                update_status(f"Loading processed data from {pickle_filename}")
                cycle_data = load_processed_data(pickle_filename)
            else:
                update_status("Loading Excel data...")
                channel_data, _, temp_auto = load_excel_data(file_path)

                update_status("Processing data...")
                cycle_data = process_data(channel_data, mass, smoothing_points)

                store_processed_data(cycle_data, pickle_filename)

            cycle_data_dict[temperature] = cycle_data
            update_status(f"Cycle data has been loaded for temperature: {temperature}")

        color_palette = palette_var.get()
        if color_palette.lower().startswith('gradient'):
            num_temps = len(cycle_data_dict)
            colors = config['PALETTES'][color_palette].split(',')
            start_color = colors[0]
            end_color = colors[1]
            colors = generate_gradient_colors(start_color, end_color, num_temps)
        elif color_palette.lower() == 'custom':
            start_color = start_color_var.get()
            end_color = end_color_var.get()
            num_temps = len(cycle_data_dict)
            colors = generate_gradient_colors(start_color, end_color, num_temps)
        else:
            colors = config['PALETTES'][color_palette].split(',')

        scan_rate = scan_rate_var.get()

        update_status(f"Creating comparison graphs for cycles {cycle_list}...")
        for cycle_number in cycle_list:
            create_cv_graph_compare(cycle_data_dict, [cycle_number], scan_rate, colors.copy(), config_file)

        update_status("Comparison graphs saved successfully.")

        output_path = os.path.join(config['DEFAULT']['outputdirectory'], f"Comparison_Cycles_{'-'.join(map(str, cycle_list))}.png")
        webbrowser.open(output_path)

    except Exception as e:
        update_status(f"Error: {str(e)}")
        logging.error(str(e))


def browse_files_popup():
    def add_file():
        filepaths = filedialog.askopenfilenames(filetypes=[("Excel files", "*.xlsx"), ("All Files", "*.*")])
        for filepath in filepaths:
            try:
                _, mass, _ = load_excel_data(filepath)
                file_infos.append({'path': filepath, 'mass': mass})
            except Exception as e:
                update_status(f"Error loading mass from file: {str(e)}")
                logging.error(str(e))
        update_file_list()

    def remove_selected_file():
        selected_items = file_listbox.curselection()
        if not selected_items:
            messagebox.showwarning("Error", "No file selected.")
            return
        for selected in reversed(selected_items):
            del file_infos[selected]
        update_file_list()

    def update_file_list():
        file_listbox.delete(0, tk.END)
        for info in file_infos:
            file_listbox.insert(tk.END, f"{info['path']} (Mass: {info['mass']} g)")

    def confirm_selection():
        selected_files_text.delete(1.0, tk.END)
        for info in file_infos:
            selected_files_text.insert(tk.END, f"{info['path']} (Mass: {info['mass']} g)\n")
        popup.destroy()

    popup = tk.Toplevel(root)
    popup.title("Select Excel Files")

    tk.Button(popup, text="Add Files", command=add_file).grid(row=0, column=0, padx=10, pady=5)
    tk.Button(popup, text="Remove Selected", command=remove_selected_file).grid(row=0, column=1, padx=10, pady=5)

    file_listbox = tk.Listbox(popup, selectmode=tk.MULTIPLE, width=80)
    file_listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

    confirm_button = tk.Button(popup, text="Confirm Selection", command=confirm_selection)
    confirm_button.grid(row=2, column=0, columnspan=2, pady=10)

    update_file_list()

def browse_dir():
    directory = filedialog.askdirectory()
    if directory:
        output_dir.set(directory)
        update_status(f"Selected output directory: {directory}")

def update_palette_preview(*args):
    color_palette = palette_var.get()
    config = configparser.ConfigParser()
    config.read(config_file)

    colors = []
    if color_palette.lower() == 'custom':
        start_color = start_color_var.get()
        end_color = end_color_var.get()
        num_cycles = len(parse_cycle_range(cycles_var.get()))
        colors = generate_gradient_colors(start_color, end_color, num_cycles)
        start_color_entry.grid(row=21, column=1, padx=10, pady=5)
        start_color_button.grid(row=21, column=2, padx=10, pady=5)
        end_color_entry.grid(row=22, column=1, padx=10, pady=5)
        end_color_button.grid(row=22, column=2, padx=10, pady=5)
    else:
        colors = config['PALETTES'][color_palette].split(',')
        start_color_entry.grid_forget()
        start_color_button.grid_forget()
        end_color_entry.grid_forget()
        end_color_button.grid_forget()

    preview_canvas.delete("all")
    for i, color in enumerate(colors):
        preview_canvas.create_rectangle(i * 20, 0, (i + 1) * 20, 20, fill=color, outline="")

def choose_start_color():
    color_code = colorchooser.askcolor(title="Choose Start Color")[1]
    if color_code:
        start_color_var.set(color_code)

def choose_end_color():
    color_code = colorchooser.askcolor(title="Choose End Color")[1]
    if color_code:
        end_color_var.set(color_code)

def on_closing():
    update_status("Deleting temporary pickle files...")
    remove_pickle_files([file_info['path'] for file_info in file_infos])
    root.destroy()

root = tk.Tk()
root.title("CV Graph Generator")
root.protocol("WM_DELETE_WINDOW", on_closing)  # Bind the close window protocol to on_closing

config = configparser.ConfigParser()
config.read(config_file)

file_infos = []

palette_options = get_color_palettes(config_file)

tk.Label(root, text="Select data files:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
tk.Button(root, text="Manage Files", command=browse_files_popup).grid(row=0, column=1, padx=10, pady=5)

selected_files_text = ScrolledText(root, height=5, width=50)
selected_files_text.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

tk.Label(root, text="Output directory:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
output_dir = tk.StringVar(value=config['DEFAULT']['outputdirectory'])
tk.Entry(root, textvariable=output_dir, width=50).grid(row=2, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=browse_dir).grid(row=2, column=2, padx=10, pady=5)

tk.Label(root, text="Color palette:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
palette_var = tk.StringVar(value=palette_options[0] if palette_options else 'Custom')
palette_combobox = ttk.Combobox(root, textvariable=palette_var, values=palette_options, state="readonly")
palette_combobox.grid(row=3, column=1, padx=10, pady=5)
palette_combobox.bind("<<ComboboxSelected>>", update_palette_preview)

preview_canvas = Canvas(root, width=200, height=20)
preview_canvas.grid(row=3, column=2, padx=10, pady=5)

tk.Label(root, text="Start Color:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
start_color_var = tk.StringVar(value="#0000FF")
start_color_entry = tk.Entry(root, textvariable=start_color_var, width=10)
start_color_button = tk.Button(root, text="Choose...", command=choose_start_color)

tk.Label(root, text="End Color:").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
end_color_var = tk.StringVar(value="#FF0000")
end_color_entry = tk.Entry(root, textvariable=end_color_var, width=10)
end_color_button = tk.Button(root, text="Choose...", command=choose_end_color)

tk.Label(root, text="Cycles to display / compare (e.g., 1-4,6,8):").grid(row=6, column=0, padx=10, pady=5, sticky=tk.W)
cycles_var = tk.StringVar(value="1-6")
tk.Entry(root, textvariable=cycles_var).grid(row=6, column=1, padx=10, pady=5)
cycles_var.trace("w", update_palette_preview)

tk.Label(root, text="Scan rate (mV/s):").grid(row=7, column=0, padx=10, pady=5, sticky=tk.W)
scan_rate_var = tk.StringVar(value="0.2")
tk.Entry(root, textvariable=scan_rate_var).grid(row=7, column=1, padx=10, pady=5)

tk.Label(root, text="Temperature:").grid(row=8, column=0, padx=10, pady=5, sticky=tk.W)
temp_var = tk.StringVar(value="auto")
tk.Entry(root, textvariable=temp_var).grid(row=8, column=1, padx=10, pady=5)

tk.Label(root, text="X Axis Min:").grid(row=9, column=0, padx=10, pady=5, sticky=tk.W)
x_min_var = tk.StringVar(value=config['DEFAULT']['xaxismin'])
tk.Entry(root, textvariable=x_min_var).grid(row=9, column=1, padx=10, pady=5)

tk.Label(root, text="X Axis Max:").grid(row=10, column=0, padx=10, pady=5, sticky=tk.W)
x_max_var = tk.StringVar(value=config['DEFAULT']['xaxismax'])
tk.Entry(root, textvariable=x_max_var).grid(row=10, column=1, padx=10, pady=5)

tk.Label(root, text="Y Axis Min:").grid(row=11, column=0, padx=10, pady=5, sticky=tk.W)
y_min_var = tk.StringVar(value=config['DEFAULT']['yaxismin'])
tk.Entry(root, textvariable=y_min_var).grid(row=11, column=1, padx=10, pady=5)

tk.Label(root, text="Y Axis Max:").grid(row=12, column=0, padx=10, pady=5, sticky=tk.W)
y_max_var = tk.StringVar(value=config['DEFAULT']['yaxismax'])
tk.Entry(root, textvariable=y_max_var).grid(row=12, column=1, padx=10, pady=5)

tk.Label(root, text="Major Tick Interval:").grid(row=13, column=0, padx=10, pady=5, sticky=tk.W)
major_tick_var = tk.StringVar(value=config['DEFAULT'].get('majortickinterval', '50'))
tk.Entry(root, textvariable=major_tick_var).grid(row=13, column=1, padx=10, pady=5)

grid_var = tk.BooleanVar(value=config['DEFAULT'].getboolean('showgrid'))
grid_checkbox = tk.Checkbutton(root, text="Show Gridlines", variable=grid_var)
grid_checkbox.grid(row=14, column=0, padx=10, pady=5)

tk.Label(root, text="Filename Template:").grid(row=15, column=0, padx=10, pady=5, sticky=tk.W)
filename_template_var = tk.StringVar(value=config['DEFAULT'].get('filenametemplate', '{temperature}_CV-Graph'))
tk.Entry(root, textvariable=filename_template_var).grid(row=15, column=1, padx=10, pady=5)

tk.Label(root, text="Smoothing Points:").grid(row=16, column=0, padx=10, pady=5, sticky=tk.W)
smoothing_points_var = tk.StringVar(value=config['DEFAULT']['smoothingpoints'])
tk.Entry(root, textvariable=smoothing_points_var).grid(row=16, column=1, padx=10, pady=5)

tk.Button(root, text="Create Graph", command=create_graph).grid(row=19, column=0, pady=20)
tk.Button(root, text="Compare Cycles", command=compare_cycles).grid(row=19, column=1, pady=20)

status_label = tk.Label(root, text="")
status_label.grid(row=20, column=0, columnspan=3, pady=10)

update_palette_preview()

root.mainloop()
