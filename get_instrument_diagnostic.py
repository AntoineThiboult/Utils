# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 18:30:08 2023
@author: Antoine Thiboult

Get the instrument diagnostics for the variable diag_variable that is stored
as bits. Decompose the code and print a human readable description of the
diagnostic as well as its frequency of occurence between the dates date_start
and date_end.
The date format in the file name should be specified.
Works for LICOR LI7700 and Campbell Scientific Irgason.
"""

import pathlib
import pandas as pd
import numpy as np
from tqdm import tqdm

dir_path = pathlib.Path("Path_to_directory")
diag_variable = 'diag_77'
date_start = '20220615 0000'
date_end   = '20231025 0000'
file_format = '%Y%m%d_%H%M_eddy.csv'


def build_diag_header_table(diag_variable):
    if diag_variable == 'diag_77':
        diag_header_table = pd.DataFrame(
            columns=['val','code'],
            data = np.array(
                [[32768, 'Instrument is not ready'],
                [16384, 'No laser signal detected'],
                [8192, 'Reference methane signal not locked'],
                [4096, 'Optical path thermocouple failure'],
                [2048, 'Laser cooler unregulated'],
                [1024, 'Block temperature unregulated'],
                [512, 'Lower mirror spin motor on'],
                [256, 'Washer pump motor running'],
                [128, 'Upper mirror heater on'],
                [64, 'Lower mirror heater on'],
                [32, 'Calibration in process'],
                [16, 'Mirror cleaner motor failure'],
                [8, 'Bad thermocouple values'],
                [4, 'Bad thermocouple values'],
                [2, 'Bad thermocouple values'],
                [1, 'LI-7550 Attached']],
                ))
    if diag_variable == 'diag_irga':
        diag_header_table = pd.DataFrame(
            columns=['val','code'],
            data = np.array(
                [[4194304, 'Differential pressure exceeds limits'],
                [2097152, 'Heater control error'],
                [1048576, 'Gas head calibration signature error'],
                [524288, 'H2O signal level too low'],
                [262144, 'CO2 signal level too low'],
                [131072, 'Moving variation in H2O Ioexceeds limits'],
                [65536, 'Moving variation in CO2 Io exceeds limits'],
                [32768, 'H2O Io exceeds limits'],
                [16384, 'H2O I exceeds limits'],
                [8192, 'CO2 Io exceeds limits'],
                [4096, 'CO2 I exceeds limits'],
                [2048, 'Invalid ambient pressure'],
                [1024, 'Invalid ambient temperature'],
                [512, 'Gas input data out of sync with home pulse'],
                [256, 'Gas head not powered'],
                [128, 'Source current exceeds limits'],
                [64, 'Invalid source temperature'],
                [32, 'Source power exceeds limits'],
                [16, 'TEC temperature exceeds limits'],
                [8, 'Motor speed outside of limits'],
                [4, 'Gas analyzer is starting up'],
                [2, 'General system fault'],
                [1, 'Data are suspect (there is an active diagnostic flag)']],
                ))
    if diag_variable == 'diag_sonic':
        diag_header_table = pd.DataFrame(
            columns=['val','code'],
            data = np.array(
                [[32, 'Sonic head calibration signature error'],
                [16, 'Acquiring ultrasonic signals'],
                [8, 'Delta temperature exceeds limits'],
                [4, 'Poor signal lock'],
                [2, 'Amplitude is too high'],
                [1, 'Amplitude is too low']],
                ))
    diag_header_table['val'] = diag_header_table['val'].astype(int)
    diag_header_table.index = np.log2(diag_header_table['val']).astype(int)
    return diag_header_table


def print_diag_header_table(diag_code, timestamp, diag_header_table):
    print(f'{pd.to_datetime(timestamp).strftime("%Y/%m/%d %Hh%M")}. Error {diag_code}:')
    bin_str = '{0:b}'.format(diag_code)
    is_bad_diag = (diag_code < 0 ) & \
        (len(bin_str) > diag_header_table.shape[0])

    if is_bad_diag:
        print(f'{diag_code} is a suspicious diagnostic. No possible interpretation of diagnostic code.\n')
        return

    for i in range(len(bin_str)):
        if int(bin_str[-i-1]) != 0:
            print(f'\t{diag_header_table.loc[i,"code"]}')
    print('\n')


### Variable initialization ###
date_range = pd.date_range(
    pd.to_datetime(date_start),
    pd.to_datetime(date_end),
    freq='30min').strftime(file_format)
diagnostics = []
timestamps = []
all_value_counts = {}

### Read files ###
print('Reading files...')
for file in tqdm(date_range):

    if dir_path.joinpath(file).exists():
        df = pd.read_csv(dir_path.joinpath(file),skiprows=[0,2,3])
    else:
        print(f"File {dir_path.joinpath(file)} doesn't exist")
        continue
    if diag_variable in df.columns:
        unique_indices = df.drop_duplicates(subset=diag_variable).index
    else:
        print(f'{diag_variable} not present in file {dir_path.joinpath(file)}')
        continue

    # Perform value counts on diag_variable column
    counts = df[diag_variable].value_counts()
    # Accumulate the value counts in the dictionary
    for index, count in counts.items():
        all_value_counts[index] = all_value_counts.get(index, 0) + count

    # Get timing of the diagnostic code
    for i in df.loc[unique_indices,['TIMESTAMP', diag_variable]].index:
        if df.loc[i,diag_variable] not in diagnostics:
            diagnostics.append(int(df.loc[i,diag_variable]))
            timestamps.append(df.loc[i,'TIMESTAMP'])

# Convert the dictionary to a DataFrame for easy manipulation and analysis
diag_counts = pd.DataFrame(list(all_value_counts.items()), columns=[diag_variable, 'count'])
diag_counts = diag_counts.sort_values(by='count', ascending=False)

### Print error codes encountered, number of occurences and their timing ###
print(diag_counts,'\n')
diag_header_table = build_diag_header_table(diag_variable)
for i_diag, i_timestamp in zip(diagnostics,timestamps):
    print_diag_header_table(i_diag, i_timestamp, diag_header_table)