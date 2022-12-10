import argparse
import csv
import os
import re
import traceback
from typing import TypedDict

class LogData(TypedDict):
    Datetime: str
    Mode: str #VR or Desktop
    EAC: str #Yes or No
    WorldName: str
    Region: str #esw ese eu jp
    Time_WorldFetch: str
    Time_RoomInstantiate: str
    Time_InitializingVRCObjects: str
    Time_ProcessingSceneObjects: str
    Time_FixingMaterials: str
    Time_FinalizingScene: str
    Time_EnteringWorld: str
    Time_WaitingToEnterRoom: str
    Time_SpawningPlayers: str

class LogDataCollector:
    VERSION = "1.1.1"
    LOGFILE_PATTERN1 = re.compile(r"output_log_\d{2}-\d{2}-\d{2}\.txt")
    LOGFILE_PATTERN2 = re.compile(r"output_log_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.txt")
    VR_PATTERN = re.compile(r"^.*?OpenVR initialized!")
    EAC_PATTERN = re.compile(r"^.*?\[EOSManager\].*?$")
    GO_HOME_PATTERN = re.compile(r"^.*?\[Behaviour\] Going to Home Location:.*?$")
    WORLDNAME_PATTERN = re.compile(r"^.*?\[Behaviour\] Entering Room: (.*?)\n")
    REGION_PATTERN = re.compile(r"^.*?\[Behaviour\] Joining wrld_(.*?~region\((.*?)\).*?|.*?)$")
    Time_WorldFetch_PATTERN = re.compile(r"^([0-9\.: ]*?) Log *?-  \[Behaviour\] ApiWorld took ([0-9\.E\-]*?)s to fetch\.")
    Time_RoomInstantiate_PATTERN = re.compile(r"^.*?\[Behaviour\] Room instantiate took ([0-9\.E\-]*?)s")
    Time_InitializingVRCObjects_PATTERN = re.compile(r"^.*?\[Behaviour\] Spent ([0-9\.E\-]*?)s initializing VRC Objects")
    Time_ProcessingSceneObjects_PATTERN = re.compile(r"^.*?\[Behaviour\] Spent ([0-9\.E\-]*?)s processing scene objects.")
    Time_FixingMaterials_PATTERN = re.compile(r"^.*?\[Behaviour\] Spent ([0-9\.E\-]*?)s fixing materials.")
    Time_FinalizingScene_PATTERN = re.compile(r"^.*?\[Behaviour\] Spent ([0-9\.E\-]*?)s finalizing scene.")
    Time_EnteringWorld_PATTERN = re.compile(r"^.*?\[Behaviour\] Spent ([0-9\.E\-]*?)s entering world.")
    Time_WaitingToEnterRoom_PATTERN = re.compile(r"^.*?\[Behaviour\] Spent ([0-9\.E\-]*?)s waiting to enter room.")
    Time_SpawningPlayers_PATTERN = re.compile(r"^.*?\[Behaviour\] Spent ([0-9\.E\-]*?)s spawning players.")

    def __init__(self):
        self.datalist = []
        pass

    def collect(self, path: str):
        logfile_list = [path + "/" + f for f in os.listdir(path) if (re.fullmatch(self.LOGFILE_PATTERN1, f) or re.fullmatch(self.LOGFILE_PATTERN2, f))]
        logfile_list.sort(key=os.path.getmtime)
        for logfile in logfile_list:
            self.read_log(logfile)

    def read_log(self, path: str):
        with open(path, encoding="utf_8", mode='r', errors="backslashreplace") as f:
            state = 0
            mode = "Desktop"
            hasEAC = "No"
            data = []
            temp = LogData(Datetime="", Mode="", EAC="", WorldName="", Region="", Time_WorldFetch="", Time_RoomInstantiate="", Time_InitializingVRCObjects="", Time_ProcessingSceneObjects="", Time_FixingMaterials="", Time_FinalizingScene="", Time_EnteringWorld="", Time_WaitingToEnterRoom="", Time_SpawningPlayers="")

            for line in f:
                if state == 0:
                    if re.match(self.VR_PATTERN, line):
                        mode = "VR"
                    if re.match(self.EAC_PATTERN, line):
                        hasEAC = "Yes"
                    if re.match(self.GO_HOME_PATTERN, line):
                        state = 1
                elif state >= 1:
                    if matched := re.match(self.Time_WorldFetch_PATTERN, line):
                        temp["Datetime"] = matched[1]
                        temp["Time_WorldFetch"] = matched[2]
                    elif matched := re.match(self.Time_RoomInstantiate_PATTERN, line):
                        temp["Time_RoomInstantiate"] = matched[1]
                    elif matched := re.match(self.Time_InitializingVRCObjects_PATTERN, line):
                        temp["Time_InitializingVRCObjects"] = matched[1]
                    elif matched := re.match(self.Time_ProcessingSceneObjects_PATTERN, line):
                        temp["Time_ProcessingSceneObjects"] = matched[1]
                    elif matched := re.match(self.Time_FixingMaterials_PATTERN, line):
                        temp["Time_FixingMaterials"] = matched[1]
                    elif matched := re.match(self.Time_FinalizingScene_PATTERN, line):
                        temp["Time_FinalizingScene"] = matched[1]
                    elif matched := re.match(self.WORLDNAME_PATTERN, line):
                        temp["WorldName"] = matched[1]
                    elif matched := re.match(self.REGION_PATTERN, line):
                        temp["Region"] = "usw" if (not matched[2] or matched[2] == "us") else matched[2]
                    elif matched := re.match(self.Time_EnteringWorld_PATTERN, line):
                        temp["Time_EnteringWorld"] = matched[1]
                    elif matched := re.match(self.Time_WaitingToEnterRoom_PATTERN, line):
                        temp["Time_WaitingToEnterRoom"] = matched[1]
                    elif matched := re.match(self.Time_SpawningPlayers_PATTERN, line):
                        temp["Time_SpawningPlayers"] = matched[1]
                        state = 2

                    if state == 2:
                        temp["Mode"] = mode
                        temp["EAC"] = hasEAC
                        data.append(temp)
                        temp = LogData(Datetime="", Mode="", EAC="", WorldName="", Region="", Time_WorldFetch="", Time_RoomInstantiate="", Time_InitializingVRCObjects="", Time_ProcessingSceneObjects="", Time_FixingMaterials="", Time_FinalizingScene="", Time_EnteringWorld="", Time_WaitingToEnterRoom="", Time_SpawningPlayers="")
                        state = 1

            self.datalist += data

    def output_to_csv(self, path: str):
        with open(path, encoding="utf_8_sig", mode="w", errors="backslashreplace", newline="") as f:
            if self.datalist:
                writer = csv.DictWriter(f, list(self.datalist[0].keys()))
                writer.writeheader()
                writer.writerows(self.datalist)

if __name__ == "__main__":
    print(f"VRC Log Data Collector v{LogDataCollector.VERSION}")
    print("Created by Sayamame(https://github.com/Sayamame-beans)")

    parser = argparse.ArgumentParser(description="This is an data collector tool from log files of VRChat.")
    parser.add_argument("path", type=str, help="Path where VRChat log files are located.")

    path = parser.parse_args().path
    if path[-1] == '\"':
        path = path[:-1]
    path = os.path.abspath(os.path.expanduser(os.path.expandvars(path)))

    if not os.path.exists(path):
        print(f"\"{path}\" does not exist.")
        exit(1)
    if not os.path.isdir(path):
        print(f"\"{path}\" is not directory.")
        exit(1)

    collector = LogDataCollector()
    print(f"Collect from \"{path}\".")
    try:
        collector.collect(path)
        collector.output_to_csv(path+"/LogData.csv")
        print("Completed!")
    except KeyboardInterrupt:
        print("Shutdown VRC Log Data Collecctor.")
    except Exception as e:
        print("Something error occured.")
        print(traceback.format_exc())