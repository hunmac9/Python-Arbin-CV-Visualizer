import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import logging
from loadExcel import load_excel_data, parse_temperature_from_filename
from processExcel import process_data
from createCVgraph import create_cv_graph
import webbrowser

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        
        file_path = data_path.get()
        output_directory = output_dir.get()
        color_palette = palette_var.get()
        
        cycle_range = cycles_var.get()
        cycle_list = parse_cycle_range(cycle_range)
        
        scan_rate = scan_rate_var.get()
        temperature = temp_var.get()
        
        if temperature == 'auto':
            temperature = parse_temperature_from_filename(file_path)
        
        update_status("Loading Excel data...")
        channel_data, mass, temp_auto = load_excel_data(file_path)
        update_status("Processing data...")
        cycle_data = process_data(channel_data, mass)
        
        temp = temperature if temperature != 'auto' else temp_auto
        
        update_status("Creating CV graph...")
        create_cv_graph(cycle_data, temp, scan_rate, cycle_list, color_palette, output_directory)
        update_status(f"Graph saved successfully to {output_directory}")
        
        # Open the graph in the default image viewer
        output_path = f'{output_directory}/{temp}_CV-Graph.png'
        webbrowser.open(output_path)
        
    except Exception as e:
        update_status(f"Error: {str(e)}")
        logging.error(str(e))

def browse_file():
    filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("All Files", "*.*")])
    if filepath:
        data_path.set(filepath)
        update_status(f"Selected data file: {filepath}")

def browse_dir():
    directory = filedialog.askdirectory()
    if directory:
        output_dir.set(directory)
        update_status(f"Selected output directory: {directory}")

root = tk.Tk()
root.title("CV Graph Generator")

# Data file path selection
tk.Label(root, text="Select data file:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
data_path = tk.StringVar()
tk.Entry(root, textvariable=data_path, width=50).grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2, padx=10, pady=5)

# Output directory selection
tk.Label(root, text="Output directory:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
output_dir = tk.StringVar(value='/Users/hunmac/Python-CV-Visualizer/processedData')
tk.Entry(root, textvariable=output_dir, width=50).grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=browse_dir).grid(row=1, column=2, padx=10, pady=5)

# Color palette selection
tk.Label(root, text="Color palette:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
palette_var = tk.StringVar(value="Default")
palette_options = [
    'Default (Dark Blue to Light Blue)', 
    'Palette 1 (Dark Blue to Red)', 
    'Palette 2 (Grey to Red)', 
    'Palette 3 (Dark Blue to Orange)'
]
ttk.Combobox(root, textvariable=palette_var, values=palette_options, state="readonly").grid(row=2, column=1, padx=10, pady=5)

# Number of cycles to display
tk.Label(root, text="Cycles to display (e.g., 1-4,6-10):").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
cycles_var = tk.StringVar(value="1-6")
tk.Entry(root, textvariable=cycles_var).grid(row=3, column=1, padx=10, pady=5)

# Scan rate input
tk.Label(root, text="Scan rate (mV/s):").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
scan_rate_var = tk.StringVar(value="0.2")
tk.Entry(root, textvariable=scan_rate_var).grid(row=4, column=1, padx=10, pady=5)

# Temperature input
tk.Label(root, text="Temperature:").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
temp_var = tk.StringVar(value="auto")
tk.Entry(root, textvariable=temp_var).grid(row=5, column=1, padx=10, pady=5)

# Create graph button
tk.Button(root, text="Create Graph", command=create_graph).grid(row=6, column=1, pady=20)

# Status label
status_label = tk.Label(root, text="")
status_label.grid(row=7, column=0, columnspan=3, pady=10)

root.mainloop()
