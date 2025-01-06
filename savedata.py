import tkinter as tk
from tkinter import filedialog
import math
import os
import osu
import re
import json
import sys
from oauth2client.service_account import ServiceAccountCredentials

def save_transformed_data_to_file(data, output_file="transformed_hit_objects.txt"):
    output_file = r"C:\Users\imjos\OneDrive\Desktop\thon\transformed_hit_objects.txt"
    with open(output_file, 'w') as f:
        f.write("Distance, Delta Time, Velocity, Time\n")  # Header line
        for distance, delta_time, velocity, time in data:
            f.write(f"{distance}, {delta_time}, {velocity}, {time} \n")
    print(f"Transformed data saved to {output_file}")

def save_jump_to_file(data_tuple, title):
    file_path = r"C:\Users\imjos\OneDrive\Desktop\thon\jump.txt"
    try:
        with open(file_path, 'w') as file:
            file.write(f"{title}\n")
            for item in data_tuple:
                file.write(f"{item}\n")
        print(f"Tuple saved to {file_path}")
    except Exception as e:
        print(f"An error occurred while saving the tuple: {e}")    

def save_stream_to_file(data_tuple, title):
    file_path = r"C:\Users\imjos\OneDrive\Desktop\thon\stream.txt"
    try:
        with open(file_path, 'w') as file:
            file.write(f"{title}\n")
            for item in data_tuple:
                file.write(f"{item}\n")
        print(f"Tuple saved to {file_path}")
    except Exception as e:
        print(f"An error occurred while saving the tuple: {e}")    

def save_rhythm_to_file(data_tuple, title):
    file_path = r"C:\Users\imjos\OneDrive\Desktop\thon\rhythm.txt"
    try:
        with open(file_path, 'w') as file:
            file.write(f"{title}\n")
            for item in data_tuple:
                file.write(f"{item}\n")
        print(f"Tuple saved to {file_path}")
    except Exception as e:
        print(f"An error occurred while saving the tuple: {e}")    

def save_stats_to_file(file_path, stats):
    with open(file_path, 'w') as file:
        for i, stat_data in enumerate(stats, start=1):
            # Write the name of the stat category based on the order or custom labels
            file.write(f"Stat {i}:\n")
            # Convert the JSON object to a pretty-printed string
            json_data = json.dumps(stat_data, indent=4)
            file.write(json_data + "\n\n")  