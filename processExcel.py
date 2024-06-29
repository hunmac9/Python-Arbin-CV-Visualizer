import pandas as pd

def process_data(channel_data, mass):
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

        if len(cycle_data[cycle_index]['Current (mA)']) >= 8:
            smoothed_current = sum(cycle_data[cycle_index]['Current (mA)'][-8:]) / 8
            smoothed_current_density = sum(cycle_data[cycle_index]['Current Density (mA g^-1)'][-8:]) / 8
        else:
            smoothed_current = current_ma
            smoothed_current_density = current_density

        cycle_data[cycle_index]['Smoothed Current (mA)'].append(smoothed_current)
        cycle_data[cycle_index]['Smoothed Current Density (mA g^-1)'].append(smoothed_current_density)

    print("Channel data processing complete.")
    return cycle_data
