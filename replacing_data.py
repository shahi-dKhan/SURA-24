import os
import pandas as pd
import glob

# Directories
angle_calculated_dir = './angle_calculated/'
envelopes_dir = './envelopes/'

# Get all CSV files in angle_calculated directory
angle_files = glob.glob(os.path.join(angle_calculated_dir, '*.csv'))

# Iterate over each file in angle_calculated directory
for angle_file in angle_files:
    # Get the base name of the file (to match with the corresponding envelope file)
    base_name = os.path.basename(angle_file)
    
    # Construct the corresponding envelope file path
    envelope_file = os.path.join(envelopes_dir, base_name)
    
    # Check if the corresponding envelope file exists
    if not os.path.exists(envelope_file):
        print(f"Envelope file for {base_name} not found. Skipping.")
        continue
    
    # Load the angle_calculated and envelope files as DataFrames
    angle_df = pd.read_csv(angle_file)
    envelope_df = pd.read_csv(envelope_file)
    
    # Ensure both files have 'CH1' to 'CH8' columns
    channels = [f'CH{i}' for i in range(1, 9)]
    
    if not all(col in angle_df.columns for col in channels):
        print(f"One or more channels (CH1 to CH8) missing in {base_name}. Skipping.")
        continue
    
    if not all(col in envelope_df.columns for col in channels):
        print(f"One or more channels (CH1 to CH8) missing in envelope file {base_name}. Skipping.")
        continue
    
    # Replace the 'CH1' to 'CH8' columns in angle_calculated with the corresponding values from the envelope file
    angle_df[channels] = envelope_df[channels]
    
    # Save the modified DataFrame back to the angle_calculated file
    angle_df.to_csv(angle_file, index=False)
    
    print(f"Replaced channels in {base_name} using envelope data.")

print("Channel replacement complete.")
