import pandas as pd
import sys

def multiply_column_in_csv(input_file, output_file, multiplier, separator=';'):
    # Load the CSV file into a pandas DataFrame with the specified separator
    df = pd.read_csv(input_file,sep=';',skiprows=1)    
    
    # Multiply the specified column by the multiplier
    df['AccX'] = df['AccX'] * 0.000061035*9.8
    df['AccY'] = df['AccY'] * 0.000061035*9.8
    df['AccZ'] = df['AccZ'] * 0.000061035*9.8
    df['GyX'] = df['GyX'] * 0.01526
    df['GyY'] = df['GyY'] * 0.01526
    df['GyZ'] = df['GyZ'] * 0.01526
    df['CH1'] = df['CH1'] * 0.045
    df['CH2'] = df['CH2'] * 0.045
    df['CH3'] = df['CH3'] * 0.045
    df['CH4'] = df['CH4'] * 0.045
    df['CH5'] = df['CH5'] * 0.045
    df['CH6'] = df['CH6'] * 0.045
    df['CH7'] = df['CH7'] * 0.045
    df['CH8'] = df['CH8'] * 0.045
    # Save the modified DataFrame back to a CSV file with the specified separator
    df.to_csv(output_file, sep=separator, index=False)
if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    multiplier_value = 2.5
    multiply_column_in_csv(input_file, output_file, multiplier_value)

