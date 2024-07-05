import numpy as np
from skimage import io, color, feature
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import utm
import json


def run_moments_calculation(
    times_width:dict = {},
    moment_windows:list[tuple] = [(5, 15), (16, 25), (26, 35), (36, 45)],
    data_file_path:str = None,
    output_path:str = './'
) -> None: 
    """

        Perform moments calculation based on provided parameters.

        Args:
        - times_width (dict): A dictionary containing gate values and corresponding width.
        - moment_windows (list[tuple]): A list of tuples indicating moment windows, each tuple specifying start and end gates.
        - ztem_file_path (str): Path to the ZTEM information file.
        - output_path (str): Path to the directory where output files will be written. Default is the current directory.

        Returns:
        - None

        This function reads ZTEM information from a file, performs calculations for moments, and writes the output to files
        based on the provided parameters.

    """

    headers = []
    vtem_data = {}
    current_line = None

    data_info_file = open(data_file_path, 'r')

    # interpret the file. these files are structured as blocks so it can be tricky
    for i, line in enumerate(data_info_file):

        if 'Longitude' in line:
        
            headers = line.split()[1:]
        

        if 'Line' in line:
            current_line = line.split()[-1]

            vtem_data[current_line] = {}

            for title in headers:
                vtem_data[current_line][title] = []

        if 'Tie' in line:

            current_line = None
            
        elif 'Line' not in line and '/' not in line and 'Tie' not in line:

            if current_line is not None:

                try:
                    # split the line to find the data
                    string_utm = line.split()

                    for ii in range(len(headers)):

                        try:
                            vtem_data[current_line][headers[ii]].append(float(string_utm[ii]))
                        except ValueError as e:
                            vtem_data[current_line][headers[ii]].append(string_utm[ii])

                
                except ValueError as e:
                    print(f' error but passing: {e}')
                    pass

    # write to files
    keys = list(vtem_data.keys())

    level_xyz = [None] * len(moment_windows)
    for ii in range(len(moment_windows)):
        level_xyz[ii] = open(f'{output_path}moments_windows_{moment_windows[ii][0]}-{moment_windows[ii][1]}.xyz', 'w+')
        level_xyz[ii].write(f'x,y,z,datum\n')
        
    for key in vtem_data.keys():    
        for kk in range(len(vtem_data[key]['Latitude'])):
            for jj in range(len(moment_windows)):
                # go through each line and assign the data
                output = utm.from_latlon(
                    vtem_data[key]['Latitude'][kk],
                    vtem_data[key]['Longitude'][kk]
                )

                x = output[0]
                y = output[1]

                z = vtem_data[key]['DEM'][kk]

                gate_span = np.arange(
                    moment_windows[jj][0],
                    moment_windows[jj][1]
                )

                moment_calc = 0
                total_time = 0

                for gate in gate_span:

                    moment_calc += times_width[gate] * vtem_data[key][f'SFz[{gate}]'][kk]
                    total_time += times_width[gate]

                # write to file
                level_xyz[jj].write(f'{x},{y},{z},{moment_calc}\n')

    # close the files
    for ii in range(len(moment_windows)):
        level_xyz[ii].close()


if __name__ == '__main__':

    # set the times used to process the survey TDEM data.
    # Refer to report to get the window widths 
    times_width_east_rim = {
        4:0.005,
        5:0.005,
        6:0.005,
        7:0.005,
        8:0.006,
        9:0.007,
        10:0.008,
        11:0.009,
        12:0.010,
        13:0.012,
        14:0.013,
        15:0.015,
        16:0.018,
        17:0.020,
        18:0.023,
        19:0.027,
        20:0.030,
        21:0.035,
        22:0.040,
        23:0.046,
        24:0.053,
        25:0.061,
        26:0.070,
        27:0.081,
        28:0.093,
        29:0.107,
        30:0.122,
        31:0.141,
        32:0.161,
        33:0.185,
        34:0.214,
        35:0.245,
        36:0.281,
        37:0.323,
        38:0.370,
        39:0.427,
        40:0.490,
        41:0.560,
        42:0.646,
        43:0.742,
        44:0.852,
        45:0.979,
        46:1.125,
    }

    # path to the ascii geosoft xyz file
    ztem_file_path = '/home/juanito/Documents/projects/east_rim/data/GL230050_EastRim_Final.XYZ'

    # path for the output xyz files containing the moments calculation
    output_path = '/home/juanito/Documents/projects/east_rim/'

    # run the moments calculation code
    run_moments_calculation(

        times_width = times_width_east_rim,
        moment_windows = [(5, 15), (16, 25), (26, 35), (36, 45)],
        data_file_path = ztem_file_path,
        output_path=output_path

    )
