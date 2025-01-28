import pygame as pg

class SoundManager:
    def __init__(self) -> None:
        pg.mixer.init()
        self.globalVolume: float = 100.0
        self.sounds: dict[str, pg.mixer.Sound] = {}
    
    def loadSound(self, id: str, path: str, volume: float=100.0) -> None:
        try:
            self.sounds[id] = pg.mixer.Sound(path)
            self.sounds[id].set_volume(volume/self.globalVolume)
        except (Exception) as e: pass

    def playSound(self, id: str) -> None:
        try:
            self.sounds[id].play()
        except (Exception) as e: print(e)

