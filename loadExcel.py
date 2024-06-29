import pandas as pd
import re

def parse_temperature_from_filename(file_path):
    match = re.search(r'(\d+)[C|c]', file_path)
    if match:
        temperature = match.group(1) + '°C'
    else:
        temperature = 'Unknown'
    return temperature

def load_excel_data(file_path):
    print(f"Loading Excel file: {file_path}")
    xls = pd.ExcelFile(file_path)
    
    # Dynamically determine the channel sheet name
    channel_sheet = xls.sheet_names[1]
    print(f"Loading sheet: {channel_sheet}")
    
    channel_data = pd.read_excel(xls, sheet_name=channel_sheet)
    print(f"Channel data loaded: {channel_data.shape}")
    
    global_info_sheet = xls.sheet_names[0]
    print(f"Loading sheet: {global_info_sheet}")
    global_info = pd.read_excel(xls, sheet_name=global_info_sheet, header=None)
    print(f"Global_Info data loaded: {global_info.shape}")
    
    # Debug: Print the full contents of the global_info DataFrame
    print("Global_Info sheet full contents:\n", global_info)
    
    try:
        # Directly access specific cells H4 and H5
        mass_value = global_info.iloc[4, 7]  # Cell H5 (5th row, 8th column)
        print(f"Extracted mass value: {mass_value}")
        
        if not isinstance(mass_value, (int, float)):
            raise ValueError(f"Mass value in H5 is not numeric: {mass_value}")
    except IndexError as e:
        raise ValueError("Global_Info sheet does not have enough rows or columns to extract mass. Error: " + str(e))
    
    temperature = parse_temperature_from_filename(file_path)
    print(f"Temperature extracted: {temperature}")
    
    return channel_data, mass_value, temperature
