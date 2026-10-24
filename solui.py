from turtle import clone

from pygame import *

init()
font.init()

comicSans = font.SysFont("ldfcomicsansbold", 18)
smallerText = font.SysFont("ldfcomicsansbold", 16)
dropDownText = font.SysFont("ldfcomicsansbold", 10)

displayInfo = display.Info()
WIDTH, HEIGHT = 800, 600
bgColor = (0, 0, 0)

screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()

globalElements = []
defferedFuncs = []
tabs = {}

currentTab = "NONE"
tabFunc = lambda: print("No running function was set")
tabElements = []

class Element:
    def __init__(self, coords, color = (255, 255, 255), hollow = 0, radius = 0):
        self.originalCoords = coords
        self.rect = Rect(coords[0], coords[1], coords[2], coords[3])
        self.color = color
        self.hollow = hollow
        self.radius = radius

    def draw(self):
        draw.rect(screen, self.color, self.rect, self.hollow, self.radius)

class Text(Element):
    def __init__(self, coords, text, font = comicSans, color = (255, 255, 255)):
        self.text = text
        self.font = font
        self.textSurface = self.font.render(self.text, True, color)
        super().__init__(coords + (self.textSurface.width, self.textSurface.height))

    def draw(self):
        self.textSurface = self.font.render(self.text, True, self.color)
        textRect = self.textSurface.get_rect(center=self.rect.center)
        screen.blit(self.textSurface, textRect)

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
        if self.rect.collidepoint(pos) and self.onClick:
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

    def draw(self):
        super().draw()
        if self.buttonsVisible:
            for button in self.buttons:
                button.draw()

    def checkClick(self, pos):
        super().checkClick(pos)
        if self.buttonsVisible:
            for button in self.buttons:
                button.checkClick(pos)

    def toggleButtons(self):
        if not self.buttonsVisible:
            for i, button in enumerate(self.buttons):
                button.rect.x = self.rect.x + self.rect.width//2 - button.rect.width//2
                button.rect.y = self.rect.y + 32 + 20*i + self.rect.height//2 - button.rect.height//2
            self.buttonsVisible = True
        else:
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
        if event.type == KEYDOWN:
            if event.key == K_UP:
                self.changeOption(1)
                processed = True
            elif event.key == K_DOWN:
                self.changeOption(-1)
                processed = True
        return processed

class TextInput(Focusable):
    def __init__(self, coords, text):
        super().__init__(coords, text)
        self.value = ""

    def update(self):
        self.text = self.value
        render = self.font.render(self.text, True, self.color)
        self.rect.width = max(self.originalCoords[2], render.width+10)
        self.rect.height = max(self.originalCoords[3], render.height+5)
        self.rect.x = self.originalCoords[0] - max(0, render.width//2-self.originalCoords[2]//2+5)
        self.rect.y = self.originalCoords[1] - max(0, render.height//2-self.originalCoords[2]//2+5)

    def handleEvents(self, event):
        processed = False
        if event.type == KEYDOWN:
            if event.key == K_BACKSPACE:
                self.value = self.value[:-1]
                processed = True
            elif event.key == K_RETURN and event.mod == KMOD_LSHIFT:
                self.value += '\n'
                processed = True
            elif event.key:
                self.value += event.unicode
                processed = True
            self.update()
        return processed

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

def toggleFullscreen(type = "normal"):
    on = display.get_window_size() != (WIDTH, HEIGHT)
    if type == "normal":
        on = display.get_window_size() == (WIDTH, HEIGHT)
        if on: display.set_mode((displayInfo.current_w, displayInfo.current_h), FULLSCREEN)
        else: display.set_mode((WIDTH, HEIGHT))
    elements = globalElements+tabElements
    factor1 = (on and displayInfo.current_w/WIDTH) or 1
    factor2 = (on and displayInfo.current_h/HEIGHT) or 1
    for elem in elements:
        elem.rect.x, elem.rect.y = int(elem.originalCoords[0]*factor1), int(elem.originalCoords[1]*factor2)
        elem.rect.width, elem.rect.height = int(elem.originalCoords[2]*factor1), int(elem.originalCoords[3]*factor2)
        if hasattr(elem, "onFullScreen"):
            elem.onFullScreen()

def setupWindow(caption, iconPath):
    icon = image.load(iconPath).convert_alpha()
    display.set_icon(icon)
    display.set_caption(caption)

def createTab(tabName, tabFunc, tabElems):
    tabs[tabName] = {"function":tabFunc, "elems":tabElems}

def deleteTab(tabName):
    tabs[tabName] = None

def changeTab(tabName):
    global currentTab, tabFunc, tabElements
    if not tabName in tabs: return False
    currentTab = tabName
    tabFunc = tabs[tabName]["function"]
    tabElements = tabs[tabName]["elems"].copy()
    toggleFullscreen("stationary")

events = []
running = False
def launch():
    global running, events, defferedFuncs
    running = True
    while running:
        screen.fill(bgColor)

        events = event.get()
        for ev in events:
            if ev.type == QUIT:
                running = False
                break
            elif ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                for elem in globalElements + tabElements:
                    if hasattr(elem, "clickable"): elem.checkClick(ev.pos)
            elif ev.type == KEYDOWN and ev.key == K_F11:
                toggleFullscreen()

        for elem in globalElements + tabElements:
            elem.draw()

        if tabFunc: tabFunc()

        for func in defferedFuncs:
            func()
        defferedFuncs = []

        display.flip()
        clock.tick(60)

    quit()
