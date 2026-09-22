import pygame as pg
import os
from tkinter import filedialog as fd
import pyperclip

import data

pg.init()
pg.font.init()

comicSans = pg.font.SysFont("Comic Sans MS", 18)

displayInfo = pg.display.Info()
WIDTH, HEIGHT = 800, 600

screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

#icon = pg.image.load("SolPy.png")
pg.display.set_caption("Study Tools")
#pg.display.set_icon(icon)

mainWindow = pg.Rect(20, 50, WIDTH - 40, HEIGHT - 70)

def toggleFullscreen():
    if pg.display.get_window_size() == (WIDTH, HEIGHT):
        pg.display.set_mode((displayInfo.current_w, displayInfo.current_h), pg.FULLSCREEN)
        mainWindow.width = displayInfo.current_w - 40
        mainWindow.height = displayInfo.current_h - 70
    else:
        pg.display.set_mode((WIDTH, HEIGHT))
        mainWindow.width = WIDTH - 40
        mainWindow.height = HEIGHT - 70

class Button():
    def __init__(self, x, y, width, height, text, onClick):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.onClick = onClick

    def draw(self):
        pg.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=5)
        textSurface = comicSans.render(self.text, True, (255, 255, 255))
        textRect = textSurface.get_rect(center=self.rect.center)
        screen.blit(textSurface, textRect)

    def checkClick(self, pos):
        if self.rect.collidepoint(pos):
            self.onClick()

buttonsList = []
menuButtons = []

buttonsList.append(Button(20, 10, 150, 30, "Fullscreen (F11)", lambda: toggleFullscreen()))
menuButtons.append(Button(WIDTH//2 - 75, HEIGHT//2 - 50, 150, 30, "Timetable", lambda: launchTimetable()))
menuButtons.append(Button(WIDTH//2 - 75, HEIGHT//2, 150, 30, "To Do List", lambda: launchToDoList()))
menuButtons.append(Button(WIDTH//2 - 75, HEIGHT//2 + 50, 150, 30, "Quizz", lambda: launchQuizz()))

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
                for button in buttonsList:
                    button.checkClick(event.pos)

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
    runningFunc = lambda: timeTable()

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