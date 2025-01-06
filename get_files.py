import tkinter as tk
from tkinter import filedialog
import math
import os
import osu
import re
import json
import sys
from oauth2client.service_account import ServiceAccountCredentials


#finds bpm cs and title
def extract_metadata(osu_file_path):
    timing_points = []
    circle_size = None
    artist = None
    timing_points_section_found = False

    with open(osu_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            # Check for the MetaData section and extract artist
            if line.startswith("[MetaData]"):
                continue
            if line.startswith("Title:"):
                title = line.split(':', 1)[1].strip()
            if line.startswith("Artist:"):
                artist = line.split(':', 1)[1].strip()
            # Check for Difficulty section and extract CircleSize
            elif line.startswith("[Difficulty]"):
                continue
            elif line.startswith("CircleSize:"):
                circle_size = float(line.split(':', 1)[1].strip())

            # Check for TimingPoints section
            elif line.startswith("[TimingPoints]"):
                timing_points_section_found = True
                continue
            elif timing_points_section_found:
                if line.startswith("["):
                    break  # Exit if we reach a new section

                # Extract timing point values
                parts = line.split(',')
                if len(parts) > 1:
                    time_sig = float(parts[1].strip())
                    if time_sig > 0:
                        timing_points.append(time_sig)

    # Ensure only one unique BPM, else return None
    if len(set(timing_points)) == 1:
        bpm = [timing_points[0]]
    else: 
        bpm = timing_points
        bpm.sort(reverse=True)
    return bpm, circle_size, title

#for running 1 by 1
def get_osu_file():
    # Hide the root window
    root = tk.Tk()
    root.withdraw()

    # Open a file dialog to select .osu files only
    file_path = filedialog.askopenfilename(
        title="Select an OSU File",
        filetypes=[("OSU Files", "*.osu")]  # Restrict to .osu files
    )

    if file_path:
        print(f"Selected file: {file_path}")
        return file_path  # Return the selected file path
    else:
        print("No file selected.")
        return None  # Return None if no file is selected


