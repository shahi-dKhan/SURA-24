import pandas as pd
import sys
def select_and_sample_columns(input_file, output_file, columns, step=10, separator=';'):
    df = pd.read_csv(input_file, sep=separator, low_memory=False)
    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns:
        print(f"Error: The following columns are missing from the CSV: {missing_columns}")
        return
    selected_columns = df[columns]
    sampled_data = selected_columns.iloc[::step]
    sampled_data.to_csv(output_file, sep=separator, index=False)
    
if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    selected_columns = ['CH1','CH2','CH3','CH4','CH5','CH6','CH7','CH8','AccX', 'AccY', 'AccZ', 'GyX', 'GyY', 'GyZ'] 
    select_and_sample_columns(input_file, output_file, selected_columns, step=10)
