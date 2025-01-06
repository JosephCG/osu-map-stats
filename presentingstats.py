import tkinter as tk
from tkinter import filedialog
import math
import os
import osu
import re
import json
import sys
from oauth2client.service_account import ServiceAccountCredentials

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

def get_googlelist(nomod_stats, title,bpm):
    row = [
    " ",  # A: Slot (leave blank or assign based on the slot)
    f"{title}",  # B: Title (retrieve from osu file metadata)
    " ",  # C: Jump Stats Header (empty for now)
    f"{nomod_stats[0]['peak_velocity'][0]:.2f} / {nomod_stats[0]['peak_velocity'][1]}",  # D: Peak Jump Velocity (value / length)
    f"{nomod_stats[0]['longest_jump_pattern'][0]} / {nomod_stats[0]['longest_jump_pattern'][1]:.2f}",  # E: Longest Jump Pattern Length / Velocity
    
    # Jump Counts
    f"{nomod_stats[0]['jump_counts']['50%']['count']} / {nomod_stats[0]['jump_counts']['50%']['longest_pattern']} / {nomod_stats[0]['jump_counts']['50%']['threshold_velocity']:.2f}",  # F: 50% Jump Count / Longest Pattern / Threshold Velocity
    f"{nomod_stats[0]['jump_counts']['70%']['count']} / {nomod_stats[0]['jump_counts']['70%']['longest_pattern']} / {nomod_stats[0]['jump_counts']['70%']['threshold_velocity']:.2f}",  # G: 70% Jump Count / Longest Pattern / Threshold Velocity
    f"{nomod_stats[0]['jump_counts']['90%']['count']} / {nomod_stats[0]['jump_counts']['90%']['longest_pattern']} / {nomod_stats[0]['jump_counts']['90%']['threshold_velocity']:.2f}",  # H: 90% Jump Count / Longest Pattern / Threshold Velocity
    
    " ",  # I: Filler Box for Stream Stats
    
    # Stream Stats (Peak Stream Velocity / Longest Stream Pattern Length)
    f"{nomod_stats[1]['peak_stream_velocity'][0]:.2f} / {nomod_stats[1]['peak_stream_velocity'][1]}",  # J: Peak Stream Velocity / Length
    f"{nomod_stats[1]['longest_stream_pattern'][0]} / {nomod_stats[1]['longest_stream_pattern'][1]:.2f}",  # K: Longest Stream Pattern Length / Velocity
    
    # Stream Count Stats
    f"{nomod_stats[1]['note_counts']['Triples']['count']} / {nomod_stats[1]['note_counts']['Triples']['max_velocity']:.2f}",  # L: Triples Count / Max Velocity
    f"{nomod_stats[1]['note_counts']['Quints']['count']} / {nomod_stats[1]['note_counts']['Quints']['max_velocity']:.2f}",  # M: Quints Count / Max Velocity
    f"{nomod_stats[1]['note_counts']['2, 4, 6 Note']['count']} / {nomod_stats[1]['note_counts']['2, 4, 6 Note']['max_velocity']:.2f}",  # N: 2, 4, 6 Note Count / Max Velocity
    f"{nomod_stats[1]['note_counts']['7-14 Note Bursts']['count']} / {nomod_stats[1]['note_counts']['7-14 Note Bursts']['max_velocity']:.2f}",  # O: 7-14 Note Bursts Count / Max Velocity
    
    # Add the 15-28 and 29+ Note Bursts
    f"{nomod_stats[1]['note_counts']['15-28 Note Streams']['count']} / {nomod_stats[1]['note_counts']['15-28 Note Streams']['max_velocity']:.2f}",  # P: 15-28 Note Bursts Count / Max Velocity
    f"{nomod_stats[1]['note_counts']['29+ Note Streams']['count']} / {nomod_stats[1]['note_counts']['29+ Note Streams']['max_velocity']:.2f}",  # Q: 29+ Note Bursts Count / Max Velocity
    
    f"{nomod_stats[2]['threshold_counts']['50%']['count']} / {nomod_stats[2]['threshold_counts']['50%']['threshold_vel']:.2f}",  # R: 50% Flow Count / Threshold Velocity
    f"{nomod_stats[2]['threshold_counts']['70%']['count']} / {nomod_stats[2]['threshold_counts']['70%']['threshold_vel']:.2f}",  # S: 70% Flow Count / Threshold Velocity
    f"{nomod_stats[2]['threshold_counts']['90%']['count']} / {nomod_stats[2]['threshold_counts']['90%']['threshold_vel']:.2f}",  # T: 90% Flow Count / Threshold Velocity
    
    f"{nomod_stats[3]}",  # U: Longest Rhythm Pattern Length / Velocity
    f"{bpm}"
  # V: The Rhythm Pattern (sequence)
    ]
    return row

def find_highest_blank_row(worksheet):
    # Get all values in the worksheet
    values = worksheet.get_all_values()

    # Loop through rows from the bottom upwards to find the first empty row
    for i, row in enumerate(reversed(values)):
        if all(cell == "" for cell in row):
            return len(values) - i  # Return the index of the first blank row (1-indexed)

    return len(values) + 1 

def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\imjos\Downloads\owc-stats-ee972929036e.json', scope)
    client = gspread.authorize(creds)
    return client

def open_google_sheet(client, sheet_id, worksheet_name):
    sheet = client.open_by_key('1TfAAeUjOEl1Hv1vNCL_9gKgyZ_O-On0VKCJd6VOp8Mo')  # Use sheet ID to open the specific sheet
    worksheet = sheet.worksheet('try1')  # Open the specified worksheet by name
    return worksheet

def mods(input, cs):
    speedbonus = 1
    circles = cs
    #these are the difficulty changing mods in the game
    timemods = ["nc", "dt", "double time", "nightcore", "halftime", "ht"]
    time_mod_count = sum(mod in input for mod in timemods)
    diff_mods = ["ez", "easy", "hr", "hardrock"]
    diff_mod_count = sum(mod in input for mod in diff_mods)
    if "hardrock" in input or "hr" in input:
        circles = cs * 1.3
    if "ez" in input or "easy" in input:
        circles = cs * .5
    if "nc" in input or "nightcore" in input:
        speedbonus = 1.5
    if "dt" in input or "doubletime" in input:
        speedbonus = 1.5
    if "ht" in input or "halftime" in input:
        speedbonus = .75
    if diff_mod_count >1 or time_mod_count >1:
        circles = cs
        speedbonus = 1
    return circles , speedbonus



def key_stats(jdata,sdata,rdata, fdata, adata, sheet, rownumber):
    
    sheet.update_cell(rownumber, 2, jdata["peak_jump"]["peak_velocity"])
    sheet.update_cell(rownumber+1,2,jdata["peak_jump"]["jump_length"])
    sheet.update_cell(rownumber, 3, jdata["longest_jump_pattern"]["peak_length"])
    sheet.update_cell(rownumber+1,3,jdata["longest_jump_pattern"]["velocity_stats"]["max"])
    sheet.update_cell(rownumber, 4, jdata["jump_counts"]["0-1"]["jump_count"])
    sheet.update_cell(rownumber + 1, 4, jdata["jump_counts"]["0-1"]["pattern_count"])
    sheet.update_cell(rownumber, 5, jdata["jump_counts"]["1-1.5"]["jump_count"])
    sheet.update_cell(rownumber + 1, 5, jdata["jump_counts"]["1-1.5"]["pattern_count"])
    sheet.update_cell(rownumber, 6, jdata["jump_counts"]["1.5-2"]["jump_count"])
    sheet.update_cell(rownumber + 1, 6, jdata["jump_counts"]["1.5-2"]["pattern_count"])
    sheet.update_cell(rownumber, 7, jdata["jump_counts"]["2-2.5"]["jump_count"])
    sheet.update_cell(rownumber + 1, 7, jdata["jump_counts"]["2-2.5"]["pattern_count"])
    sheet.update_cell(rownumber, 8, jdata["jump_counts"]["2.5-3"]["jump_count"])
    sheet.update_cell(rownumber + 1, 8, jdata["jump_counts"]["2.5-3"]["pattern_count"])
    sheet.update_cell(rownumber, 9, jdata["jump_counts"]["3-3.5"]["jump_count"])
    sheet.update_cell(rownumber + 1, 9, jdata["jump_counts"]["3-3.5"]["pattern_count"])
    sheet.update_cell(rownumber, 10, jdata["jump_counts"]["3.5-4"]["jump_count"])
    sheet.update_cell(rownumber + 1, 10, jdata["jump_counts"]["3.5-4"]["pattern_count"])
    sheet.update_cell(rownumber, 11, jdata["jump_counts"]["4-4.5"]["jump_count"])
    sheet.update_cell(rownumber + 1, 11, jdata["jump_counts"]["4-4.5"]["pattern_count"])
    sheet.update_cell(rownumber, 12, jdata["jump_counts"]["4.5-+"]["jump_count"])
    sheet.update_cell(rownumber + 1, 12, jdata["jump_counts"]["4.5-+"]["pattern_count"])
    sheet.update_cell(rownumber, 14, sdata["peak_flow"]["peak_flow"])  # 13 -> 14
    sheet.update_cell(rownumber + 1, 14, sdata["peak_flow"]["stream_length"])  # 13 -> 14
    sheet.update_cell(rownumber, 15, sdata["longest_stream"]["longest_stream"])  # 14 -> 15
    sheet.update_cell(rownumber + 1, 15, sdata["longest_stream"]["velocity_peak"])  # 14 -> 15
    sheet.update_cell(rownumber, 16, sdata["stream_stats"]["Triples"]["count"])  # 15 -> 16
    sheet.update_cell(rownumber + 1, 16, sdata["stream_stats"]["Triples"]["max_velocity"])  # 15 -> 16
    sheet.update_cell(rownumber, 17, sdata["stream_stats"]["Quints"]["count"])  # 16 -> 17
    sheet.update_cell(rownumber + 1, 17, sdata["stream_stats"]["Quints"]["max_velocity"])  # 16 -> 17
    sheet.update_cell(rownumber, 18, sdata["stream_stats"]["2, 4, 6 Note"]["count"])  # 17 -> 18
    sheet.update_cell(rownumber + 1, 18, sdata["stream_stats"]["2, 4, 6 Note"]["max_velocity"])  # 17 -> 18
    sheet.update_cell(rownumber, 19, sdata["stream_stats"]["7-14 Note Bursts"]["count"])  # 18 -> 19
    sheet.update_cell(rownumber + 1, 19, sdata["stream_stats"]["7-14 Note Bursts"]["max_velocity"])  # 18 -> 19
    sheet.update_cell(rownumber, 20, sdata["stream_stats"]["15-28 Note Streams"]["count"])  # 19 -> 20
    sheet.update_cell(rownumber + 1, 20, sdata["stream_stats"]["15-28 Note Streams"]["max_velocity"])  # 19 -> 20
    sheet.update_cell(rownumber, 21, sdata["stream_stats"]["29+ Note Streams"]["count"])  # 20 -> 21
    sheet.update_cell(rownumber + 1, 21, sdata["stream_stats"]["29+ Note Streams"]["max_velocity"])  # 20 -> 21
    sheet.update_cell(rownumber, 22, str(rdata["longest_rhythm_pattern"]["pattern"]))  # 21 -> 22
    sheet.update_cell(rownumber + 1, 22, rdata["longest_rhythm_pattern"]["pattern length"])  # 21 -> 22

    sheet2.update_cell(rownumber2, 3, jdata["peak_jump"]["peak_velocity"])
    sheet2.update_cell(rownumber2+1,3,jdata["peak_jump"]["jump_length"])
    sheet2.update_cell(rownumber2+2,3,jdata["peak_jump"]["velocity_stats"]["min"])
    sheet2.update_cell(rownumber2+2,4,jdata["peak_jump"]["velocity_stats"]["median"])
    sheet2.update_cell(rownumber2+2,5,jdata["peak_jump"]["velocity_stats"]["max"])
    sheet2.update_cell(rownumber2+3, 3, jdata["peak_jump"]["angle_stats"]["min"])
    sheet2.update_cell(rownumber2+3, 4, jdata["peak_jump"]["angle_stats"]["median"])
    sheet2.update_cell(rownumber2+3, 5, jdata["peak_jump"]["angle_stats"]["max"])
    sheet.update_cell(rownumber2, 6, jdata["longest_jump_pattern"]["peak_length"])
    sheet.update_cell(rownumber2+1,6,jdata["longest_jump_pattern"]["velocity_stats"]["max"])
    sheet.update_cell(rownumber, 4, jdata["jump_counts"]["0-1"]["jump_count"])
    sheet.update_cell(rownumber + 1, 4, jdata["jump_counts"]["0-1"]["pattern_count"])
    sheet.update_cell(rownumber, 5, jdata["jump_counts"]["1-1.5"]["jump_count"])
    sheet.update_cell(rownumber + 1, 5, jdata["jump_counts"]["1-1.5"]["pattern_count"])
    sheet.update_cell(rownumber, 6, jdata["jump_counts"]["1.5-2"]["jump_count"])
    sheet.update_cell(rownumber + 1, 6, jdata["jump_counts"]["1.5-2"]["pattern_count"])
    sheet.update_cell(rownumber, 7, jdata["jump_counts"]["2-2.5"]["jump_count"])
    sheet.update_cell(rownumber + 1, 7, jdata["jump_counts"]["2-2.5"]["pattern_count"])
    sheet.update_cell(rownumber, 8, jdata["jump_counts"]["2.5-3"]["jump_count"])
    sheet.update_cell(rownumber + 1, 8, jdata["jump_counts"]["2.5-3"]["pattern_count"])
    sheet.update_cell(rownumber, 9, jdata["jump_counts"]["3-3.5"]["jump_count"])
    sheet.update_cell(rownumber + 1, 9, jdata["jump_counts"]["3-3.5"]["pattern_count"])
    sheet.update_cell(rownumber, 10, jdata["jump_counts"]["3.5-4"]["jump_count"])
    sheet.update_cell(rownumber + 1, 10, jdata["jump_counts"]["3.5-4"]["pattern_count"])
    sheet.update_cell(rownumber, 11, jdata["jump_counts"]["4-4.5"]["jump_count"])
    sheet.update_cell(rownumber + 1, 11, jdata["jump_counts"]["4-4.5"]["pattern_count"])
    sheet.update_cell(rownumber, 12, jdata["jump_counts"]["4.5-+"]["jump_count"])
    sheet.update_cell(rownumber + 1, 12, jdata["jump_counts"]["4.5-+"]["pattern_count"])
    sheet.update_cell(rownumber, 14, sdata["peak_flow"]["peak_flow"])  # 13 -> 14
    sheet.update_cell(rownumber + 1, 14, sdata["peak_flow"]["stream_length"])  # 13 -> 14
    sheet.update_cell(rownumber, 15, sdata["longest_stream"]["longest_stream"])  # 14 -> 15
    sheet.update_cell(rownumber + 1, 15, sdata["longest_stream"]["velocity_peak"])  # 14 -> 15
    sheet.update_cell(rownumber, 16, sdata["stream_stats"]["Triples"]["count"])  # 15 -> 16
    sheet.update_cell(rownumber + 1, 16, sdata["stream_stats"]["Triples"]["max_velocity"])  # 15 -> 16
    sheet.update_cell(rownumber, 17, sdata["stream_stats"]["Quints"]["count"])  # 16 -> 17
    sheet.update_cell(rownumber + 1, 17, sdata["stream_stats"]["Quints"]["max_velocity"])  # 16 -> 17
    sheet.update_cell(rownumber, 18, sdata["stream_stats"]["2, 4, 6 Note"]["count"])  # 17 -> 18
    sheet.update_cell(rownumber + 1, 18, sdata["stream_stats"]["2, 4, 6 Note"]["max_velocity"])  # 17 -> 18
    sheet.update_cell(rownumber, 19, sdata["stream_stats"]["7-14 Note Bursts"]["count"])  # 18 -> 19
    sheet.update_cell(rownumber + 1, 19, sdata["stream_stats"]["7-14 Note Bursts"]["max_velocity"])  # 18 -> 19
    sheet.update_cell(rownumber, 20, sdata["stream_stats"]["15-28 Note Streams"]["count"])  # 19 -> 20
    sheet.update_cell(rownumber + 1, 20, sdata["stream_stats"]["15-28 Note Streams"]["max_velocity"])  # 19 -> 20
    sheet.update_cell(rownumber, 21, sdata["stream_stats"]["29+ Note Streams"]["count"])  # 20 -> 21
    sheet.update_cell(rownumber + 1, 21, sdata["stream_stats"]["29+ Note Streams"]["max_velocity"])  # 20 -> 21
    sheet.update_cell(rownumber, 22, str(rdata["longest_rhythm_pattern"]["pattern"]))  # 21 -> 22
    sheet.update_cell(rownumber + 1, 22, rdata["longest_rhythm_pattern"]["pattern length"])



def find_highest_empty_row(worksheet):
    # Get all the values from the sheet
    try:
        data = worksheet.get_all_values()
    except Exception as e:
        print(f"Error fetching data from sheet2: {e}")
    # Iterate over the rows, checking columns B to W (index 1 to 22)
    for i, row in enumerate(data, start=1):
        if not any(row[1:23]):  # Columns B (index 1) to W (index 22)
            return i  # Return the first empty row
    
    return None  # If no empty row 
def try_stats(jdata, sdata, fdata,rdata,adata, rownumber, sheet, title, artist, bpm):
    
    mappings = [
        (0, 1, lambda _:  artist),
        (1, 1, lambda _:  title),
        (2, 1, lambda _:  str(bpm)),
        (0, 2, lambda data: data["peak_jump"]["peak_velocity"]),
        (1, 2, lambda data: data["peak_jump"]["jump_length"]),
        (2, 2, lambda data: data["peak_jump"]["velocity_stats"]["min"]),
        (2, 3, lambda data: data["peak_jump"]["velocity_stats"]["median"]),
        (2, 4, lambda data: data["peak_jump"]["velocity_stats"]["max"]),
        (3, 2, lambda data: data["peak_jump"]["angle_stats"]["min"]),
        (3, 3, lambda data: data["peak_jump"]["angle_stats"]["median"]),
        (3, 4, lambda data: data["peak_jump"]["angle_stats"]["max"]),
        (0, 5, lambda data: data["longest_jump_pattern"]["peak_length"]),
        (1, 5, lambda data: data["longest_jump_pattern"]["peak_count"]),
        (2, 5, lambda data: data["longest_jump_pattern"]["velocity_stats"]["min"]),
        (2,6,lambda data: data["longest_jump_pattern"]["velocity_stats"]["median"]),
        (2,7,lambda data: data["longest_jump_pattern"]["velocity_stats"]["max"]),
        (3,5,lambda data: data["longest_jump_pattern"]["angle_stats"]["min"]),
        (3,6,lambda data: data["longest_jump_pattern"]["angle_stats"]["median"]),
        (3,7,lambda data: data["longest_jump_pattern"]["angle_stats"]["max"]),
        (0,8,lambda data: data["jump_counts"]["0-1"]["length_stats"]["max"]),
        (1,8,lambda data: data["jump_counts"]["0-1"]["jump_count"]),
        (1,10,lambda data: data["jump_counts"]["0-1"]["pattern_count"]),
        (2,8,lambda data: data["jump_counts"]["0-1"]["length_stats"]["min"]),
        (2,9,lambda data: data["jump_counts"]["0-1"]["length_stats"]["median"]),
        (2,10,lambda data: data["jump_counts"]["0-1"]["length_stats"]["max"]),
        (3,8,lambda data: data["jump_counts"]["0-1"]["angle_stats"]["min"]),
        (3,9,lambda data: data["jump_counts"]["0-1"]["angle_stats"]["median"]),
        (3,10,lambda data: data["jump_counts"]["0-1"]["angle_stats"]["max"]),
        (0,11,lambda data: data["jump_counts"]["1-1.5"]["length_stats"]["max"]),
        (1,11,lambda data: data["jump_counts"]["1-1.5"]["jump_count"]),
        (1,13,lambda data: data["jump_counts"]["1-1.5"]["pattern_count"]),
        (2,11,lambda data: data["jump_counts"]["1-1.5"]["length_stats"]["min"]),
        (2,12,lambda data: data["jump_counts"]["1-1.5"]["length_stats"]["median"]),
        (2,13,lambda data: data["jump_counts"]["1-1.5"]["length_stats"]["max"]),
        (3,11,lambda data: data["jump_counts"]["1-1.5"]["angle_stats"]["min"]),
        (3,12,lambda data: data["jump_counts"]["1-1.5"]["angle_stats"]["median"]),
        (3,13,lambda data: data["jump_counts"]["1-1.5"]["angle_stats"]["max"]),

        (0,14,lambda data: data["jump_counts"]["1.5-2"]["length_stats"]["max"]),
        (1,14,lambda data: data["jump_counts"]["1.5-2"]["jump_count"]),
        (1,16,lambda data: data["jump_counts"]["1.5-2"]["pattern_count"]),
        (2,14,lambda data: data["jump_counts"]["1.5-2"]["length_stats"]["min"]),
        (2,15,lambda data: data["jump_counts"]["1.5-2"]["length_stats"]["median"]),
        (2,16,lambda data: data["jump_counts"]["1.5-2"]["length_stats"]["max"]),
        (3,14,lambda data: data["jump_counts"]["1.5-2"]["angle_stats"]["min"]),
        (3,15,lambda data: data["jump_counts"]["1.5-2"]["angle_stats"]["median"]),
        (3,16,lambda data: data["jump_counts"]["1.5-2"]["angle_stats"]["max"]),

        (0,17,lambda data: data["jump_counts"]["2-2.5"]["length_stats"]["max"]),
        (1,17,lambda data: data["jump_counts"]["2-2.5"]["jump_count"]),
        (1,19,lambda data: data["jump_counts"]["2-2.5"]["pattern_count"]),
        (2,17,lambda data: data["jump_counts"]["2-2.5"]["length_stats"]["min"]),
        (2,18,lambda data: data["jump_counts"]["2-2.5"]["length_stats"]["median"]),
        (2,19,lambda data: data["jump_counts"]["2-2.5"]["length_stats"]["max"]),
        (3,17,lambda data: data["jump_counts"]["2-2.5"]["angle_stats"]["min"]),
        (3,18,lambda data: data["jump_counts"]["2-2.5"]["angle_stats"]["median"]),
        (3,19,lambda data: data["jump_counts"]["2-2.5"]["angle_stats"]["max"]),

        (0,20,lambda data: data["jump_counts"]["2.5-3"]["length_stats"]["max"]),
        (1,20,lambda data: data["jump_counts"]["2.5-3"]["jump_count"]),
        (1,22,lambda data: data["jump_counts"]["2.5-3"]["pattern_count"]),
        (2,20,lambda data: data["jump_counts"]["2.5-3"]["length_stats"]["min"]),
        (2,21,lambda data: data["jump_counts"]["2.5-3"]["length_stats"]["median"]),
        (2,22,lambda data: data["jump_counts"]["2.5-3"]["length_stats"]["max"]),
        (3,20,lambda data: data["jump_counts"]["2.5-3"]["angle_stats"]["min"]),
        (3,21,lambda data: data["jump_counts"]["2.5-3"]["angle_stats"]["median"]),
        (3,22,lambda data: data["jump_counts"]["2.5-3"]["angle_stats"]["max"]),

        (0,23,lambda data: data["jump_counts"]["3-3.5"]["length_stats"]["max"]),
        (1,23,lambda data: data["jump_counts"]["3-3.5"]["jump_count"]),
        (1,25,lambda data: data["jump_counts"]["3-3.5"]["pattern_count"]),
        (2,23,lambda data: data["jump_counts"]["3-3.5"]["length_stats"]["min"]),
        (2,24,lambda data: data["jump_counts"]["3-3.5"]["length_stats"]["median"]),
        (2,25,lambda data: data["jump_counts"]["3-3.5"]["length_stats"]["max"]),
        (3,23,lambda data: data["jump_counts"]["3-3.5"]["angle_stats"]["min"]),
        (3,24,lambda data: data["jump_counts"]["3-3.5"]["angle_stats"]["median"]),
        (3,25,lambda data: data["jump_counts"]["3-3.5"]["angle_stats"]["max"]),

        (0,26,lambda data: data["jump_counts"]["3.5-4"]["length_stats"]["max"]),
        (1,26,lambda data: data["jump_counts"]["3.5-4"]["jump_count"]),
        (1,28,lambda data: data["jump_counts"]["3.5-4"]["pattern_count"]),
        (2,26,lambda data: data["jump_counts"]["3.5-4"]["length_stats"]["min"]),
        (2,27,lambda data: data["jump_counts"]["3.5-4"]["length_stats"]["median"]),
        (2,28,lambda data: data["jump_counts"]["3.5-4"]["length_stats"]["max"]),
        (3,26,lambda data: data["jump_counts"]["3.5-4"]["angle_stats"]["min"]),
        (3,27,lambda data: data["jump_counts"]["3.5-4"]["angle_stats"]["median"]),
        (3,28,lambda data: data["jump_counts"]["3.5-4"]["angle_stats"]["max"]),

        (0,29,lambda data: data["jump_counts"]["4-4.5"]["length_stats"]["max"]),
        (1,29,lambda data: data["jump_counts"]["4-4.5"]["jump_count"]),
        (1,31,lambda data: data["jump_counts"]["4-4.5"]["pattern_count"]),
        (2,29,lambda data: data["jump_counts"]["4-4.5"]["length_stats"]["min"]),
        (2,30,lambda data: data["jump_counts"]["4-4.5"]["length_stats"]["median"]),
        (2,31,lambda data: data["jump_counts"]["4-4.5"]["length_stats"]["max"]),
        (3,29,lambda data: data["jump_counts"]["4-4.5"]["angle_stats"]["min"]),
        (3,30,lambda data: data["jump_counts"]["4-4.5"]["angle_stats"]["median"]),
        (3,31,lambda data: data["jump_counts"]["4-4.5"]["angle_stats"]["max"]),
        (0,32,lambda data: data["jump_counts"]["4.5-+"]["length_stats"]["max"]),
        (1,32,lambda data: data["jump_counts"]["4.5-+"]["jump_count"]),
        (1,34,lambda data: data["jump_counts"]["4.5-+"]["pattern_count"]),
        (2,32,lambda data: data["jump_counts"]["4.5-+"]["length_stats"]["min"]),
        (2,33,lambda data: data["jump_counts"]["4.5-+"]["length_stats"]["median"]),
        (2,34,lambda data: data["jump_counts"]["4.5-+"]["length_stats"]["max"]),
        (3,32,lambda data: data["jump_counts"]["4.5-+"]["angle_stats"]["min"]),
        (3,33,lambda data: data["jump_counts"]["4.5-+"]["angle_stats"]["median"]),
        (3,34,lambda data: data["jump_counts"]["4.5-+"]["angle_stats"]["max"]),
        (0,36,lambda data: data["peak_flow"]["peak_flow"]),
        (1,36,lambda data: data["peak_flow"]["stream_length"]),
        (2,36,lambda data: data["peak_flow"]["velocity_stats"]["min"]),
        (2,37,lambda data: data["peak_flow"]["velocity_stats"]["median"]),
        (2,38,lambda data: data["peak_flow"]["velocity_stats"]["max"]),
        (3, 36,lambda _:  fdata["flow_counts"]["50%"]["count"]),
        (3, 37,lambda _:  fdata["flow_counts"]["70%"]["count"]),
        (3, 38,lambda _:  fdata["flow_counts"]["90%"]["count"]),
        (0,39,lambda data: data["longest_stream"]["longest_stream"]),
        (1,39,lambda data: data["longest_stream"]["velocity_peak"]),
        (1,41,lambda data: data["longest_stream"]["max_stream_count"]),
        (2,39,lambda data: data["longest_stream"]["velocity_stats"]["min"]),
        (2,40,lambda data: data["longest_stream"]["velocity_stats"]["median"]),
        (2,41,lambda data: data["longest_stream"]["velocity_stats"]["max"]),
        (0,42,lambda data: data["stream_stats"]["Triples"]["count"]),
        (0,44,lambda data: data["stream_stats"]["Triples"]["max_velocity"]),
        (1,42,lambda data: data["stream_stats"]["Triples"]["min_velocity"]),
        (1,43,lambda data: data["stream_stats"]["Triples"]["median_velocity"]),
        (1,44,lambda data: data["stream_stats"]["Triples"]["max_velocity"]),
        (2,42,lambda data: data["stream_stats"]["Triples"]["50% Max Velocity"]),
        (2,43,lambda data: data["stream_stats"]["Triples"]["70% Max Velocity"]),
        (2,44,lambda data: data["stream_stats"]["Triples"]["90% Max Velocity"]),
        (0,45,lambda data: data["stream_stats"]["Quints"]["count"]),
        (0,47,lambda data: data["stream_stats"]["Quints"]["max_velocity"]),
        (1,45,lambda data: data["stream_stats"]["Quints"]["min_velocity"]),
        (1,46,lambda data: data["stream_stats"]["Quints"]["median_velocity"]),
        (1,47,lambda data: data["stream_stats"]["Quints"]["max_velocity"]),
        (2,45,lambda data: data["stream_stats"]["Quints"]["50% Max Velocity"]),
        (2,46,lambda data: data["stream_stats"]["Quints"]["70% Max Velocity"]),
        (2,47,lambda data: data["stream_stats"]["Quints"]["90% Max Velocity"]),
        (0,48,lambda data: data["stream_stats"]["2, 4, 6 Note"]["count"]),
        (0,50,lambda data: data["stream_stats"]["2, 4, 6 Note"]["max_velocity"]),
        (1,48,lambda data: data["stream_stats"]["2, 4, 6 Note"]["Doubles"]),
        (1,49,lambda data: data["stream_stats"]["2, 4, 6 Note"]["Quads"]),
        (1,50,lambda data: data["stream_stats"]["2, 4, 6 Note"]["Six Notes"]),
        (2,48,lambda data: data["stream_stats"]["2, 4, 6 Note"]["min_velocity"]),
        (2,49,lambda data: data["stream_stats"]["2, 4, 6 Note"]["median_velocity"]),
        (2,50,lambda data: data["stream_stats"]["2, 4, 6 Note"]["max_velocity"]),
        (3,48,lambda data: data["stream_stats"]["2, 4, 6 Note"]["50% Max Velocity"]),
        (3,49,lambda data: data["stream_stats"]["2, 4, 6 Note"]["70% Max Velocity"]),
        (3,50,lambda data: data["stream_stats"]["2, 4, 6 Note"]["90% Max Velocity"]),
        (0,51,lambda data: data["stream_stats"]["7-14 Note Bursts"]["count"]),
        (0,53,lambda data: data["stream_stats"]["7-14 Note Bursts"]["max_velocity"]),
        (1,51,lambda data: data["stream_stats"]["7-14 Note Bursts"]["<10 Notes"]),
        (1,52,lambda data: data["stream_stats"]["7-14 Note Bursts"]["10-11 Notes"]),
        (1,53,lambda data: data["stream_stats"]["7-14 Note Bursts"][">=12 Notes"]),
        (2,51,lambda data: data["stream_stats"]["7-14 Note Bursts"]["min_velocity"]),
        (2,52,lambda data: data["stream_stats"]["7-14 Note Bursts"]["median_velocity"]),
        (2,53,lambda data: data["stream_stats"]["7-14 Note Bursts"]["max_velocity"]),
        (3,51,lambda data: data["stream_stats"]["7-14 Note Bursts"]["50% Max Velocity"]),
        (3,52,lambda data: data["stream_stats"]["7-14 Note Bursts"]["70% Max Velocity"]),
        (3,53,lambda data: data["stream_stats"]["7-14 Note Bursts"]["90% Max Velocity"]),
        (0,54,lambda data: data["stream_stats"]["15-28 Note Streams"]["count"]),
        (0,56,lambda data: data["stream_stats"]["15-28 Note Streams"]["max_velocity"]),
        (1,54,lambda data: data["stream_stats"]["15-28 Note Streams"]["<20 Notes"]),
        (1,55,lambda data: data["stream_stats"]["15-28 Note Streams"]["20-24 Notes"]),
        (1,56,lambda data: data["stream_stats"]["15-28 Note Streams"][">24 Notes"]),
        (2,54,lambda data: data["stream_stats"]["15-28 Note Streams"]["min_velocity"]),
        (2,55,lambda data: data["stream_stats"]["15-28 Note Streams"]["median_velocity"]),
        (2,56,lambda data: data["stream_stats"]["15-28 Note Streams"]["max_velocity"]),
        (3,54,lambda data: data["stream_stats"]["15-28 Note Streams"]["50% Max Velocity"]),
        (3,55,lambda data: data["stream_stats"]["15-28 Note Streams"]["70% Max Velocity"]),
        (3,56,lambda data: data["stream_stats"]["15-28 Note Streams"]["90% Max Velocity"]),
        (0,57,lambda data: data["stream_stats"]["29+ Note Streams"]["count"]),
        (0,59,lambda data: data["stream_stats"]["29+ Note Streams"]["max_velocity"]),
        (1,57,lambda data: data["stream_stats"]["29+ Note Streams"]["min_velocity"]),
        (1,58,lambda data: data["stream_stats"]["29+ Note Streams"]["median_velocity"]),
        (1,59,lambda data: data["stream_stats"]["29+ Note Streams"]["max_velocity"]),
        (2,57,lambda data: data["stream_stats"]["29+ Note Streams"]["50% Max Velocity"]),
        (2,58,lambda data: data["stream_stats"]["29+ Note Streams"]["70% Max Velocity"]),
        (2,59,lambda data: data["stream_stats"]["29+ Note Streams"]["90% Max Velocity"]),
        (0,61,lambda _: str(rdata["longest_rhythm_pattern"]["pattern"])),
        (1,61,lambda data: data["longest_rhythm_pattern"]["pattern length"]),
        (2,61,lambda data: data["longest_rhythm_pattern"]["jump_v"]["min"]),
        (2,62,lambda data: data["longest_rhythm_pattern"]["jump_v"]["median"]),
        (2,63,lambda data: data["longest_rhythm_pattern"]["jump_v"]["max"]),
        (3,61,lambda data: data["longest_rhythm_pattern"]["stream_v"]["min"]),
        (3,62,lambda data: data["longest_rhythm_pattern"]["stream_v"]["median"]),
        (3,63,lambda data: data["longest_rhythm_pattern"]["stream_v"]["max"]),
        (0,64,lambda data: data["rhythm_counts"]["50%"]["pattern_count"]),
        (1,64,lambda data: data["rhythm_counts"]["50%"]["rhythm_jumps"]["min"]),
        (1,65,lambda data: data["rhythm_counts"]["50%"]["rhythm_jumps"]["median"]),
        (1,66,lambda data: data["rhythm_counts"]["50%"]["rhythm_jumps"]["max"]),
        (2,64,lambda data: data["rhythm_counts"]["50%"]["rhythm_streams"]["min"]),
        (2,65,lambda data: data["rhythm_counts"]["50%"]["rhythm_streams"]["median"]),
        (2,66,lambda data: data["rhythm_counts"]["50%"]["rhythm_streams"]["max"]),
        (0,67,lambda data: data["rhythm_counts"]["70%"]["pattern_count"]),
        (1,67,lambda data: data["rhythm_counts"]["70%"]["rhythm_jumps"]["min"]),
        (1,68,lambda data: data["rhythm_counts"]["70%"]["rhythm_jumps"]["median"]),
        (1,69,lambda data: data["rhythm_counts"]["70%"]["rhythm_jumps"]["max"]),
        (2,67,lambda data: data["rhythm_counts"]["70%"]["rhythm_streams"]["min"]),
        (2,68,lambda data: data["rhythm_counts"]["70%"]["rhythm_streams"]["median"]),
        (2,69,lambda data: data["rhythm_counts"]["70%"]["rhythm_streams"]["max"]),
        (0,70,lambda data: data["rhythm_counts"]["90%"]["pattern_count"]),
        (1,70,lambda data: data["rhythm_counts"]["90%"]["rhythm_jumps"]["min"]),
        (1,71,lambda data: data["rhythm_counts"]["90%"]["rhythm_jumps"]["median"]),
        (1,72,lambda data: data["rhythm_counts"]["90%"]["rhythm_jumps"]["max"]),
        (2,70,lambda data: data["rhythm_counts"]["90%"]["rhythm_streams"]["min"]),
        (2,71,lambda data: data["rhythm_counts"]["90%"]["rhythm_streams"]["median"]),
        (2,72,lambda data: data["rhythm_counts"]["90%"]["rhythm_streams"]["max"]),
        (0,74,lambda data: data["maxcel"]),
        (1,74,lambda _: "50%"),
        (2,74,lambda _: "70%"),
        (3,74,lambda _: "90%"),
        (1,75,lambda data: data["thresholds"]["50%"]["count"]),
        (2,75,lambda data: data["thresholds"]["70%"]["count"]),
        (3,75,lambda data: data["thresholds"]["90%"]["count"]),
    ]

    # Determine the required number of rows from the mappings
    max_offset = max(offset for offset, _, _ in mappings)
    num_rows = max_offset + 1  # Add 1 because row offsets start at 0

    # Initialize a nested list for batch updates
    sheet_updates = [["" for _ in range(80)] for _ in range(num_rows)]  # 26 columns, adjust if needed

    # Write data to the sheet dynamically
    for offset, column, get_value in mappings:
        try:
            # Calculate row relative to `rownumber`
            row = rownumber + offset
            # Extract value using the lambda function
            value = get_value(jdata if column < 35 else sdata if column<60 else rdata if column < 73 else adata) #if column < 22 else rdata
            # Update the corresponding cell in the batch list
            sheet_updates[row - rownumber][column - 1] = value  # Adjust for 0-based indexing
        except KeyError as e:
            print(f"Missing data for column {column} at row {row}: {e}")

    # Define the range for batch updates
    sheet_range = f"A{rownumber}:CB{rownumber + num_rows - 1}"  # Adjust range to match your sheet layout

    # Perform batch update
    sheet.update(sheet_range, sheet_updates)


def easier_stats(jdata, sdata, fdata,rdata,adata, rownumber, sheet, title, artist, bpm):
    
    mappings = [
        (0, 1, lambda _:  artist),
        (1, 1, lambda _:  title),
        (2, 1, lambda _:  str(bpm)),
        (0, 2, lambda _: "Peak Jump Velocity"),
        (1, 2, lambda data: data["peak_jump"]["peak_velocity"]),
        (2, 2, lambda _: "Associated Length"),
        (3, 2, lambda data: data["peak_jump"]["jump_length"]),
        (0, 3, lambda _: "Longest Jump Pattern"),
        (1, 3, lambda data: data["longest_jump_pattern"]["peak_length"]),
        (2, 3, lambda _: "Associated Velocity"),
        (3, 3, lambda data: data["longest_jump_pattern"]["velocity_stats"]["max"]),
        (0, 4, lambda _: "0-1 Jumps"),
        (1, 4, lambda data: data["jump_counts"]["0-1"]["jump_count"]),
        (2, 4, lambda _: "0-1 Patterns"),
        (3, 4, lambda data: data["jump_counts"]["0-1"]["pattern_count"]),
        (0, 5, lambda _: "1-1.5 Jumps"),
        (1, 5, lambda data: data["jump_counts"]["1-1.5"]["jump_count"]),
        (2, 5, lambda _: "1-1.5 Patterns"),
        (3, 5, lambda data: data["jump_counts"]["1-1.5"]["pattern_count"]),
        (0, 6, lambda _: "1.5-2 Jumps"),
        (1, 6, lambda data: data["jump_counts"]["1.5-2"]["jump_count"]),
        (2, 6, lambda _: "1.5-2 Patterns"),
        (3, 6, lambda data: data["jump_counts"]["1.5-2"]["pattern_count"]),
        (0, 7, lambda _: "2-2.5 Jumps"),
        (1, 7, lambda data: data["jump_counts"]["2-2.5"]["jump_count"]),
        (2, 7, lambda _: "2-2.5 Patterns"),
        (3, 7, lambda data: data["jump_counts"]["2-2.5"]["pattern_count"]),
        (0, 8, lambda _: "2.5-3 Jumps"),
        (1, 8, lambda data: data["jump_counts"]["2.5-3"]["jump_count"]),
        (2, 8, lambda _: "2.5-3 Patterns"),
        (3, 8, lambda data: data["jump_counts"]["2.5-3"]["pattern_count"]),
        (0, 9, lambda _: "3-3.5 Jumps"),
        (1, 9, lambda data: data["jump_counts"]["3-3.5"]["jump_count"]),
        (2, 9, lambda _: "3-3.5 Patterns"),
        (3, 9, lambda data: data["jump_counts"]["3-3.5"]["pattern_count"]),
        (0, 10, lambda _: "3.5-4 Jumps"),
        (1, 10, lambda data: data["jump_counts"]["3.5-4"]["jump_count"]),
        (2, 10, lambda _: "3.5-4 Patterns"),
        (3, 10, lambda data: data["jump_counts"]["3.5-4"]["pattern_count"]),
        (0, 11, lambda _: "4-4.5 Jumps"),
        (1, 11, lambda data: data["jump_counts"]["4-4.5"]["jump_count"]),
        (2, 11, lambda _: "4-4.5 Patterns"),
        (3, 11, lambda data: data["jump_counts"]["4-4.5"]["pattern_count"]),
        (0, 12, lambda _: "4.5+ Jumps"),
        (1, 12, lambda data: data["jump_counts"]["4.5-+"]["jump_count"]),
        (2, 12, lambda _: "4.5+ Patterns"),
        (3, 12, lambda data: data["jump_counts"]["4.5-+"]["pattern_count"]),
        (0, 14, lambda _: "Peak Stream Velocity"),
        (1, 14, lambda data: data["peak_flow"]["peak_flow"]),
        (2, 14, lambda _: "Associate Length"),
        (3, 14, lambda data: data["peak_flow"]["stream_length"]),
        (0, 15, lambda _: "Longest Stream"),
        (1, 15, lambda data: data["longest_stream"]["longest_stream"]),
        (2, 15, lambda _: "Associated Velocity"),
        (3, 15, lambda data: data["longest_stream"]["velocity_peak"]),
        (0, 16, lambda _: "Triples Count"),
        (1, 16, lambda data: data["stream_stats"]["Triples"]["count"]),
        (2, 16, lambda _: "Triples Max Vel"),
        (3, 16, lambda data: data["stream_stats"]["Triples"]["max_velocity"]),
        (0, 16, lambda _: "Triples Count"),
        (1, 16, lambda data: data["stream_stats"]["Triples"]["count"]),
        (2, 16, lambda _: "Triples Max Vel"),
        (3, 16, lambda data: data["stream_stats"]["Triples"]["max_velocity"]),
        (0, 17, lambda _: "Quints Count"),
        (1, 17, lambda data: data["stream_stats"]["Quints"]["count"]),
        (2, 17, lambda _: "Quints Max Vel"),
        (3, 17, lambda data: data["stream_stats"]["Quints"]["max_velocity"]),
        (0, 18, lambda _: "2,4,6 Note Count"),
        (1, 18, lambda data: data["stream_stats"]["2, 4, 6 Note"]["count"]),
        (2, 18, lambda _: "2,4,6 Note Max Vel"),
        (3, 18, lambda data: data["stream_stats"]["2, 4, 6 Note"]["max_velocity"]),
        (0, 19, lambda _: "7-14 Note Bursts Count"),
        (1, 19, lambda data: data["stream_stats"]["7-14 Note Bursts"]["count"]),
        (2, 19, lambda _: "7-14 Note Bursts Max Vel"),
        (3, 19, lambda data: data["stream_stats"]["7-14 Note Bursts"]["max_velocity"]),
        (0, 20, lambda _: "15-28 Note Streams Count"),
        (1, 20, lambda data: data["stream_stats"]["15-28 Note Streams"]["count"]),
        (2, 20, lambda _: "15-28 Note Streams Max Vel"),
        (3, 20, lambda data: data["stream_stats"]["15-28 Note Streams"]["max_velocity"]),
        (0, 21, lambda _: "29+ Note Streams Count"),
        (1, 21, lambda data: data["stream_stats"]["29+ Note Streams"]["count"]),
        (2, 21, lambda _: "29+ Note Streams Max Vel"),
        (3, 21, lambda data: data["stream_stats"]["29+ Note Streams"]["max_velocity"]),
        (0, 22, lambda _: "Longest Rhythm Pattern"),
        (1,22, lambda _: str(rdata["longest_rhythm_pattern"]["pattern"])),
        (2, 22, lambda _: "Pattern Length"),
        (3, 22, lambda _: rdata["longest_rhythm_pattern"]["pattern length"])

    ]
    max_offset = max(offset for offset, _, _ in mappings)
    num_rows = max_offset + 1  # Add 1 because row offsets start at 0

    # Initialize a nested list for batch updates
    sheet_updates = [["" for _ in range(25)] for _ in range(num_rows)]  # 26 columns, adjust if needed

    # Write data to the sheet dynamically
    for offset, column, get_value in mappings:
        try:
            # Calculate row relative to `rownumber`
            row = rownumber + offset
            # Extract value using the lambda function
            value = get_value(jdata if column < 13 else sdata if column<60 else rdata if column < 73 else adata) #if column < 22 else rdata
            # Update the corresponding cell in the batch list
            sheet_updates[row - rownumber][column - 1] = value  # Adjust for 0-based indexing
        except KeyError as e:
            print(f"Missing data for column {column} at row {row}: {e}")

    # Define the range for batch updates
    sheet_range = f"A{rownumber}:Z{rownumber + num_rows - 1}"  # Adjust range to match your sheet layout

    # Perform batch update
    sheet.update(sheet_range, sheet_updates)