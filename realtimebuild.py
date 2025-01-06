from get_files import extract_metadata
from transform_data import transform_hitobjects, get_jump_streaks_time, get_accstream_streaks, get_rhythm_pattern_time
from getting_stats import get_jump_statistics, get_streams_stats, calculate_flowaim, get_rhythm_stats
from presentingstats import update_velocity_stats, print_stats
import asyncio
import websockets
import json


def analyze_osu_file(osu_file_path, gamemods):
    try:
        print(f"Analyzing: {osu_file_path}")
        time_sig, size, title = extract_metadata(osu_file_path)
        if "HR" in gamemods:
            size *= 1.4
        csbonus = 36.4975 / (23.05 - (size - 7) * 4.4825)
        timebonus = 1  # Default timebonus
        if any(mod in gamemods for mod in ["DT", "NC"]):  # Check for either "DT" or "NC"
            timebonus = 1.5
            print("DT/NC mod detected, Timebonus applied.")

        bpm = [round(60000 / x * timebonus)  for x in time_sig]
        
        if max(bpm) > min(bpm) + 15:
            print("invalid bpm ranhge")
            
        else:
            transformation = transform_hitobjects(osu_file_path)
            jump_data = get_jump_streaks_time(transformation, time_sig)
            if jump_data != []:
                jump_stats = get_jump_statistics(jump_data, [50, 70, 90])
            else: 
                jump_stats = jump_data
            stream_data = get_accstream_streaks(transformation, time_sig)
            if stream_data != []:
                stream_stats = get_streams_stats(stream_data)
                flow_stats = calculate_flowaim(stream_data)
            else: 
                stream_stats = stream_data
                flow_stats = stream_data
            rhythm_data = get_rhythm_pattern_time(transformation, time_sig)
            if rhythm_data != []:
                rhythm_stats = get_rhythm_stats(rhythm_data)
            else: 
                rhythm_stats = rhythm_data
            main_stats = update_velocity_stats(jump_stats, stream_stats, flow_stats, rhythm_stats, csbonus * timebonus)
            print_stats(main_stats, bpm, jump_stats, stream_stats, rhythm_stats)
    except Exception as e:
        print(f"Error analyzing file: {osu_file_path}\n{e}")

# WebSocket listener
async def connect_and_process(uri):
    last_osu_file_path = None
    last_mods = None
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")
        try:
            while True:
                # Receive data from the WebSocket
                data = json.loads(await websocket.recv())
                osu_file_path = data["settings"]["folders"]["songs"] + "\\" + \
                                data["menu"]["bm"]["path"]["folder"] + "\\" + \
                                data["menu"]["bm"]["path"]["file"]
                gamemods = data["menu"]["mods"]
                mod_string = gamemods.get('str', '')
                

                if osu_file_path != last_osu_file_path or mod_string != last_mods:
                    last_osu_file_path = osu_file_path  # Update the stored path
                    last_mods = mod_string
                    analyze_osu_file(osu_file_path, mod_string)
        except websockets.ConnectionClosed as e:
            print(f"Connection closed: {e}")

# Main function
async def main():
    websocket_uri = "ws://localhost:24050/ws"  # Replace with your WebSocket URI
    await connect_and_process(websocket_uri)

# Start the asyncio event loop
asyncio.run(main())