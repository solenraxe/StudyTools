import sys, os
import json

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_save_path():
    data_dir = os.path.expanduser("~/.local/share")
    save_dir = os.path.join(data_dir, "StudyTools")
    os.makedirs(save_dir, exist_ok=True)
    return os.path.join(save_dir, "data.json")

save_path = get_save_path()
if not os.path.exists(save_path):
    with open(save_path, 'w') as f, open(resource_path('data.json'), 'r') as default_f:
        f.write(default_f.read())

data = {}
with open(save_path, 'r') as f:
    data = json.load(f)

def getData(ctx):
    return data[ctx].copy()

def addEvent(category, label, time, duration, date, color, repeat = 0):
    event = {"Label": label, "Time": time, "Duration": duration, "Color": color, "Date": date, "Repeat": repeat}
    data["Timetable"][category].append(event)

    save()

def deleteEvent(event):
    if "Repeat" in event and event["Repeat"] != 0:
        deleteRepeatedEvent(event)
    else:
        deleteTempEvent(event)
    save()

def deleteRepeatedEvent(event):
    for i in range(len(data["Timetable"]["Repeated"]) - 1, -1, -1):
        ev = data["Timetable"]["Repeated"][i]
        if ev == event:
            data["Timetable"]["Repeated"].pop(i)

def deleteTempEvent(event):
    for i in range(len(data["Timetable"]["Temporary"]) - 1, -1, -1):
        ev = data["Timetable"]["Temporary"][i]
        if ev == event:
            data["Timetable"]["Temporary"].pop(i)

def addTask(label, date, quantity):
    task = {"Label": label, "Date": date, "Progress": 0, "Quantity": quantity}
    data["To Do List"].append(task)

    save()

def progressTask(task):
    for i, ts in enumerate(data["To Do List"]):
        if ts == task:
            data["To Do List"][i]["Progress"] = (data["To Do List"][i]["Progress"]+1) % (task["Quantity"]+1)
    save()

def deleteTask(task):
    for i in range(len(data["To Do List"])-1, -1, -1):
        ts = data["To Do List"][i]
        if ts == task:
            data["To Do List"].pop(i)
    save()

def save():
    with open(save_path, "w") as f:
        json.dump(data, f, indent=2)
