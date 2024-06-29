import os
from loadExcel import load_excel_data
from processExcel import process_data
from createCVgraph import create_cv_graph

def main(file_path, channel_sheet, global_info_sheet, output_dir, log):
    os.makedirs(output_dir, exist_ok=True)
    
    log("Loading Excel data...")
    try:
        channel_data, mass, temperature = load_excel_data(file_path, channel_sheet, global_info_sheet)
    except ValueError as e:
        log(f"Error loading Excel data: {e}")
        return
    
    log(f"Mass: {mass}, Temperature: {temperature}")
    
    log("Processing data...")
    cycle_data = process_data(channel_data, mass)
    
    log(f"Creating CV graphs for {temperature}...")
    create_cv_graph(cycle_data, temperature, output_dir)
    
    log("Process complete.")
