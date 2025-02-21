realtimebuild requires tosu!!!!!!! https://github.com/tosuapp/tosu
also only works on stable!!!!!!
need to do pip install sockets for real time build

mapbymap works by selecting the .osu file of maps found in your songs folder

Once you run the program you will often see that there is often an extra number paired with the stat, this is an associated stat giving more detail and context of the stat
Listing the associated stats here, the normal stats should be obvious i hope idk
Jump Stats:
Peak Jump Velocity: length of pattern
Longest jump pattern: peak velocity
Velocity Counts: Longest pattern that meets the vvelocity threshold

Stream Stats:
Peak Stream Velocity: Length of Stream 
Longest Stream PAttern: Peak Velocity
Note Counts: Peak Velocity
Flowaim Velocity Counts: there are none

Longest Rhythm Pattern: Note count of pattern, timestamp, the pattern

also how rhythm patterns works:

requires 1/4th rhythm or less to be considered a rhythm pattern
pattern instantly ends if the delta time is greater than a 1/2 beat
2 consecutive singles breaks the rhythm pattern
a single will not break the rhythm pattern if followed by another double or greater 
1-5-1-1-5-1
is counted as 2 different patterns and marked as
1-5-1
1-5-1

get_files has the function for the user to select the map manually, and also the function that extracts bpm/cs/title for some reason
transform_data includes the functions that converts .osu files to more readable lists, and that more readable list into other more specified lists for easier data extraction for the stats.
also a lot of functions in this file aren't used.  they were made for more extraction of more otherr stats like angles and accelaration, but i didnt bother using that build for now

getting_stats has the functions that extract the map stats from iterated lists

presenting_stats has functions for asking user input for converting mods for multipliers, printing the stats, and updating the stats given mods and cs 

