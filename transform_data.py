import tkinter as tk
from tkinter import filedialog
import math
import os
import re
import json
import sys

def transform_hitobjects(osu_file_path):
    with open(osu_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    hit_objects_section_found = False
    previous_object = None
    transformed_data = []
    for line in lines:
        if line.startswith("[HitObjects]"):
            hit_objects_section_found = True
            continue

        if hit_objects_section_found:
            if line.strip() == "" or line.startswith("["):
                break

            # Parse hit object data
            parts = line.strip().split(',')
            try:
                x, y, time, objtype = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
            except (ValueError, IndexError):
                continue  # Skip invalid lines

            # Skip spinners
            if objtype == 12:
                continue

            if previous_object:
                prev_x, prev_y, prev_time = previous_object

                # Calculate distance, delta time, and velocity
                distance = math.sqrt((x - prev_x) ** 2 + (y - prev_y) ** 2)
                delta_time = time - prev_time
                velocity = round(distance / delta_time, 2) if delta_time > 0 else 0
            else:
                # For the first object, set distance and delta time to 0
                distance = 0
                delta_time = 0
                velocity = 0

            # Append data as a tuple
            transformed_data.append((distance, delta_time, velocity, time))

            # Update the previous object
            previous_object = (x, y, time)

    return transformed_data

def get_jump_streaks(transformed_data, time_sig):
    jump_streaks = []
    current_streak = []
    margin = 10
    half_beat_interval = (min(time_sig)/2 - margin, max(time_sig)/2 + margin)

    for index, (distance, delta_time, velocity, time) in enumerate(transformed_data):
        # Check if the current object is a jump
        if half_beat_interval[0] <= delta_time <= half_beat_interval[1]:
            current_streak.append(velocity)  # Store velocity

        # If the current streak ends
        elif current_streak:
            length = len(current_streak)
            max_velocity = max(current_streak)
            jump_streaks.append((length, max_velocity, current_streak))  # Store as (length, max_velocity, velocities)
            current_streak = []  # Reset the current streak

    # Check for any remaining streak after the loop ends
    if current_streak:
        length = len(current_streak)
        max_velocity = max(current_streak)
        jump_streaks.append((length, max_velocity, current_streak))

    return jump_streaks

def get_stream_streaks(transformed_data, time_sig):
    stream_streaks = []
    current_streak = []
    margin = 10
    quarter_beat_interval = (min(time_sig)/4 - margin, max(time_sig)/4 + margin)

    for index, (distance, delta_time, velocity, time) in enumerate(transformed_data):
        # Check if the current object is part of a stream
        if quarter_beat_interval[0] <= delta_time <= quarter_beat_interval[1]: 
            current_streak.append(velocity)  # Store velocity

        # If the current streak ends
        elif current_streak:
            length = len(current_streak) + 1  # Count includes the first object
            max_velocity = max(current_streak)
            stream_streaks.append((length, max_velocity, current_streak))  # Store as (length, max_velocity, velocities)
            current_streak = []  # Reset the current streak

    # Check for any remaining streak after the loop ends
    if current_streak:
        length = len(current_streak) + 1  # Count includes the first object
        max_velocity = max(current_streak)
        stream_streaks.append((length, max_velocity, current_streak))

    return stream_streaks

def get_rhythm_pattern(transformed_data, timesig):
    rhythm_patterns = []
    current = []
    count = 1  # To count consecutive 1/4 beat gaps
    previous_delta = 0
    past_delta = 0
    quarter_beat_interval = (min(timesig) / 4 -10, max(timesig)/4 + 10)
    half_beat_interval = (min(timesig) / 2 -10, max(timesig)/2 + 10)

    for index, (distance, delta_time, velocity, time) in enumerate(transformed_data):
        if current == [] and count == 1:
            if quarter_beat_interval[0] <= delta_time <= quarter_beat_interval[1]:
                if quarter_beat_interval[0] <= previous_delta <= half_beat_interval[1]:  
                    current.append(1)
                count = count + 1
        else:
            if quarter_beat_interval[0] <= delta_time <= quarter_beat_interval[1]:
                count = count + 1  
            if delta_time > quarter_beat_interval[1]:
                if count > 1:
                    current.append(count)
                    count = 1
                if half_beat_interval[1] >= previous_delta > quarter_beat_interval[1]:
                    if current[-1] > 1:
                        current.append(1)
                if delta_time > half_beat_interval[1] or (previous_delta >= quarter_beat_interval[1] and past_delta >= quarter_beat_interval[1]):
                    rhythm_patterns.append(current)
                    count = 1
                    current = []
        past_delta = previous_delta            
        previous_delta = delta_time
        
    if count > 1:
      current.append(count)  
    else: 
        if half_beat_interval[1]>= delta_time > quarter_beat_interval[1] and len(current) >=1:
            if current[-1] > 1:
                current.append(1)    
    if current:
        rhythm_patterns.append(current)    
    return rhythm_patterns

def god_transform(osu_file_path, multiplier):
    with open(osu_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    x_velocity = 0
    y_velocity = 0
    prevx_vel = 0
    prevy_vel = 0
    hit_objects_section_found = False
    previous_object = None
    transformed_data = []
    for line in lines:
        if line.startswith("[HitObjects]"):
            hit_objects_section_found = True
            continue

        if hit_objects_section_found:
            if line.strip() == "" or line.startswith("["):
                break

            # Parse hit object data
            parts = line.strip().split(',')
            try:
                x, y, time, objtype = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
            except (ValueError, IndexError):
                continue  # Skip invalid lines

            # Skip spinners
            if objtype == 12:
                continue

            if previous_object:
                prev_x, prev_y, prev_time, prevx_vel, prevy_vel = previous_object

                # Calculate distance, delta time, and velocity
                distance = multiplier * math.sqrt((x - prev_x) ** 2 + (y - prev_y) ** 2)
                delta_time = time - prev_time
                velocity = round(distance / delta_time, 2) if delta_time > 0 else 0
                x_velocity = round((x - prev_x) / delta_time, 2) if delta_time > 0 else 0
                y_velocity = round((y - prev_y) / delta_time, 2) if delta_time > 0 else 0
            else:
                # For the first object, set distance and delta time to 0
                distance = 0
                delta_time = 0
                velocity = 0

            angle_prev = math.atan2(prevy_vel, prevx_vel)
            angle_current = math.atan2(y_velocity, x_velocity)
    
    # Compute the directed difference and convert it to degrees
            angle_difference = math.degrees(angle_current - angle_prev)
    
    # Normalize to the range [0, 360] degrees
            if angle_difference < 0:
                angle_difference += 360  
            if angle_difference > 180:
                angle_difference = 360 - angle_difference
            angle_difference = 180 - angle_difference
            transformed_data.append((distance, delta_time, velocity, time, round(angle_difference)))

            # Update the previous object
            previous_object = (x, y, time, x_velocity, y_velocity)

    return transformed_data

def get_stream_streaks_accel(transformed_data, time_sig):
    stream_streaks = []
    current_streak = []
    x_velocities = []
    y_velocities = []
    margin = 10
    quarter_beat_interval = (min(time_sig) / 4 - margin, max(time_sig) / 4 + margin)

    for index, (distance, delta_time, velocity, time, x_velocity , y_velocity) in enumerate(transformed_data):

        # Check if the current object is part of a stream
        if quarter_beat_interval[0] <= delta_time <= quarter_beat_interval[1]: 
            current_streak.append(velocity)  # Store only the velocity magnitude
            x_velocities.append(x_velocity)
            y_velocities.append(y_velocity)

        # If the current streak ends
        elif current_streak:
            length = len(current_streak) + 1
            max_velocity = max(current_streak)
            
            if len(current_streak) >= 2:# Calculate absolute acceleration list
                abs_acceleration = [
                current_streak[i] - current_streak[i - 1]
                for i in range(1, len(current_streak))
                ]
            
            # Calculate directional acceleration list
                dir_acceleration = [
                math.sqrt(
                    (x_velocities[i] - x_velocities[i - 1]) ** 2 +
                    (y_velocities[i] - y_velocities[i - 1]) ** 2
                )
                for i in range(1, len(x_velocities))
                ]

            # Append stream streak data with accelerations
            stream_streaks.append((length, max_velocity, current_streak, abs_acceleration, dir_acceleration))
            
            # Reset streak and directional components
            current_streak = []
            x_velocities = []
            y_velocities = []

    # Check for any remaining streak after the loop ends
    if current_streak:
        length = len(current_streak) + 1
        max_velocity = max(current_streak)
        
        if len(current_streak) >= 2:# Calculate absolute acceleration list
                abs_acceleration = [
                current_streak[i] - current_streak[i - 1]
                for i in range(1, len(current_streak))
                ]
            
            # Calculate directional acceleration list
                dir_acceleration = [
                math.sqrt(
                    (x_velocities[i] - x_velocities[i - 1]) ** 2 +
                    (y_velocities[i] - y_velocities[i - 1]) ** 2
                )
                for i in range(1, len(x_velocities))
                ]

        stream_streaks.append((length, max_velocity, current_streak, abs_acceleration, dir_acceleration))

    return stream_streaks

def get_accstream_streaks(transformed_data, time_sig):
    stream_streaks = []
    current_streak = []
    margin = 10
    quarter_beat_interval = (min(time_sig)/4 - margin, max(time_sig)/4 + margin)

    for index, (distance, delta_time, velocity, time) in enumerate(transformed_data):
        # Check if the current object is part of a stream
        if quarter_beat_interval[0] <= delta_time <= quarter_beat_interval[1]: 
            if current_streak == []:
                start_time = prev_time
            current_streak.append(velocity)  # Store velocity

        # If the current streak ends
        elif current_streak:
            if len(current_streak) >= 1:
                abs_acceleration = [
                    current_streak[i] - current_streak[i - 1]
                    for i in range(1, len(current_streak))
                ]

            length = len(current_streak) + 1  # Count includes the first object
            max_velocity = max(current_streak)
            stream_streaks.append((start_time, length, max_velocity, current_streak, abs_acceleration))  # Store as (length, max_velocity, velocities)
            current_streak = []  # Reset the current streak
        prev_time = time
    # Check for any remaining streak after the loop ends
    if current_streak:
        if len(current_streak) >= 1:
                abs_acceleration = [
                    current_streak[i] - current_streak[i - 1]
                    for i in range(1, len(current_streak))
                ]
        
        length = len(current_streak) + 1  # Count includes the first object
        max_velocity = max(current_streak)
        stream_streaks.append((start_time, length, max_velocity, current_streak, abs_acceleration))

    return stream_streaks

def get_jump_streaks_time(transformed_data, time_sig):
    jump_streaks = []
    current_streak = []
    margin = 10
    half_beat_interval = (min(time_sig)/2 - margin, max(time_sig)/2 + margin)

    for index, (distance, delta_time, velocity, time) in enumerate(transformed_data):
        # Check if the current object is a jump
        if half_beat_interval[0] <= delta_time <= half_beat_interval[1]:
            if current_streak == []:
                start_time = prev_time
            current_streak.append(velocity)  # Store velocity

        # If the current streak ends
        elif current_streak:
            length = len(current_streak)
            max_velocity = max(current_streak)
            jump_streaks.append((start_time, length, max_velocity, current_streak))  # Store as (length, max_velocity, velocities)
            current_streak = []  # Reset the current streak

        prev_time = time
    # Check for any remaining streak after the loop ends
    if current_streak:
        length = len(current_streak)
        max_velocity = max(current_streak)
        jump_streaks.append((start_time, length, max_velocity, current_streak))

    return jump_streaks

def get_rhythm_pattern_time(transformed_data, timesig):
    rhythm_patterns = []
    current = []
    count = 1  # To count consecutive 1/4 beat gaps
    previous_delta = 0
    past_delta = 0
    quarter_beat_interval = (min(timesig) / 4 -10, max(timesig)/4 + 10)
    half_beat_interval = (min(timesig) / 2 -10, max(timesig)/2 + 10)
    previous_time = 0
    for index, (distance, delta_time, velocity, time) in enumerate(transformed_data):
        if current == [] and count == 1:
            if quarter_beat_interval[0] <= delta_time <= quarter_beat_interval[1]:
                if quarter_beat_interval[0] <= previous_delta <= half_beat_interval[1]:
                    start_time = past_time  
                    current.append(1)
                else: 
                    start_time = previous_time
                count = count + 1
        else:
            if quarter_beat_interval[0] <= delta_time <= quarter_beat_interval[1]:
                count = count + 1  
            if delta_time > quarter_beat_interval[1]:
                if count > 1:
                    current.append(count)
                    count = 1
                if half_beat_interval[1] >= previous_delta > quarter_beat_interval[1]:
                    if current[-1] > 1:
                        current.append(1)
                if delta_time > half_beat_interval[1] or (previous_delta >= quarter_beat_interval[1] and past_delta >= quarter_beat_interval[1]):
                    rhythm_patterns.append((start_time, current))
                    count = 1
                    current = []
        past_delta = previous_delta            
        previous_delta = delta_time
        past_time = previous_time
        previous_time = time
    if count > 1:
      current.append(count)  
    else: 
        if half_beat_interval[1]>= delta_time > quarter_beat_interval[1] and len(current) >=1:
            if current[-1] > 1:
                current.append(1)    
    if current:
        rhythm_patterns.append((start_time, current))    
    return rhythm_patterns
# everything past here isnt used yet, for extra stats build 
def get_rhythm_pattern_plus(transformed_data, timesig):
    rhythm_patterns = []
    jump_list = []
    stream_list = []
    current = []
    count = 1  # To count consecutive 1/4 beat gaps
    previous_delta = 0
    past_delta = 0
    quarter_beat_interval = (min(timesig) / 4 -10, max(timesig)/4 + 10)
    half_beat_interval = (min(timesig) / 2 -10, max(timesig)/2 + 10)
    previous_time = 0
    for index, (distance, delta_time, velocity, time) in enumerate(transformed_data):
        if current == [] and count == 1:
            if quarter_beat_interval[0] <= delta_time <= quarter_beat_interval[1]:
                stream_list.append(velocity)
                if quarter_beat_interval[1] < previous_delta <= half_beat_interval[1]:
                    start_time = past_time 
                    jump_list.append(prev_velocity)
                    current.append(1)
                else: 
                    start_time = previous_time
                count = count + 1
        else:
            if quarter_beat_interval[0] <= delta_time <= quarter_beat_interval[1]:
                stream_list.append(velocity)
                count = count + 1  
            if delta_time > quarter_beat_interval[1]:
                if count > 1:
                    current.append(count)
                    count = 1
                if half_beat_interval[1] >= previous_delta > quarter_beat_interval[1]:
                    if current[-1] > 1:
                        current.append(1)
                        jump_list.append(prev_velocity)
                if delta_time > half_beat_interval[1] or (previous_delta >= quarter_beat_interval[1] and past_delta >= quarter_beat_interval[1]):
                    sumr = sum(current)
                    rhythm_patterns.append((start_time, current, sumr, jump_list, stream_list))
                    jump_list = []
                    stream_list = []
                    count = 1
                    current = []
        past_delta = previous_delta            
        previous_delta = delta_time
        past_time = previous_time
        previous_time = time
        prev_velocity = velocity
    if count > 1:
      current.append(count)  
    else: 
        if half_beat_interval[1]>= delta_time > quarter_beat_interval[1] and len(current) >=1:
            if current[-1] > 1:
                current.append(1)  
                jump_list.append(elocity)  
    if current:
        sumr = sum(current)
        rhythm_patterns.append((start_time, current, sumr, jump_list, stream_list))    
    return rhythm_patterns

def god_jump_streaks(transformed_data, time_sig):
    jump_streaks = []
    current_streak = []
    angle_streak = []
    margin = 10
    half_beat_interval = (min(time_sig)/2 - margin, max(time_sig)/2 + margin)

    for index, (distance, delta_time, velocity, time, angle) in enumerate(transformed_data):
        # Check if the current object is a jump
        if half_beat_interval[0] <= delta_time <= half_beat_interval[1]:
            if current_streak == []:
                start_time = time - delta_time
            current_streak.append(velocity)  # Store velocity
            angle_streak.append(angle)
        # If the current streak ends
        elif current_streak:
            length = len(current_streak)
            max_velocity = max(current_streak)
            angle_streak.pop(0)
            jump_streaks.append((start_time, length, max_velocity, current_streak, angle_streak))  # Store as (length, max_velocity, velocities)
            current_streak = []  # Reset the current streak
            angle_streak = []
    # Check for any remaining streak after the loop ends
    if current_streak:
        length = len(current_streak)
        max_velocity = max(current_streak)
        angle_streak.pop(0)
        jump_streaks.append((start_time, length, max_velocity, current_streak, angle_streak))
    return jump_streaks

def god_stream_streaks(transformed_data, time_sig):
    stream_streaks = []
    current_streak = []
    margin = 10
    quarter_beat_interval = (min(time_sig)/4 - margin, max(time_sig)/4 + margin)

    for index, (distance, delta_time, velocity, time, angle) in enumerate(transformed_data):
        # Check if the current object is part of a stream
        if quarter_beat_interval[0] <= delta_time <= quarter_beat_interval[1]: 
            if current_streak == []:
                start_time = prev_time
            current_streak.append(velocity)  # Store velocity

        # If the current streak ends
        elif current_streak:
            if len(current_streak) >= 1:
                abs_acceleration = [
                    current_streak[i] - current_streak[i - 1]
                    for i in range(1, len(current_streak))
                ]

            length = len(current_streak) + 1  # Count includes the first object
            max_velocity = max(current_streak)
            stream_streaks.append((start_time, length, max_velocity, current_streak, abs_acceleration))  # Store as (length, max_velocity, velocities)
            current_streak = []  # Reset the current streak
        prev_time = time
    # Check for any remaining streak after the loop ends
    if current_streak:
        if len(current_streak) >= 1:
                abs_acceleration = [
                    round(current_streak[i] - current_streak[i - 1], 2)
                    for i in range(1, len(current_streak))
                ]
        
        length = len(current_streak) + 1  # Count includes the first object
        max_velocity = max(current_streak)
        stream_streaks.append((start_time, length, max_velocity, current_streak, abs_acceleration))
    return stream_streaks

def god_rhythm_pattern(transformed_data, timesig):
    rhythm_patterns = []
    jump_list = []
    stream_list = []
    current = []
    count = 1  # To count consecutive 1/4 beat gaps
    previous_delta = 0
    past_delta = 0
    quarter_beat_interval = (min(timesig) / 4 -10, max(timesig)/4 + 10)
    half_beat_interval = (min(timesig) / 2 -10, max(timesig)/2 + 10)
    previous_time = 0
    for index, (distance, delta_time, velocity, time, angle) in enumerate(transformed_data):
        if current == [] and count == 1:
            if quarter_beat_interval[0] <= delta_time <= quarter_beat_interval[1]:
                stream_list.append(velocity)
                if quarter_beat_interval[1] < previous_delta <= half_beat_interval[1]:
                    start_time = past_time 
                    jump_list.append(prev_velocity)
                    current.append(1)
                else: 
                    start_time = previous_time
                count = count + 1
        else:
            if quarter_beat_interval[0] <= delta_time <= quarter_beat_interval[1]:
                stream_list.append(velocity)
                count = count + 1  
                if quarter_beat_interval[1] < previous_delta <= half_beat_interval[1]:
                    jump_list.append(prev_velocity)
            if delta_time > quarter_beat_interval[1]:
                if count > 1:
                    current.append(count)
                    count = 1
                if half_beat_interval[1] >= previous_delta > quarter_beat_interval[1]:
                    if current[-1] > 1:
                        current.append(1)
                        jump_list.append(prev_velocity)
                if delta_time > half_beat_interval[1] or (previous_delta >= quarter_beat_interval[1] and past_delta >= quarter_beat_interval[1]):
                    sumr = sum(current)
                    rhythm_patterns.append((start_time, current, sumr, jump_list, stream_list))
                    jump_list = []
                    stream_list = []
                    count = 1
                    current = []
        past_delta = previous_delta            
        previous_delta = delta_time
        past_time = previous_time
        previous_time = time
        prev_velocity = velocity
    if count > 1:
      current.append(count)  
    else: 
        if half_beat_interval[1]>= delta_time > quarter_beat_interval[1] and len(current) >=1:
            if current[-1] > 1:
                current.append(1)  
                jump_list.append(velocity)  
    if current:
        sumr = sum(current)
        rhythm_patterns.append((start_time, current, sumr, jump_list, stream_list))    
    return rhythm_patterns
