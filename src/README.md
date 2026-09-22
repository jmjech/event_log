# Acoustic Survey Metadata - Event Log
The event log is a file that hosts survey-level metadata for an acoustic survey. It contains dates, time, latitudes, longitudes, and event descriptors, e.g., where, why, what of activities during the survey.  

## clean_eventlog.py
This Python program is used to select the beginning and ending metadata for transect-based sampling. It will renumber transect numbers starting at zero. The codes for begin/start, end/stop, and resuming transects are:  
- "begin": the beginning of a transect
- "end": the end of a transect
- "stop": when an activity is conducted during a transect, the transect is stopped for that activity. This, in conjunction with "start", is used to exclude data from analysis for transect-based estimates.
- "start": start of another activity during a transect
- "resume": restart the transect after stopping. Data will be included in transect-based estimates after this.
Only these codes are recognized in the program.
The "begin" & "end" pair define the full transect.
### Examples:
1. "begin" -> "end": one full transect without stops. Begin the transect and end the transect.
2. "begin" -> "stop" -> "start" -> "stop" -> "resume" -> "end": a transect with one activity. Begin the transect, stop the transect, start the activity, stop the activity, resume the transect, and finally end the transect. </br>

The program works for one activity. TBD - fix the program for more than one activity per transect.

