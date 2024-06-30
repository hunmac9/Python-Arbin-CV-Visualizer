import pandas as pd
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_temperature_from_filename(file_path):
    match = re.search(r'(\d+)[C|c]', file_path)
    if match:
        temperature = match.group(1) + '°C'
    else:
        temperature = 'Unknown'
    return temperature

def find_channel_sheet(xls):
    try:
        # Check if 'Channel_4_1' exists in the sheet names
        if 'Channel_4_1' in xls.sheet_names:
            return 'Channel_4_1'
        else:
            # Fall back to any sheet containing 'Channel_' if 'Channel_4_1' is not found
            return next(sheet for sheet in xls.sheet_names if 'Channel_' in sheet)
    except (IndexError, StopIteration) as e:
        logging.error(f"Error finding channel sheet: {str(e)}")
        raise

def load_excel_data(file_path):
    logging.info(f"Loading Excel file: {file_path}")
    xls = pd.ExcelFile(file_path)
    
    # Dynamically determine the channel sheet name
    channel_sheet = find_channel_sheet(xls)
    logging.info(f"Loading sheet: {channel_sheet}")
    channel_data = pd.read_excel(xls, sheet_name=channel_sheet)
    logging.info(f"Channel data loaded: {channel_data.shape}")
    
    global_info_sheet = xls.sheet_names[0]
    logging.info(f"Loading sheet: {global_info_sheet}")
    global_info = pd.read_excel(xls, sheet_name=global_info_sheet, header=None)
    logging.info(f"Global_Info data loaded: {global_info.shape}")
    
    # Debug: Print the full contents of the global_info DataFrame
    logging.debug("Global_Info sheet full contents:\n" + global_info.to_string())
    
    try:
        # Directly access specific cells H4 and H5
        mass_value = global_info.iloc[4, 7]  # Cell H5 (5th row, 8th column)
        logging.info(f"Extracted mass value: {mass_value}")
        
        if not isinstance(mass_value, (int, float)):
            raise ValueError(f"Mass value in H5 is not numeric: {mass_value}")
    except IndexError as e:
        raise ValueError("Global_Info sheet does not have enough rows or columns to extract mass. Error: " + str(e))
    
    temperature = parse_temperature_from_filename(file_path)
    logging.info(f"Temperature extracted: {temperature}")

    print(channel_data)
    
    return channel_data, mass_value, temperature