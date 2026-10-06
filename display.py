from datetime import date
import pygame as pg

import data
import solui as ui

pg.init()
pg.font.init()

comicSans = pg.font.SysFont("ldfcomicsansbold", 18)
smallerText = pg.font.SysFont("ldfcomicsansbold", 16)
dropDownText = pg.font.SysFont("ldfcomicsansbold", 10)

displayInfo = pg.display.Info()
WIDTH, HEIGHT = 800, 600

screen = pg.display.set_mode((WIDTH, HEIGHT))
ui.screen = screen
clock = pg.time.Clock()

icon = pg.image.load(data.resource_path("StudyTools.png")).convert_alpha()
pg.display.set_caption("Study Tools")
pg.display.set_icon(icon)

mainWindow = pg.Rect(20, 50, WIDTH - 40, HEIGHT - 70)

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
monDate = date(monYear, monMonth, monDay)

def toggleFullscreen():
    if pg.display.get_window_size() == (WIDTH, HEIGHT):
        pg.display.set_mode((displayInfo.current_w, displayInfo.current_h), pg.FULLSCREEN)
        mainWindow.width = displayInfo.current_w - 40
        mainWindow.height = displayInfo.current_h - 70
    else:
        pg.display.set_mode((WIDTH, HEIGHT))
        mainWindow.width = WIDTH - 40
        mainWindow.height = HEIGHT - 70

def changeMonDate(dir, ctx):
    global monDay, monMonth, monYear, monDate
    monDay, monMonth, monYear = substractDays(monDate, (-7+dir)*dir)
    monDate = date(monYear, monMonth, monDay)

    globals()[f"launch{ctx}"]()

class TimetableElement(ui.Element):
    def __init__(self, rect, label, elem, color = (255, 255, 255), font = smallerText):
        super().__init__(rect, color)
        self.label = label
        self.labelText = font.render(label, True, (0, 0, 0))
        fontSize = 16
        while self.labelText.get_width() > rect.width - 20 or self.labelText.get_height() > rect.height - 4:
            fontSize -= 1
            font = pg.font.SysFont("ldfcomicsansbold", fontSize)
            self.labelText = font.render(label, True, (0, 0, 0))
        self.xText = self.rect.x + 10
        self.yText = self.rect.y + self.rect.height//2 - self.labelText.get_height()//2
        self.elem = elem
        self.clickable = True

    def draw(self):
        pg.draw.rect(screen, self.color, self.rect, self.hollow)
        pg.draw.rect(screen, (255, 255, 255), self.rect, 2)
        screen.blit(self.labelText, (self.xText, self.yText))

    def checkClick(self, pos):
        if self.rect.collidepoint(pos):
            self.onClick()

    def onClick(self):
        launchAddEvent(self.elem)

class ToDoElement(ui.Element):
    def __init__(self, coords, text, progress, quantity):
        super().__init__(coords)
        self.text = comicSans.render(text, True, (255, 255, 255))
        self.quantity = int(quantity)
        self.progress = int(progress)
        self.button = ui.Button((coords[0], coords[1], 50, 30), f"{progress}/{quantity}", lambda: self.increaseProgress())
        self.clickable = True

    def increaseProgress(self):
        self.progress = (self.progress+1)%(self.quantity+1)
        self.button.text = f"{self.progress}/{self.quantity}"
        if self.progress == self.quantity:
            pass

    def checkClick(self, pos):
        if self.button.rect.collidepoint(pos):
            self.button.onClick()
        #elif self.rect.collidepoint(pos):
            #self.onClick()

    def draw(self):
        self.button.draw()
        screen.blit(self.text, (self.rect.x + 60, self.rect.y))

globalElements = []
menuElements = []
timeElements = []
eventElements = []
toDoElements = []

globalElements.append(ui.Button((20, 10, 150, 30), "Fullscreen", lambda: toggleFullscreen()))
globalElements.append(ui.Button((180, 10, 75, 30), "Menu", lambda: launchMenu()))
menuElements.append(ui.Button((WIDTH//2 - 75, HEIGHT//2 - 50, 150, 30), "Timetable", lambda: launchTimetable()))
menuElements.append(ui.Button((WIDTH//2 - 75, HEIGHT//2, 150, 30), "To Do List", lambda: launchToDoList()))
menuElements.append(ui.Button((WIDTH//2 - 75, HEIGHT//2 + 50, 150, 30), "Quizz", lambda: launchQuizz()))
launchAddButton = ui.Button((385, 10, 150, 30), "Add Event", lambda: launchAddEvent())
changeDateNeg = ui.Button((265, 10, 50, 30), "<-", lambda: changeMonDate(-1, "Timetable"))
changeDatePos = ui.Button((325, 10, 50, 30), "->", lambda: changeMonDate(1, "Timetable"))
eventElements.append(ui.Button((265, 10, 100, 30), "Back", lambda: launchTimetable()))

timeSelection = ui.Selector((WIDTH//2 - 175, HEIGHT//2 - 45, 150, 30), "Time: ", [t for t in times])
durationSelection = ui.Selector((WIDTH//2 + 25, HEIGHT//2 - 45, 150, 30), "Duration: ", [f"{d/2}h" for d in range(1, 11)])
repeatSelection = ui.Selector((WIDTH//2 - 75, HEIGHT//2 + 75, 165, 30), "Repeat every: ", [t for t in range(30)])
repeatUnit = ui.Selector((WIDTH//2 + 100, HEIGHT//2 + 75, 75, 30), "", ["days", "weeks", "months", "years"])

possibleDays = monthDays = (date(currentDate.year, currentDate.month+1, 1) - date(currentDate.year, currentDate.month, 1)).days
daySelection = ui.Selector((WIDTH//2 - 65, HEIGHT//2 + 15, 30, 30), "", [d for d in range(1, possibleDays+1)])
monthSelection = ui.Selector((WIDTH//2 - 15, HEIGHT//2 + 15, 30, 30), "", [m for m in range(1, 13)])
yearSelection = ui.Selector((WIDTH//2 + 35, HEIGHT//2 + 15, 50, 30), "", [y for y in range(2026, 2101)])

nameSelection = ui.TextInput((WIDTH//2 - 75, HEIGHT//2 - 105, 150, 30), "Event Name")
colorSelection = ui.Selector((WIDTH//2 - 250, HEIGHT//2 + 75, 150, 30), "Color: ", [c for c in colors])

eventElements.append(timeSelection)
eventElements.append(durationSelection)
eventElements.append(daySelection)
eventElements.append(monthSelection)
eventElements.append(yearSelection)
eventElements.append(nameSelection)
eventElements.append(colorSelection)
eventElements.append(repeatSelection)
eventElements.append(repeatUnit)

toDoElements.append(changeDateNeg)
toDoElements.append(changeDatePos)

running = True

def mainMenu():
    global running
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                for element in globalElements + menuElements:
                    if hasattr(element, "clickable"): element.checkClick(event.pos)

    header = comicSans.render("Tools List:", True, (255, 255, 255))
    screen.blit(header, (WIDTH//2 - header.width//2, HEIGHT//2 - 100))

    for element in menuElements + globalElements:
        element.draw()

def timeTable():
    global running
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                for element in timeElements + globalElements:
                    if hasattr(element, "clickable"): element.checkClick(event.pos)

    for i, day in enumerate(weekDays):
        weekText = smallerText.render(day, True, (255, 255, 255))
        screen.blit(weekText, (120 + 95 * i, 85))
        pg.draw.line(screen, (255, 255, 255), (90 + 95*i, 122), (90 + 95*i, 529), 2)
    pg.draw.line(screen, (255, 255, 255), (90 + 95*7, 122), (90 + 95*7, 529), 2)
    for i, time in enumerate(times):
        timeText = smallerText.render(time, True, (255, 255, 255))
        screen.blit(timeText, (50, 110 + 34*i))
        if i%2 == 0:
            pg.draw.line(screen, (255, 255, 255), (90, 110 + 34*i + txtH//2), (755, 110 + 34*i + txtH//2), 2)

    screen.blit(comicSans.render(f"{monDate}", True, (255, 255, 255)), (40, 60))

    for element in timeElements + globalElements:
        element.draw()

def addEvent(context):
    global running
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            continue

        processed = False
        if ui.focusedElement != None: processed = ui.focusedElement.handleEvents(event)
        if processed: continue

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for element in eventElements + globalElements:
                if hasattr(element, "clickable"): element.checkClick(event.pos)
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                if context != "New":
                    data.deleteEvent(context)
                eventDate = [yearSelection.value, monthSelection.value, daySelection.value]
                eventDuration = float(durationSelection.value[:-1])
                eventTime = float(timeSelection.value[:-1])
                eventName = nameSelection.text
                eventColor = colors[colorSelection.value]
                eventCategory = "Temporary"
                eventRepeat = None
                if repeatSelection.value != 0:
                    eventRepeat = repeatSelection.value * (repeatUnit.index+1)
                    eventCategory = "Repeated"
                data.addEvent(eventCategory, eventName, eventTime, eventDuration, eventDate, eventColor, eventRepeat)
                launchTimetable()
            elif event.key == pg.K_TAB:
                launchTimetable()
            elif event.key == pg.K_BACKSPACE:
                if context != "New":
                    data.deleteEvent(context)
                launchTimetable()

    for element in eventElements + globalElements:
        element.draw()

def toDoList():
    global running
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                for element in toDoElements + globalElements:
                    if hasattr(element, "clickable"): element.checkClick(event.pos)

    screen.blit(comicSans.render(f"{monDate}", True, (255, 255, 255)), (40, 60))

    header = comicSans.render("To do:", True, (255, 255, 255))
    screen.blit(header, (WIDTH//2 - header.get_width()//2, 100))

    listRect = pg.Rect(200, 130, 400, 400)
    pg.draw.rect(screen, (255, 255, 255), listRect, 2, 5)

    for element in toDoElements + globalElements:
        element.draw()

def quizz():
    global running
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button in globalElements:
                    button.checkClick(event.pos)

runningFunc = lambda: mainMenu()

def launchMenu():
    global runningFunc
    runningFunc = lambda: mainMenu()

def launchTimetable():
    global runningFunc, timeElements
    timeElements = [launchAddButton, changeDateNeg, changeDatePos]
    timetableData = data.getData("Timetable")
    for event in timetableData["Repeated"]:
        year, month, day = event["Date"]
        dDate = (date(year, month, day) - monDate).days % event["Repeat"]
        while 0 <= dDate < 7:
            eventRect = pg.Rect(90 + 95*dDate, 110 + txtH//2 + 34*(event["Time"] - 8), 95, 34*event["Duration"])
            eventObject = TimetableElement(eventRect, event["Label"], event, event["Color"])
            timeElements.append(eventObject)
            dDate += event["Repeat"]
    for event in timetableData["Temporary"]:
        year, month, day = event["Date"]
        dDate = (date(year, month, day) - monDate).days
        if dDate < 0:
            data.deleteTempEvent(event)
        elif dDate < 7:
            eventRect = pg.Rect(90 + 95*dDate, 110 + txtH//2 + 34*(event["Time"] - 8), 95, 34*event["Duration"])
            eventObject = TimetableElement(eventRect, event["Label"], event, event["Color"])
            timeElements.append(eventObject)

    runningFunc = lambda: timeTable()

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
    global runningFunc
    if context != "New":
        restituteEventFromContext(context)

    runningFunc = lambda: addEvent(context)

def launchToDoList():
    global runningFunc
    runningFunc = lambda: toDoList()
    changeDateNeg.onClick = lambda: changeMonDate(-1, "ToDoList")
    changeDatePos.onClick = lambda: changeMonDate(1, "ToDoList")

    toDoData = data.getData("To Do List")
    taskCounter = 0
    for task in toDoData:
        year, month, day = task["Date"]
        dDate = (date(year, month, day) - monDate).days
        if dDate < 0 or task["Progress"] == task["Quantity"]:
            data.deleteTask(task)
        elif dDate < 7:
            taskObj = ToDoElement((220, 150+60*taskCounter, 360, 50), f"{task["Label"]} ({day}/{month}/{year})", task["Progress"], task["Quantity"])
            toDoElements.append(taskObj)
            taskCounter += 1

def launchQuizz():
    global runningFunc
    runningFunc = lambda: quizz()

while running:
    screen.fill((0, 0, 0))
    pg.draw.rect(screen, (255, 255, 255), mainWindow, 2, border_radius=5)

    runningFunc()

    pg.display.flip()
    clock.tick(60)

pg.quit()
