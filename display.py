from datetime import date

import data
import solui as ui

iconPath = data.resource_path("StudyTools.png")
ui.setupWindow("Study Tools", iconPath)

mainWindow = ui.Element((20, 50, ui.WIDTH - 40, ui.HEIGHT - 70), (255, 255, 255), 2, 5)

#constants
txtH = 23
weekDays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
times = [f"{i}h" for i in range(8, 21)]
colors = {
    "Red": [255, 0, 0],
    "Green": [0, 255, 0],
    "Blue": [0, 0, 255],
    "White": [255, 255, 255],
    "Cyan": [0, 255, 255],
    "Magenta": [255, 0, 255],
    "Yellow": [255, 255, 0]
}

def substractDays(oDate, n):
    newDay = oDate.day - n + 1
    newMonth = oDate.month
    newYear = oDate.year
    monthDays = 31
    if newMonth != 12:
        monthDays = (date(newYear, newMonth+1, 1) - date(newYear, newMonth, 1)).days
    if newDay < 1:
        if newMonth != 1:
            monthDays = (date(newYear, newMonth, 1) - date(newYear, newMonth-1, 1)).days
            newMonth -= 1
            newDay += monthDays
        else:
            newYear -= 1
            newMonth = 12
            newDay += 31
    elif newDay > monthDays:
        if newMonth != 12:
            newMonth += 1
            newDay -= monthDays
        else:
            newYear += 1
            newMonth = 1
            newDay -= monthDays
    return newDay, newMonth, newYear

currentDate = date.today()
weekDay = weekDays[currentDate.isoweekday()-1]

monDay, monMonth, monYear = substractDays(currentDate, currentDate.isoweekday())
permMonDate = date(monYear, monMonth, monDay)
monDate = date(monYear, monMonth, monDay)

scroll = 0

def printScreen():
    from PIL import Image
    img = Image.new('RGB', (ui.WIDTH, ui.HEIGHT), (0, 0, 0))
    for x in range(ui.WIDTH):
        for y in range(ui.HEIGHT):
            r, g, b, _ = ui.screen.get_at((x, y))
            img.putpixel((x, y), (r, g, b))
    img.show()

def changeMonDate(dir, ctx):
    global monDay, monMonth, monYear, monDate
    monDay, monMonth, monYear = substractDays(monDate, (-7+dir)*dir)
    monDate = date(monYear, monMonth, monDay)

    globals()[f"launch{ctx}"]()

class TimetableElement(ui.Element):
    def __init__(self, rect, label, elem, color = (255, 255, 255), font = ui.smallerText):
        super().__init__(rect, color)
        self.label = label
        self.labelText = font.render(label, True, (0, 0, 0))
        fontSize = 16
        while self.labelText.get_width() > rect.width - 20 or self.labelText.get_height() > rect.height - 4:
            fontSize -= 1
            font = ui.font.SysFont("ldfcomicsansbold", fontSize)
            self.labelText = font.render(label, True, (0, 0, 0))
        self.xText = self.rect.x + 10
        self.yText = self.rect.y + self.rect.height//2 - self.labelText.get_height()//2
        self.elem = elem
        self.clickable = True

    def draw(self):
        ui.draw.rect(ui.screen, self.color, self.rect, self.hollow)
        ui.draw.rect(ui.screen, (255, 255, 255), self.rect, 2)
        ui.screen.blit(self.labelText, (self.xText, self.yText))

    def checkClick(self, pos):
        if self.rect.collidepoint(pos):
            launchAddEvent(self.elem)

    def onFullScreen(self):
        self.xText = self.rect.x + 10
        self.yText = self.rect.y + self.rect.height//2 - self.labelText.get_height()//2

class ToDoElement(ui.Element):
    def __init__(self, coords, elem):
        super().__init__(coords)
        self.baseText = f"{elem["Label"]} [{elem["Date"][2]}/{elem["Date"][1]}]"
        self.text = ui.comicSans.render(self.baseText, True, (255, 255, 255))
        self.quantity = int(elem["Quantity"])
        self.progress = int(elem["Progress"])
        self.button = ui.Button((coords[0], coords[1], 50, 30), f"{self.progress}/{self.quantity}", lambda: self.increaseProgress())
        self.clickable = True
        self.elem = elem

    def increaseProgress(self):
        self.progress = (self.progress+1)%(self.quantity+1)
        self.button.text = f"{self.progress}/{self.quantity}"
        if self.progress == self.quantity:
            self.color = (0, 255, 0)
        else:
            self.color = (255, 255, 255)
        self.text = ui.comicSans.render(self.baseText, True, self.color)
        self.button.color = self.color
        data.progressTask(self.elem)

    def checkClick(self, pos):
        if self.button.rect.collidepoint(pos) and self.button.onClick:
            self.button.onClick()
        elif self.rect.collidepoint(pos):
            launchAddTask(self.elem)

    def draw(self):
        self.button.draw()
        ui.screen.blit(self.text, (self.rect.x + 60, self.rect.y))

    def onFullScreen(self):
        self.button = ui.Button((self.rect.x, self.rect.y, 50, 30), f"{self.progress}/{self.quantity}", lambda: self.increaseProgress(), color=self.color)

dateText = ui.Text((40, 60), f"{monDate}")
changeDateNeg = ui.Button((265, 10, 50, 30), "<-", lambda: changeMonDate(-1, "Timetable"))
changeDatePos = ui.Button((325, 10, 50, 30), "->", lambda: changeMonDate(1, "Timetable"))

menuElements = []
menuElements.append(ui.Button((ui.WIDTH//2 - 75, ui.HEIGHT//2 - 25, 150, 30), "Timetable", lambda: launchTimetable()))
menuElements.append(ui.Button((ui.WIDTH//2 - 75, ui.HEIGHT//2 + 25, 150, 30), "To Do List", lambda: launchToDoList()))
menuElements.append(ui.Text((ui.WIDTH//2, ui.HEIGHT//2-100, 0, 30), "Tools List:"))
ui.createTab("Menu", None, menuElements)

timeElements = []
timeElements.append(dateText)
timeElements.append(changeDateNeg)
timeElements.append(changeDatePos)
timeElements.append(ui.Button((385, 10, 150, 30), "Add Event", lambda: launchAddEvent()))
timeElements.append(ui.Button((545, 10, 75, 30), "Save", lambda: ui.defferedFuncs.append(lambda: printScreen())))
for i, day in enumerate(weekDays):
    timeElements.append(ui.Text((120+95*i, 85), day))
    timeElements.append(ui.Element((90+95*i, 123, 2, 407)))
timeElements.append(ui.Element((88+95*7, 123, 2, 407)))
for i, time in enumerate(times):
    timeElements.append(ui.Text((50, 110+34*i), time))
    if i%2 == 0:
        timeElements.append(ui.Element((90, 98+34*i+txtH, 665, 2)))
def timeTable():
    dateText.text = f"{monDate}"
ui.createTab("Timetable", lambda: timeTable(), timeElements)

eventElements = []
eventElements.append(ui.Button((265, 10, 100, 30), "Back", lambda: launchTimetable()))
timeSelection = ui.Selector((ui.WIDTH//2 - 175, ui.HEIGHT//2 - 45, 150, 30), "Time: ", [t for t in times])
durationSelection = ui.Selector((ui.WIDTH//2 + 25, ui.HEIGHT//2 - 45, 150, 30), "Duration: ", [f"{d/2}h" for d in range(1, 11)])
repeatSelection = ui.Selector((ui.WIDTH//2 - 75, ui.HEIGHT//2 + 75, 165, 30), "Repeat every: ", [t for t in range(30)])
repeatUnit = ui.Selector((ui.WIDTH//2 + 100, ui.HEIGHT//2 + 75, 75, 30), "", ["days", "weeks", "months", "years"])
possibleDays = (date(currentDate.year, currentDate.month+1, 1) - date(currentDate.year, currentDate.month, 1)).days
daySelection = ui.Selector((ui.WIDTH//2 - 65, ui.HEIGHT//2 + 15, 30, 30), "", [d for d in range(1, possibleDays+1)])
monthSelection = ui.Selector((ui.WIDTH//2 - 15, ui.HEIGHT//2 + 15, 30, 30), "", [m for m in range(1, 13)])
yearSelection = ui.Selector((ui.WIDTH//2 + 35, ui.HEIGHT//2 + 15, 50, 30), "", [y for y in range(2026, 2101)])
nameSelection = ui.TextInput((ui.WIDTH//2 - 75, ui.HEIGHT//2 - 105, 150, 30), "Event Name")
colorSelection = ui.Selector((ui.WIDTH//2 - 250, ui.HEIGHT//2 + 75, 150, 30), "Color: ", [c for c in colors])
quantitySelection = ui.Selector((ui.WIDTH//2 - 75, ui.HEIGHT//2 - 45, 150, 30), "Quantity: ", [i for i in range(1, 20)])
eventElements.append(timeSelection)
eventElements.append(durationSelection)
eventElements.append(daySelection)
eventElements.append(monthSelection)
eventElements.append(yearSelection)
eventElements.append(nameSelection)
eventElements.append(colorSelection)
eventElements.append(repeatSelection)
eventElements.append(repeatUnit)
def addEvent(context):
    for event in ui.events:
        processed = False
        if ui.focusedElement != None: processed = ui.focusedElement.handleEvents(event)
        if processed: continue
        if event.type == ui.KEYDOWN:
            if event.key == ui.K_RETURN:
                if context != "New":
                    data.deleteEvent(context)
                eventDate = [yearSelection.value, monthSelection.value, daySelection.value]
                eventDuration = float(durationSelection.value[:-1])
                eventTime = float(timeSelection.value[:-1])
                eventName = nameSelection.text
                eventColor = colors[colorSelection.value]
                eventCategory = "Temporary"
                eventRepeat = 0
                if repeatSelection.value != 0:
                    eventRepeat = repeatSelection.value * (repeatUnit.index*6+1)
                    eventCategory = "Repeated"
                data.addEvent(eventCategory, eventName, eventTime, eventDuration, eventDate, eventColor, eventRepeat)
                launchTimetable()
            elif event.key == ui.K_TAB:
                launchTimetable()
            elif event.key == ui.K_BACKSPACE:
                if context != "New":
                    data.deleteEvent(context)
                launchTimetable()
ui.createTab("AddEvent", lambda: addEvent("New"), eventElements)

toDoElements = []
toDoElements.append(dateText)
toDoElements.append(changeDateNeg)
toDoElements.append(changeDatePos)
toDoElements.append(ui.Text((ui.WIDTH//2, 100, 0, 30), "To do"))
toDoElements.append(ui.Element((200, 130, 400, 400), hollow=2, radius=5))
toDoElements.append(ui.Button((385, 10, 150, 30), "Add Task", lambda: launchAddTask()))
def toDoList():
    global scroll
    for event in ui.events:
        if event.type == ui.MOUSEWHEEL:
            scroll = max(0, scroll - 1 * (event.y//1))
            launchToDoList(scroll)

    dateText.text = f"{monDate}"
ui.createTab("ToDoList", lambda: toDoList(), toDoElements)

taskElements = []
taskElements.append(nameSelection)
taskElements.append(daySelection)
taskElements.append(monthSelection)
taskElements.append(yearSelection)
taskElements.append(quantitySelection)
taskElements.append(ui.Button((265, 10, 100, 30), "Back", lambda: launchToDoList()))
def addTask(ctx):
    for event in ui.events:
        processed = False
        if ui.focusedElement != None: processed = ui.focusedElement.handleEvents(event)
        if processed: continue

        elif event.type == ui.KEYDOWN:
            if event.key == ui.K_RETURN:
                if ctx != "New":
                    data.deleteTask(ctx)
                taskName = nameSelection.text
                taskDate = [yearSelection.value, monthSelection.value, daySelection.value]
                taskQuant = quantitySelection.value
                data.addTask(taskName, taskDate, taskQuant)
                launchToDoList()
            elif event.key == ui.K_BACKSPACE:
                if ctx != "New":
                    data.deleteTask(ctx)
                launchToDoList()
            elif event.key == ui.K_TAB:
                launchToDoList()
ui.createTab("AddTask", lambda: addTask("New"), taskElements)

ui.globalElements.append(ui.Button((20, 10, 150, 30), "Fullscreen", lambda: ui.toggleFullscreen()))
ui.globalElements.append(ui.Button((180, 10, 75, 30), "Menu", lambda: launchMenu()))
ui.globalElements.append(mainWindow)

def launchMenu():
    ui.changeTab("Menu")

def launchTimetable():
    changeDateNeg.onClick = lambda: changeMonDate(-1, "Timetable")
    changeDatePos.onClick = lambda: changeMonDate(1, "Timetable")
    timetableData = data.getData("Timetable")
    ui.changeTab("Timetable")
    for event in timetableData["Repeated"]:
        year, month, day = event["Date"]
        dDate = (date(year, month, day) - monDate).days % event["Repeat"]
        while 0 <= dDate < 7:
            eventRect = ui.Rect(90 + 95*dDate, 110 + txtH//2 + 34*(event["Time"] - 8), 95, 34*event["Duration"])
            eventObject = TimetableElement(eventRect, event["Label"], event, event["Color"])
            ui.tabElements.append(eventObject)
            dDate += event["Repeat"]
    for event in timetableData["Temporary"]:
        year, month, day = event["Date"]
        dDate = (date(year, month, day) - monDate).days
        if dDate < 0 and (date(year, month, day) - permMonDate).days < 0:
            data.deleteTempEvent(event)
        elif dDate < 7:
            eventRect = ui.Rect(90 + 95*dDate, 110 + txtH//2 + 34*(event["Time"] - 8), 95, 34*event["Duration"])
            eventObject = TimetableElement(eventRect, event["Label"], event, event["Color"])
            ui.tabElements.append(eventObject)
    ui.toggleFullscreen("stationary")

def restituteEventFromContext(context):
    year, month, day = context["Date"]
    yearSelection.index = int(year) - 2026; yearSelection.update();
    monthSelection.index = int(month) - 1; monthSelection.update();
    daySelection.index = int(day) - 1; daySelection.update();
    nameSelection.value = context["Label"]; nameSelection.update();
    durationSelection.index = int(context["Duration"]*2) - 1; durationSelection.update();
    timeSelection.index = int(context["Time"]) - 8; timeSelection.update();
    repeatSelection.index = int(context["Repeat"]); repeatSelection.update();
    color = next((c for c, v in colors.items() if v == context["Color"]), "Red")
    colorSelection.index = next(i for i, c in enumerate(colors) if c == color); colorSelection.update();

def launchAddEvent(context = "New"):
    if context != "New":
        restituteEventFromContext(context)

    ui.tabs["AddEvent"]["function"] = lambda: addEvent(context)
    ui.changeTab("AddEvent")

def launchToDoList(skip = 0):
    changeDateNeg.onClick = lambda: changeMonDate(-1, "ToDoList")
    changeDatePos.onClick = lambda: changeMonDate(1, "ToDoList")
    toDoData = data.getData("To Do List")
    ui.changeTab("ToDoList")
    acceptedTasks = []
    for task in toDoData:
        year, month, day = task["Date"]
        dDate = (date(year, month, day) - monDate).days
        if (dDate < 0 and (date(year, month, day) - permMonDate).days < 0) or task["Progress"] == task["Quantity"]:
            data.deleteTask(task)
        elif 0 <= dDate < 14:
            acceptedTasks.append(task)
    skip = min(skip, len(acceptedTasks)-8)
    if len(acceptedTasks) > 9:
        scrollBar = ui.Element((588, 137+386/(len(acceptedTasks)+1)*skip, 5, 386*9/(len(acceptedTasks)+1)), radius = 5)
        ui.tabElements.append(scrollBar)
    taskCounter = 0
    for i, task in enumerate(acceptedTasks):
        if (len(acceptedTasks) > 9 and skip > 0) or taskCounter > 8: skip -= 1; continue
        taskObj = ToDoElement((220, 150+42*taskCounter, 360, 50), task)
        ui.tabElements.append(taskObj)
        taskCounter += 1
    ui.toggleFullscreen("stationary")

def restituteTaskFromContext(ctx):
    year, month, day = ctx["Date"]
    yearSelection.index = int(year) - 2026; yearSelection.update();
    monthSelection.index = int(month) - 1; monthSelection.update();
    daySelection.index = int(day) - 1; daySelection.update();
    nameSelection.value = ctx["Label"]; nameSelection.update();
    quantitySelection.value = ctx["Quantity"]; quantitySelection.update();

def launchAddTask(ctx = "New"):
    if ctx != "New":
        restituteTaskFromContext(ctx)
    ui.tabs["AddTask"]["function"] = lambda: addTask(ctx)
    ui.changeTab("AddTask")

ui.changeTab("Menu")
ui.launch()
