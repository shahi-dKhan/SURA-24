import os
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import sys
def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    if low <= 0 or high >= 1:
        raise ValueError(f"Invalid lowcut ({lowcut}) or highcut ({highcut}) values compared to Nyquist ({nyquist}).")
    b, a = butter(order, [low, high], btype='band')
    y = filtfilt(b, a, data)
    return y

def butter_lowpass_filter(data, cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    if normal_cutoff >= 1:
        raise ValueError(f"Invalid cutoff frequency ({cutoff}) compared to Nyquist ({nyquist}).")
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y

def emg_envelope_all_channels(emg_data, fs, lowcut=20, highcut=249, low_pass_cutoff=10):
    envelope_df = pd.DataFrame()
    for col in emg_data.columns:
        bandpassed_signal = butter_bandpass_filter(emg_data[col], lowcut, highcut, fs)
        rectified_signal = np.abs(bandpassed_signal)
        envelope = butter_lowpass_filter(rectified_signal, low_pass_cutoff, fs)
        envelope_df[col] = envelope
    return envelope_df

def main():
    input_file = sys.argv[1]
    emg_data = pd.read_csv(input_file,sep=';',low_memory=False)
    fs = 500
    lowcut = 20
    highcut = 249  
    emg_envelopes = emg_envelope_all_channels(emg_data[['CH1', 'CH2', 'CH3', 'CH4', 'CH5', 'CH6', 'CH7', 'CH8']], fs)
    emg_envelopes['AccX'] = emg_data['AccX']
    emg_envelopes['AccY'] = emg_data['AccY']
    emg_envelopes['AccZ'] = emg_data['AccZ']
    emg_envelopes['GyX'] = emg_data['GyX']
    emg_envelopes['GyY'] = emg_data['GyY']
    emg_envelopes['GyZ'] = emg_data['GyZ']
    output_csv_file_path = sys.argv[2]
    emg_envelopes.to_csv(output_csv_file_path, sep = ';',index=False)

# Call the main function
if __name__ == "__main__":
    main()
