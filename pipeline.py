import glob
import subprocess
import os
import sys
import re

output1_dir = "./output1_dir/"
output2_dir = "./output2_dir/"
output3_dir = "./envelopes/"
os.makedirs(output1_dir, exist_ok=True)
os.makedirs(output2_dir, exist_ok=True)
os.makedirs(output3_dir, exist_ok=True)  # Ensure envelopes directory is created

csv_files = glob.glob('./*.csv')
for idx, csv_file in enumerate(csv_files, start=1):
    base_name = os.path.basename(csv_file)
    print(f"Processing file {idx}: {base_name}")
    
    # Step 1: Running the first script
    output1_file = os.path.join(output1_dir, f"output1_{base_name}")
    subprocess.run(["python3", "runningforsep.py", csv_file, output1_file], check=True)
    
    # Step 2: Renaming the file based on regex match
    weight, position, run_number = re.findall(r"_(\d+\.?\d*kg)_(lower|upper)_run(0[1-3])", base_name)[0]
    new_base_name = f"{weight}_{position}_run{run_number}.csv"
    final_output_file = os.path.join(output2_dir, new_base_name)
    
    # Step 3: Running the second script
    subprocess.run(["python3", "envelope.py", output1_file, final_output_file], check=True)
    
    # Step 4: Running the third script (pruning)
    output = os.path.join(output3_dir, new_base_name)
    result = subprocess.run(["python3", "pruning.py", final_output_file, output], capture_output=True, text=True)
    
    # Display stdout and stderr for debugging purposes
    print(result.stdout)
    print(result.stderr)
    
    print(f"Processed file {idx}: {base_name} -> {new_base_name}")

print("Processing complete. Output CSV files saved.")
