from tkinter import filedialog as fd
from datetime import date
import pygame as pg
import os
import pyperclip

import data

pg.init()
pg.font.init()

comicSans = pg.font.SysFont("Comic Sans MS", 18)
smallerText = pg.font.SysFont("Comic Sans MS", 15)
dropDownText = pg.font.SysFont("Comic Sans MS", 10)

displayInfo = pg.display.Info()
WIDTH, HEIGHT = 800, 600

screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

#icon = pg.image.load("SolPy.png")
pg.display.set_caption("Study Tools")
#pg.display.set_icon(icon)

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

def changeMonDate(dir):
    global monDay, monMonth, monYear, monDate
    monDay, monMonth, monYear = substractDays(monDate, (-7+dir)*dir)
    monDate = date(monYear, monMonth, monDay)

    launchTimetable()

class Element:
    def __init__(self, coords, color = (255, 255, 255), hollow = 0, radius = 0):
        self.rect = pg.Rect(coords[0], coords[1], coords[2], coords[3])
        self.color = color
        self.hollow = hollow
        self.radius = radius

    def draw(self):
        pg.draw.rect(screen, self.color, self.rect, self.hollow, self.radius)

class Button(Element):
    def __init__(self, coords, text, onClick = None, font = comicSans, color = (255, 255, 255)):
        super().__init__(coords, color, 2, 5)
        self.text = text
        self.onClick = onClick
        self.font = font
        self.clickable = True

    def draw(self):
        super().draw()
        textSurface = self.font.render(self.text, True, self.color)
        textRect = textSurface.get_rect(center=self.rect.center)
        screen.blit(textSurface, textRect)

    def checkClick(self, pos):
        if self.rect.collidepoint(pos):
            self.onClick()

class DropDown(Button):
    def __init__(self, coords, text, buttons):
        super().__init__(coords, text, lambda: self.toggleButtons())
        self.buttons = buttons
        self.value = buttons[0].text
        self.buttonsVisible = False

        for button in self.buttons:
            button.parent = self
            button.font = dropDownText
            button.onClick = lambda v = button.text: self.setValue(v)

    def setValue(self, value):
        self.value = value
        self.text = value
        self.toggleButtons()

    def toggleButtons(self):
        if not self.buttonsVisible:
            for i, button in enumerate(self.buttons):
                button.rect.x = self.rect.x + self.rect.width//2 - button.rect.width//2
                button.rect.y = self.rect.y + 32 + 20*i + self.rect.height//2 - button.rect.height//2
                globalElements.append(button)
            self.buttonsVisible = True
        else:
            for i in range(len(globalElements)-1, -1, -1):
                button = globalElements[i]
                if hasattr(button, 'parent') and button.parent == self:
                    globalElements.pop(i)
            self.buttonsVisible = False

class Focusable(Button):
    def __init__(self, coords, text):
        super().__init__(coords, text, lambda e = self: setFocus(e))

class Selector(Focusable):
    def __init__(self, coords, text, options):
        super().__init__(coords, f"{text}{options[0]}")
        self.baseText = text
        self.options = options
        self.index = 0
        self.value = options[0]

    def update(self):
        self.value = self.options[self.index]
        self.text = f"{self.baseText}{self.value}"

    def changeOption(self, dir):
        self.index = (self.index + 1*dir) % len(self.options)
        self.update()

    def handleEvents(self, event):
        processed = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                self.changeOption(1)
                processed = True
            elif event.key == pg.K_DOWN:
                self.changeOption(-1)
                processed = True
        return processed

class TextInput(Focusable):
    def __init__(self, coords, text):
        super().__init__(coords, text)
        self.value = ""

    def update(self):
        self.text = self.value

    def handleEvents(self, event):
        processed = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE:
                self.value = self.value[:-1]
                processed = True
            elif event.unicode:
                self.value += event.unicode
                processed = True
            self.update()
        return processed

class TimetableElement(Element):
    def __init__(self, rect, label, elem, color = (255, 255, 255), font = smallerText):
        super().__init__(rect, color)
        self.label = label
        self.labelText = font.render(label, True, (0, 0, 0))
        self.xText = self.rect.x + self.rect.width//2 - self.labelText.get_width()//2
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

focusedElement = None
def setFocus(elem):
    global focusedElement
    if focusedElement != elem:
        if focusedElement != None:
            focusedElement.color = (255, 255, 255)
        focusedElement = elem
        elem.color = (255, 0, 0)
    else:
        focusedElement = None
        elem.color = (255, 255, 255)

globalElements = []
menuElements = []
timeElements = []
eventElements = []

globalElements.append(Button((20, 10, 150, 30), "Fullscreen", lambda: toggleFullscreen()))
menuElements.append(Button((WIDTH//2 - 75, HEIGHT//2 - 50, 150, 30), "Timetable", lambda: launchTimetable()))
menuElements.append(Button((WIDTH//2 - 75, HEIGHT//2, 150, 30), "To Do List", lambda: launchToDoList()))
menuElements.append(Button((WIDTH//2 - 75, HEIGHT//2 + 50, 150, 30), "Quizz", lambda: launchQuizz()))
launchAddButton = Button((180, 10, 150, 30), "Add Event", lambda: launchAddEvent())
changeDateNeg = Button((340, 10, 50, 30), "<-", lambda: changeMonDate(-1))
changeDatePos = Button((400, 10, 50, 30), "->", lambda: changeMonDate(1))
eventElements.append(Button((180, 10, 100, 30), "Back", lambda: launchTimetable()))

timeSelection = Selector((WIDTH//2 - 175, HEIGHT//2 - 45, 150, 30), "Time: ", [t for t in times])
durationSelection = Selector((WIDTH//2 + 25, HEIGHT//2 - 45, 150, 30), "Duration: ", [f"{d/2}h" for d in range(1, 11)])
repeatSelection = Selector((WIDTH//2 - 75, HEIGHT//2 + 75, 165, 30), "Repeat every: ", [t for t in range(30)])
repeatUnit = Selector((WIDTH//2 + 100, HEIGHT//2 + 75, 75, 30), "", ["days", "weeks", "months", "years"])

possibleDays = monthDays = (date(currentDate.year, currentDate.month+1, 1) - date(currentDate.year, currentDate.month, 1)).days
daySelection = Selector((WIDTH//2 - 65, HEIGHT//2 + 15, 30, 30), "", [d for d in range(1, possibleDays+1)])
monthSelection = Selector((WIDTH//2 - 15, HEIGHT//2 + 15, 30, 30), "", [m for m in range(1, 13)])
yearSelection = Selector((WIDTH//2 + 35, HEIGHT//2 + 15, 50, 30), "", [y for y in range(2026, 2101)])

nameSelection = TextInput((WIDTH//2 - 75, HEIGHT//2 - 105, 150, 30), "Event Name")
colorSelection = Selector((WIDTH//2 - 250, HEIGHT//2 + 75, 150, 30), "Color: ", [c for c in colors])

eventElements.append(timeSelection)
eventElements.append(durationSelection)
eventElements.append(daySelection)
eventElements.append(monthSelection)
eventElements.append(yearSelection)
eventElements.append(nameSelection)
eventElements.append(colorSelection)
eventElements.append(repeatSelection)
eventElements.append(repeatUnit)

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
        if focusedElement != None: processed = focusedElement.handleEvents(event)
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
                for button in globalElements:
                    button.checkClick(event.pos)

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

def launchTimetable():
    global runningFunc, timeElements
    timeElements = [launchAddButton, changeDateNeg, changeDatePos]
    timetableData = data.getTimetableData()
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

def launchQuizz():
    global runningFunc
    runningFunc = lambda: quizz()

while running:
    screen.fill((0, 0, 0))

    pg.draw.rect(screen, (255, 255, 255), mainWindow, 2, border_radius=5)
    for button in globalElements:
        button.draw()

    runningFunc()

    pg.display.flip()
    clock.tick(60)

pg.quit()
