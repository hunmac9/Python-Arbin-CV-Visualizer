import pandas as pd
import logging
import pickle
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def store_processed_data(cycle_data, filename):
    with open(filename, 'wb') as file:
        pickle.dump(cycle_data, file)
    logging.info(f"Cycle data stored successfully in '{filename}'.")

def load_processed_data(filename):
    if os.path.exists(filename):
        with open(filename, 'rb') as file:
            cycle_data = pickle.load(file)
        logging.info(f"Cycle data loaded successfully from '{filename}'.")
        return cycle_data
    else:
        raise FileNotFoundError(f"The file '{filename}' does not exist.")

def process_data(channel_data, mass, smoothing_points=8):
    logging.info("Processing channel data...")

    cycle_data = {}

    # Check if 'Cycle_Index' exists in the DataFrame
    if 'Cycle_Index' not in channel_data.columns:
        raise KeyError("The required column 'Cycle_Index' is missing from the data.")

    for i, row in channel_data.iterrows():
        # Ensure 'Cycle_Index' is correctly extracted
        try:
            cycle_index = int(row['Cycle_Index'])  # Ensure Cycle_Index is an integer
        except ValueError:
            raise ValueError(f"Invalid Cycle_Index value at row {i}: {row['Cycle_Index']}")

        # Initialize the dictionary for this cycle_index if it doesn't exist
        if cycle_index not in cycle_data:
            cycle_data[cycle_index] = {
                'Voltage(V)': [],
                'Current(A)': [],
                'Current (mA)': [],
                'Current Density (mA g^-1)': [],
                'Smoothed Current (mA)': [],
                'Smoothed Current Density (mA g^-1)': []
            }

        # Extract relevant data
        voltage = row.get('Voltage(V)')
        current = row.get('Current(A)')

        # Ensure that voltage and current are not missing
        if pd.isnull(voltage) or pd.isnull(current):
            raise ValueError(f"Missing data on row {i}: Voltage or Current")

        # Convert current to mA and calculate current density
        current_ma = current * 1000
        current_density = current_ma / mass

        # Append extracted values to the respective lists
        cycle_data[cycle_index]['Voltage(V)'].append(voltage)
        cycle_data[cycle_index]['Current(A)'].append(current)
        cycle_data[cycle_index]['Current (mA)'].append(current_ma)
        cycle_data[cycle_index]['Current Density (mA g^-1)'].append(current_density)

        # Calculate smoothed values if required
        if smoothing_points > 0 and len(cycle_data[cycle_index]['Current (mA)']) >= smoothing_points:
            smoothed_current = sum(cycle_data[cycle_index]['Current (mA)'][-smoothing_points:]) / smoothing_points
            smoothed_current_density = sum(cycle_data[cycle_index]['Current Density (mA g^-1)'][-smoothing_points:]) / smoothing_points
        else:
            smoothed_current = current_ma
            smoothed_current_density = current_density

        # Append smoothed values to respective lists
        cycle_data[cycle_index]['Smoothed Current (mA)'].append(smoothed_current)
        cycle_data[cycle_index]['Smoothed Current Density (mA g^-1)'].append(smoothed_current_density)

    logging.info("Channel data processing complete.")

    return cycle_data
