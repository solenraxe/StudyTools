import json
import sys, os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_save_path():
    appdata = os.getenv("APPDATA")
    save_dir = os.path.join(appdata, "StudyTools")
    os.makedirs(save_dir, exist_ok=True)
    return os.path.join(save_dir, "data.json")

save_path = get_save_path()
if not os.path.exists(save_path):
    with open(save_path, 'w') as f:
        with open(resource_path('data.json'), 'r') as default_f:
            f.write(default_f.read())

data = {}
with open(save_path, 'r') as f:
    data = json.load(f)

def getTimetableData():
    return data["Timetable"].copy()

def deleteTempEvent(event):
    for i in range(len(data["Timetable"]["Temporary"]) - 1, -1, -1):
        ev = data["Timetable"]["Temporary"][i]
        if ev == event:
            data["Timetable"]["Temporary"].pop(i)

    with open(save_path, 'w') as f:
            json.dump(data, f, indent=4)