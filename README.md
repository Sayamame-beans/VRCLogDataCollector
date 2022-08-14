# VRCLogDataCollector
Data collector tool from log files of VRChat.

## Why was this tool created?
It was to collect data for this Canny ([Slowed down to enter an instance? | Voters | VRChat](https://feedback.vrchat.com/feature-requests/p/slowed-down-to-enter-an-instance)).

### Tips
`~region(us)` is interpreted as `~region(usw)`

## Input
Log files of VRChat

## Output
`LogData.csv`

## Usage Example
run `python log_collector.py ./logfiles_dir` in a shell or something.

If the data is successfully collected, LogData.csv is created in the specified folder of log files.

## Environment
- Windows 10
- Python 3.9.2
