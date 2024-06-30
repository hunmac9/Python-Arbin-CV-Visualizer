import pandas as pd

def process_data(channel_data, mass, smoothing_points=8):
    print("Processing channel data...")
    cycle_data = {}

    for i, row in channel_data.iterrows():
        cycle_index = int(row['Cycle_Index'])  # Ensure Cycle_Index is an integer

        if cycle_index not in cycle_data:
            cycle_data[cycle_index] = {
                'Voltage(V)': [],
                'Current(A)': [],
                'Current (mA)': [],
                'Current Density (mA g^-1)': [],
                'Smoothed Current (mA)': [],
                'Smoothed Current Density (mA g^-1)': []
            }

        voltage = row['Voltage(V)']  # Assuming Voltage(V) is the correct column name
        current = row['Current(A)']  # Assuming Current(A) is the correct column name

        current_ma = current * 1000
        current_density = current_ma / mass

        cycle_data[cycle_index]['Voltage(V)'].append(voltage)
        cycle_data[cycle_index]['Current(A)'].append(current)
        cycle_data[cycle_index]['Current (mA)'].append(current_ma)
        cycle_data[cycle_index]['Current Density (mA g^-1)'].append(current_density)

        if smoothing_points > 0 and len(cycle_data[cycle_index]['Current (mA)']) >= smoothing_points:
            smoothed_current = sum(cycle_data[cycle_index]['Current (mA)'][-smoothing_points:]) / smoothing_points
            smoothed_current_density = sum(cycle_data[cycle_index]['Current Density (mA g^-1)'][-smoothing_points:]) / smoothing_points
        else:
            smoothed_current = current_ma
            smoothed_current_density = current_density

        cycle_data[cycle_index]['Smoothed Current (mA)'].append(smoothed_current)
        cycle_data[cycle_index]['Smoothed Current Density (mA g^-1)'].append(smoothed_current_density)

    print("Channel data processing complete.")
    return cycle_data
