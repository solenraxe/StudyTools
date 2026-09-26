import pygame as pg
import os
from tkinter import filedialog as fd
import pyperclip
from datetime import date

import data

pg.init()
pg.font.init()

comicSans = pg.font.SysFont("Comic Sans MS", 18)
smallerText = pg.font.SysFont("Comic Sans MS", 16)
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

currentDate = date.today()
weekDay = weekDays[currentDate.isoweekday()-1]

monDay = currentDate.day - currentDate.isoweekday() + 1
monMonth = currentDate.month
monYear = currentDate.year
if monDay < 1:
    if monMonth != 1:
        monthDays = (date(currentDate.year, currentDate.month, 1) - date(currentDate.year, currentDate.month-1, 1)).days
        monMonth -= 1
        monDay = monthDays + monDay
    else:
        monYear -= 1
        monMonth = 12
        monDay = 31 + monDay
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

class Element():
    def __init__(self, rect, color = (255, 255, 255), hollow = 0):
        self.rect = rect
        self.color = color
        self.hollow = hollow

    def draw(self):
        pg.draw.rect(screen, self.color, self.rect, self.hollow)

class TimetableElement(Element):
    def __init__(self, rect, label, color = (255, 255, 255), font = smallerText):
        super().__init__(rect, color, 0) 
        self.label = label
        self.labelText = font.render(label, True, (0, 0, 0))
        self.xText = self.rect.x + self.rect.width//2 - self.labelText.get_width()//2
        self.yText = self.rect.y + self.rect.height//2 - self.labelText.get_height()//2

    def draw(self):
        pg.draw.rect(screen, self.color, self.rect, self.hollow)
        screen.blit(self.labelText, (self.xText, self.yText))

class Button():
    def __init__(self, x, y, width, height, text, onClick = None, font = comicSans):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.onClick = onClick
        self.font = font

    def draw(self):
        pg.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=5)
        textSurface = self.font.render(self.text, True, (255, 255, 255))
        textRect = textSurface.get_rect(center=self.rect.center)
        screen.blit(textSurface, textRect)

    def checkClick(self, pos):
        if self.rect.collidepoint(pos):
            self.onClick()

class DropDown(Button):
    def __init__(self, x, y, width, height, text, buttons):
        super().__init__(x, y, width, height, text, lambda: self.toggleButtons())
        self.buttons = buttons
        self.value = None
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
                buttonsList.append(button)
            self.buttonsVisible = True
        else:
            for i in range(len(buttonsList)-1, -1, -1):
                button = buttonsList[i]
                if hasattr(button, 'parent') and button.parent == self:
                    buttonsList.pop(i)
            self.buttonsVisible = False

elements = []

buttonsList = []
menuButtons = []
timeButtons = []
eventButtons = []

buttonsList.append(Button(20, 10, 150, 30, "Fullscreen", lambda: toggleFullscreen()))
menuButtons.append(Button(WIDTH//2 - 75, HEIGHT//2 - 50, 150, 30, "Timetable", lambda: launchTimetable()))
menuButtons.append(Button(WIDTH//2 - 75, HEIGHT//2, 150, 30, "To Do List", lambda: launchToDoList()))
menuButtons.append(Button(WIDTH//2 - 75, HEIGHT//2 + 50, 150, 30, "Quizz", lambda: launchQuizz()))
timeButtons.append(Button(180, 10, 150, 30, "Add Event", lambda: launchAddEvent()))
eventButtons.append(Button(180, 10, 100, 30, "Back", lambda: launchTimetable()))

timeSelection = DropDown(WIDTH//2 - 75, HEIGHT//2 - 15, 100, 30, "Time", [Button(0, 0, 75, 18, t) for t in times])
daySelection = DropDown(WIDTH//2 + 100, HEIGHT//2 - 15, 100, 30, "Day", [Button(0, 0, 75, 18, d) for d in weekDays])
eventButtons.append(timeSelection)
eventButtons.append(daySelection)

running = True

def mainMenu():
    global running
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button in buttonsList + menuButtons:
                    button.checkClick(event.pos)
    
    header = comicSans.render("Tools List:", True, (255, 255, 255))
    screen.blit(header, (WIDTH//2 - header.width//2, HEIGHT//2 - 100))
    
    for button in menuButtons:
        button.draw()

def timeTable():
    global running
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button in buttonsList + timeButtons:
                    button.checkClick(event.pos)

    for element in elements:
            element.draw()

    for i, day in enumerate(weekDays):
        weekText = smallerText.render(day, True, (255, 255, 255))
        screen.blit(weekText, (120 + 95 * i, 85))
        pg.draw.line(screen, (255, 255, 255), (90 + 95*i, 122), (90 + 95*i, 529), 2)
    pg.draw.line(screen, (255, 255, 255), (85 + 95*7, 122), (85 + 95*7, 529), 2)
    for i, time in enumerate(times):
        timeText = smallerText.render(time, True, (255, 255, 255))
        screen.blit(timeText, (50, 110 + 34*i))
        if i%2 == 0:
            pg.draw.line(screen, (255, 255, 255), (90, 110 + 34*i + txtH//2), (750, 110 + 34*i + txtH//2), 2)

    for button in timeButtons:
        button.draw()

def addEvent():
    global running
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button in buttonsList + eventButtons:
                    button.checkClick(event.pos)

    for button in eventButtons:
        button.draw()

def toDoList():
    global running
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button in buttonsList:
                    button.checkClick(event.pos)

def quizz():
    global running
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button in buttonsList:
                    button.checkClick(event.pos)

runningFunc = lambda: mainMenu()

def launchTimetable():
    global runningFunc
    timetableData = data.getTimetableData()
    for event in timetableData["Repeated"]:
        year, month, day = event["Added"]
        dDate = (date(year, month, day) - monDate).days % event["Repeat"]
        if 0 <= dDate < 7:
            eventRect = pg.Rect(90 + 95*dDate, 110 + txtH//2 + 34*(event["Time"] - 8), 95, 34*event["Duration"])
            eventObject = TimetableElement(eventRect, event["Label"], event["Color"])
            elements.append(eventObject)
    runningFunc = lambda: timeTable()

def launchAddEvent():
    global runningFunc
    runningFunc = lambda: addEvent()

def launchToDoList():
    global runningFunc
    runningFunc = lambda: toDoList()

def launchQuizz():
    global runningFunc
    runningFunc = lambda: quizz()

while running:
    screen.fill((0, 0, 0))

    pg.draw.rect(screen, (255, 255, 255), mainWindow, 2, border_radius=5)
    for button in buttonsList:
        button.draw()

    runningFunc()

    pg.display.flip()
    clock.tick(60)

pg.quit()