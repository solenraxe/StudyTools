import pygame as pg

pg.init()
pg.font.init()

comicSans = pg.font.SysFont("ldfcomicsansbold", 18)
smallerText = pg.font.SysFont("ldfcomicsansbold", 16)
dropDownText = pg.font.SysFont("ldfcomicsansbold", 10)

screen = None

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
            elif event.key == pg.K_RETURN and event.mod == pg.KMOD_LSHIFT:
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
