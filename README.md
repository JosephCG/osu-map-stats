REALTIME BUILD REQUIRES TOSU!!!!!!! https://github.com/tosuapp/tosu
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
