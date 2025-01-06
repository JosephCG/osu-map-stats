import tkinter as tk
from tkinter import filedialog
import math
import os
import re
import json
import sys

def update_velocity_stats(jump_stats, stream_stats, flow_stats, rhythm_stats, multiplier):
    if jump_stats:
        peak_velocity, peak_length = jump_stats['peak_velocity']
        jump_stats['peak_velocity'] = (round(peak_velocity * multiplier,2), peak_length)
        print(jump_stats['peak_velocity'])
    # Update the longest jump pattern: multiply the velocity by the multiplier
        longest_jump_length, longest_jump_velocity = jump_stats['longest_jump_pattern']
        jump_stats['longest_jump_pattern'] = (longest_jump_length, round(longest_jump_velocity * multiplier,2))
    
    # Update jump counts for each threshold
        for threshold, count_data in jump_stats['jump_counts'].items():
            count_data['threshold_velocity'] = round(count_data['threshold_velocity'] * multiplier, 2)
    if stream_stats:
        peak_stream_velocity, peak_stream_length = stream_stats['peak_stream_velocity']
        longest_stream_pattern_length, longest_stream_pattern_velocity = stream_stats['longest_stream_pattern']
    
    # Apply multiplier to peak stream velocity and longest stream pattern velocity
        stream_stats['peak_stream_velocity'] = (round(peak_stream_velocity * multiplier,2), peak_stream_length)
        stream_stats['longest_stream_pattern'] = (longest_stream_pattern_length, round(longest_stream_pattern_velocity * multiplier,2))


    # Update note counts with multiplier (only modifying max_velocity)
        for key, count_data in stream_stats['note_counts'].items():
            count_data['max_velocity'] =  round(multiplier *count_data['max_velocity'],2) # Apply multiplier to max velocities

    #Update flow velocity thresholds
        for theshold, count_data in flow_stats['threshold_counts'].items():
            count_data['threshold_vel'] = round(multiplier  * count_data['threshold_vel'],2)


    return jump_stats, stream_stats, flow_stats, rhythm_stats

def print_stats(nomod_stats,bpm, jump_stats, stream_stats, rhythm_stats):
    jump_stats, stream_stats, flow_stats, rhythm_stats = nomod_stats  # Unpack the tuple

    print(f"BPM: {bpm}")
    if jump_stats:
        print(f"Peak Velocity: {jump_stats['peak_velocity']}")
        print(f"Longest Jump Pattern: {jump_stats['longest_jump_pattern']}")
        for threshold, data in jump_stats['jump_counts'].items():
            count = data['count']
            longest_with_threshold = data['longest_pattern']
            threshold_velocity = data['threshold_velocity']
            print(f"  {threshold} of Peak Velocity count ({threshold_velocity}): {count} ({longest_with_threshold})")
    if stream_stats: 
        print("Stream Stats:")
        print(f"Peak Stream Velocity: {stream_stats['peak_stream_velocity']}")
        print(f"Longest Stream Pattern: {stream_stats['longest_stream_pattern']}")
        print("Note Counts:")
        for length, data in stream_stats['note_counts'].items():
            if data['count'] > 0:
                print(f"  {length}: {data['count']} ({data['max_velocity']})")

    # Print Flow Aim Stats
        print("Flow Aim Stats:")
        for threshold, data in flow_stats['threshold_counts'].items():
            print(f"  {threshold} of Max Velocity Count ({data['threshold_vel']}): {data['count']}")
    if rhythm_stats:
        print(f"Longest Rhythm Pattern: {rhythm_stats[0]} , {rhythm_stats[1]}")

