from get_files import get_osu_file, extract_metadata
from transform_data import transform_hitobjects, get_jump_streaks_time, get_accstream_streaks, get_rhythm_pattern_time
from getting_stats import get_jump_statistics, get_streams_stats, calculate_flowaim, get_rhythm_stats
from presentingstats import update_velocity_stats, print_stats
def main():
    osu_file_path = get_osu_file()
    #   # Get the file path from the dialog
    time_sig, size, title = extract_metadata(osu_file_path)
    size2 = size
    csbonus = 36.49 / (23.05 - (size - 7) * 4.4825)
    csbonus2 = csbonus
    timebonus = 1
    bpm = [round(60000/x) for x in time_sig]
    if len(bpm) > 1:
        minbpm = int(input(f"The map has multiple bpms {bpm}, select a MIN bpm for analysis: "))
        maxbpm = int(input("Max bpm: "))
        time_sig = [60000/maxbpm, 60000/minbpm]
    transformation = transform_hitobjects(osu_file_path)
    # Jump statistics
    jump_data = get_jump_streaks_time(transformation, time_sig)
    save_jump_to_file(jump_data, title)
    jump_stats = get_jump_statistics(jump_data, [50, 70, 90])
    stream_data = get_accstream_streaks(transformation, time_sig)
    save_stream_to_file(stream_data, title)
    stream_stats = get_streams_stats(stream_data)
    flow_stats = calculate_flowaim(stream_data)
    rhythm_data = get_rhythm_pattern_time(transformation, time_sig)
    save_rhythm_to_file(rhythm_data, title)
    rhythm_stats = get_rhythm_stats(rhythm_data)
    main_stats = update_velocity_stats(jump_stats, stream_stats, flow_stats, rhythm_stats, csbonus * timebonus)
    print_stats(main_stats,bpm, jump_stats, stream_stats, rhythm_stats)
    size2, timebonus = mods(input("mods: "), size)
    if size2 == size and timebonus == 1:
        print("no mods applied")
    else: 
        csbonus2 = 36.49 / (23.05 - (size2 - 7) * 4.4825)
        main_stats = update_velocity_stats(jump_stats, stream_stats, flow_stats, rhythm_stats,  csbonus2 / csbonus * timebonus)
        moddedbpm = [round(x * timebonus) for x in bpm]
        print_stats(main_stats,moddedbpm, jump_stats, stream_stats, rhythm_stats)
if __name__ == "__main__":
    main()
