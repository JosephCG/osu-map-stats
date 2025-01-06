import tkinter as tk
from tkinter import filedialog
import math
import os
import re
import json
import sys
from statistics import median

def get_jump_statistics(jump_data, thresholds):
    if len(jump_data[0]) == 4:
        jump_data = [(length, peak_velocity, velocities)
        for (start_time, length, peak_velocity, velocities) in jump_data]
    peak_velocity_find = max(jump_data, key=lambda x: x[1], default=(0, 0))[1]  # (length, peak_velocity, velocities)
    longest_jump_pattern_find = max(jump_data, key=lambda x: x[0], default=(0, 0))[0]  # (length, peak_velocity, velocities)
    associate_velocity = max(x[0] for x in jump_data if x[1] == peak_velocity_find)
    associate_length = max(x[1] for x in jump_data if x[0] == longest_jump_pattern_find)

    peak_jump_velocity = (peak_velocity_find, associate_velocity)
    longest_jump_pattern = (longest_jump_pattern_find ,associate_length)
    
    jump_counts = {}
    for threshold in thresholds:
        threshold_velocity = peak_velocity_find * (threshold / 100)
        
        # Count patterns meeting this threshold
        count = sum(1 for _, _, velocities in jump_data for v in velocities if v >= threshold_velocity)
        
        # Find the longest pattern meeting this threshold
        longest_pattern = max((length for length, peak_velocity, _ in jump_data if peak_velocity >= threshold_velocity), default=0)
        
        # Store results in dictionary
        jump_counts[f"{threshold}%"] = {
            "count": count,
            "longest_pattern": longest_pattern,
            "threshold_velocity": threshold_velocity
        }
    
    # Step 3: Return the dictionary in the specified format
    return {
            "peak_velocity": peak_jump_velocity,                # Tuple of (value, associated length)
            "longest_jump_pattern": longest_jump_pattern,       # Tuple of (length, associated peak velocity)
            "jump_counts": jump_counts                          # Counts and longest patterns per threshold
        }

def get_streams_stats(stream_streaks):
    if len(stream_streaks[0]) == 5:
        stream_streaks = [(length, peak_velocity, velocities)
        for (start_time, length, peak_velocity, velocities, accel) in stream_streaks]
    # Define thresholds for lengths
    length_thresholds = {
        "Triples": 3,
        "Quints": 5,
        "2, 4, 6 Note": [2, 4, 6],
        "7-14 Note Bursts": (7, 14),
        "15-28 Note Streams": (15, 28),
        "29+ Note Streams": (29,)
    }

    # Initialize variables
    peak_flow_find = max(stream_streaks, key=lambda x: x[1], default=(0, 0))[1]  
    longest_stream_pattern_find = max(stream_streaks, key=lambda x: x[0], default=(0, 0))[0]  
    associate_velocity = max(x[0] for x in stream_streaks if x[1] == peak_flow_find)
    associate_length = max(x[1] for x in stream_streaks if x[0] == longest_stream_pattern_find)

    peak_stream_velocity = (peak_flow_find, associate_velocity)
    longest_stream_pattern = (longest_stream_pattern_find, associate_length)


    note_counts = {key: {'count': 0, 'max_velocity': 0} for key in length_thresholds.keys()}

    # Count lengths for each defined threshold and keep track of associated velocities
    for length, max_velocity, _ in stream_streaks:
        if length == length_thresholds["Triples"]:
            note_counts["Triples"]['count'] += 1
            note_counts["Triples"]['max_velocity'] = max(note_counts["Triples"]['max_velocity'], max_velocity)

        if length == length_thresholds["Quints"]:
            note_counts["Quints"]['count'] += 1
            note_counts["Quints"]['max_velocity'] = max(note_counts["Quints"]['max_velocity'], max_velocity)

        if length in length_thresholds["2, 4, 6 Note"]:
            note_counts["2, 4, 6 Note"]['count'] += 1
            note_counts["2, 4, 6 Note"]['max_velocity'] = max(note_counts["2, 4, 6 Note"]['max_velocity'], max_velocity)

        if length_thresholds["7-14 Note Bursts"][0] <= length <= length_thresholds["7-14 Note Bursts"][1]:
            note_counts["7-14 Note Bursts"]['count'] += 1
            note_counts["7-14 Note Bursts"]['max_velocity'] = max(note_counts["7-14 Note Bursts"]['max_velocity'], max_velocity)

        if length_thresholds["15-28 Note Streams"][0] <= length <= length_thresholds["15-28 Note Streams"][1]:
            note_counts["15-28 Note Streams"]['count'] += 1
            note_counts["15-28 Note Streams"]['max_velocity'] = max(note_counts["15-28 Note Streams"]['max_velocity'], max_velocity)

        if length >= length_thresholds["29+ Note Streams"][0]:
            note_counts["29+ Note Streams"]['count'] += 1
            note_counts["29+ Note Streams"]['max_velocity'] = max(note_counts["29+ Note Streams"]['max_velocity'], max_velocity)

    # Construct the output dictionary for stream stats
    return {
        'peak_stream_velocity': peak_stream_velocity,
        'longest_stream_pattern': longest_stream_pattern,
        'note_counts': {
            key: {
                'count': count_data['count'],
                'max_velocity': count_data['max_velocity']
            } for key, count_data in note_counts.items()
        }
    }

#did a schizo build for flow aim where 2 consecutive velocities need to reach a threshold for it to count
def calculate_flowaim(stream_streaks):
    if not stream_streaks:
        return {}
    if len(stream_streaks[0]) == 5:
        stream_streaks = [(length, peak_velocity, velocities)
        for (start_time, length, peak_velocity, velocities, accel) in stream_streaks]
    # Initialize a dictionary to store counts for each threshold
    threshold_counts = {}
    
    # Flatten the list of velocities to find the maximum velocity across all streams
    all_velocities = [velocity for _, _, velocities in stream_streaks for velocity in velocities]
    max_velocity = max(all_velocities) if all_velocities else 0
    max_length = 0
    # Define thresholds based on max velocity
    thresholds = [50,70,90]
    
    for threshold in thresholds:
        count = 0  # Reset count for this threshold
        threshold_vel = threshold * max_velocity / 100
        for _, _, velocities in stream_streaks:
            consecutive_count = 0  # Track consecutive velocities meeting the threshold
            
            for v in velocities:
                if v >= threshold_vel:
                    consecutive_count += 1  # Increase count for valid velocity
                    if consecutive_count == 2:  # If we have 2 consecutive valid velocities
                        count += 1  # Increase overall count for this threshold
                        consecutive_count = 0  # Reset after counting
                else:
                    consecutive_count = 0  # Reset if threshold not met

        threshold_counts[f"{threshold}%"] = {
            'count': count,
            'threshold_vel': threshold_vel
        }

    return {
            'threshold_counts': threshold_counts
            }


def get_rhythm_stats(rhythmdata):
    highest_sum = 0
    highest_sum_list = []
    for sublist in rhythmdata:
        current_sum = sum(sublist[1])  # Calculate the sum of the current sublist
        if current_sum > highest_sum:
            highest_sum = current_sum
            highest_sum_list = sublist 
    return highest_sum, highest_sum_list

#i dont remember the difference between this and the others
def calculate_flowaim_plus(stream_streaks):
    if not stream_streaks:
        return {}
    if len(stream_streaks[0]) == 5:
        stream_streaks = [(length, peak_velocity, velocities)
        for (start_time, length, peak_velocity, velocities, accel) in stream_streaks]
    # Initialize a dictionary to store counts for each threshold
    threshold_counts = {}
    # Flatten the list of velocities to find the maximum velocity across all streams
    all_velocities = [velocity for _, _, velocities in stream_streaks for velocity in velocities]
    max_velocity = max(all_velocities) if all_velocities else 0
    # Define thresholds based on max velocity
    thresholds = [50,70,90]
    
    for threshold in thresholds:
        count = 0  # Reset count for this threshold
        threshold_vel = threshold * max_velocity / 100
        max_length = 0
        for _, _, velocities in stream_streaks:
            consecutive_count = 0  # Track consecutive velocities meeting the threshold
            for v in velocities:
                if v >= threshold_vel:
                    consecutive_count += 1  # Increase count for valid velocity
                    if consecutive_count == 2:  # If we have 2 consecutive valid velocities
                        count += 1  # Increase overall count for this threshold
                        consecutive_count = 0  # Reset after counting
                        if length > max_length:
                            max_length = length
                else:
                    consecutive_count = 0  # Reset if threshold not met

        threshold_counts[f"{threshold}%"] = {
            'count': count,
            'threshold_vel': threshold_vel,
            'max_thresh_length': max_length
        }

    return {
            'threshold_counts': threshold_counts
            }

def get_rhythm_stats(rhythmdata):
    highest_sum = 0
    highest_sum_list = []
    for sublist in rhythmdata:
        current_sum = sum(sublist[1])  # Calculate the sum of the current sublist
        if current_sum > highest_sum:
            highest_sum = current_sum
            highest_sum_list = sublist 
    return highest_sum, highest_sum_list

