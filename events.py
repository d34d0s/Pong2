import pygame as pg

class EventHandler:
    quit:bool=False

    def __init__(self):
        self.keyboard = {}
        self.mouseOld = {}
        self.keyboardOld = {}
        self.mouse = {
            1:False,
            2:False,
            3:False,
            4:False,
            5:False,
            6:False,
            7:False
        }
        self.mouseWheelUp=False
        self.mouseWheelDown=False
        
        self.mouseLocation = (0,0)

    def update(self) -> bool:
        self.mouseWheelUp = False
        self.mouseWheelDown = False
        self.mouseOld = self.mouse.copy()
        self.keyboardOld = self.keyboard.copy()
        self.mouseLocation = pg.mouse.get_pos()
        
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_F12):
                return False
            match event.type:
                case pg.KEYUP:
                    self.keyboard[event.key] = False
                case pg.KEYDOWN:
                    self.keyboard[event.key] = True
                case pg.MOUSEBUTTONUP:
                    self.mouse[event.button] = False
                case pg.MOUSEBUTTONDOWN:
                    self.mouse[event.button] = True
                    if event.button == 4:
                        self.mouseWheelUp = True
                    if event.button == 5:
                        self.mouseWheelDown = True
        return True

    def keyPressed(self, key):
        return self.keyboard.get(key, False)

    def keyTriggered(self, key):
        return self.keyboard.get(key, False) and not self.keyboardOld.get(key, False)
    
    def mousePressed(self, button:int):
        return self.mouse.get(button, False)

    def mouseTriggered(self, button):
        return self.mouse.get(button, False) and not self.mouseOld.get(button, False)
  
