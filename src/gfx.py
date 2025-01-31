import os, re
import pygame as pg
from pygame.math import Vector2

# ------------------------------------------------------------ #
class Window:
    def __init__(self, width: int, height: int, title: str) -> None:
        self.zoom: float = 1.0
        self.size: list[int] = [width, height]
        self.display: pg.Surface = pg.Surface([width, height])
        self.window: pg.Surface = pg.display.set_mode([width, height], pg.WINDOWPOS_CENTERED)
        pg.display.set_caption(title)

    def fill(self, color: list[int]) -> None:
        self.display.fill(color)
        self.window.fill(color)

    def blit(self, surface: pg.Surface, location: list[float]) -> None:
        self.display.blit(surface, location)

    def render(self) -> None:
        self.window.blit(
            dest = [0, 0],
            source = pg.transform.scale(self.display, [self.size[0] / self.zoom, self.size[1] / self.zoom])
        )
        pg.display.flip()
# ------------------------------------------------------------ #

# ------------------------------------------------------------ #
class Sprite(pg.sprite.Sprite):
    def __init__(self, size: list[int], speed: float, location: list[float], color: list=[255, 255, 255], rotate: bool = False) -> None:
        super().__init__([])
        self.size = size
        self.color = color
        self.speed = speed

        self._image = pg.Surface(size, pg.SRCALPHA)
        self._image.fill(color)

        self.image = self._image
        self.rect = self.image.get_rect(topleft=location)

        self.rotation = 0.0
        self.rotSpeed = 0.0
        self.rotate: bool = rotate
        self.friction: float = (90/100) # dampens movement by 90% by default
        self.velocity = pg.math.Vector2(0, 0)
        self.location = pg.math.Vector2(location)
    
    def moveRight(self) -> None:
        self.velocity[0] = self.speed
    
    def moveLeft(self) -> None:
        self.velocity[0] = -self.speed
    
    def moveUp(self) -> None:
        self.velocity[1] = -self.speed
    
    def moveDown(self) -> None:
        self.velocity[1] = self.speed

    def fillImage(self, color: list[int]=[255, 255, 255]) -> None:
        self._image.fill(color)

    def setColor(self, color: list[int]=[255, 255, 255]) -> None:
        self._image.fill(color)
        self.color = color

    def setImage(self, image: pg.Surface=None, color: list=[255, 255, 255], wireSize: int = 0) -> None:
        if image is None:
            self._image = pg.Surface(self.size, pg.SRCALPHA)
            if wireSize != 0:
                drawRect(self._image, self.size, self._image.get_rect().topleft, color, wireSize)
            else:
                self._image.fill(color)
        else:
            self._image = image

        self.image = self._image
        self.rect = self.image.get_rect(topleft=self.location)

    def update(self, deltaTime: float) -> None:
        self.location += self.velocity * deltaTime
        self.rect.topleft = self.location

        if self.rotate and self.rotSpeed != 0:
            self.rotation += self.rotSpeed * deltaTime

            self.rotSpeed *= 0.9
            if abs(self.rotSpeed) < 0.1:
                self.rotSpeed = 0.0

            self.image = pg.transform.rotate(self._image, -self.rotation)
            self.rect = self.image.get_rect(center=self.rect.center)
        
        # normalize rotation to -180 to 180
        if self.rotation > 180:
            self.rotation -= 360
        elif self.rotation < -180:
            self.rotation += 360
# ------------------------------------------------------------ #

# ------------------------------------------------------------ #
class Renderer:
    def __init__(self):
        self.groups = {
            "background": pg.sprite.Group(),
            "midground": pg.sprite.Group(),
            "foreground": pg.sprite.Group()
        }

    def addSprite(self, sprite:Sprite, group:str="background") -> bool:
        try:
            self.groups[group].add(sprite)
            return True
        except (Exception) as e: return False

    def remSprite(self, sprite:Sprite, group:str="background") -> bool:
        try:
            self.groups[group].remove(sprite)
            return True
        except (Exception) as e: return False

    def render(self, target:pg.Surface) -> None:
        for group in self.groups:
            self.groups[group].draw(target)
# ------------------------------------------------------------ #

# ------------------------------------------------------------ #
class AssetManager:
    def __init__(self) -> None:
        self.font:dict = {}
        self.image:dict = {}
        self.audio:dict = {}

    def getImage(self, key:str) -> pg.Surface|pg.Surface:
        return self.image.get(key, None)
    
    def setImage(self, key:str, image:pg.Surface) -> pg.Surface|None:
        try:
            self.image[key] = image
        except (KeyError) as err: print(err)

    def loadImage(self, key:str, path:str, scale:list=None, colorKey:list=None) -> pg.Surface:
        try:
            self.image[key] = loadImage(path, scale, colorKey)
        except (FileNotFoundError) as err: print(err)
    
    def loadImageDir(self, key:str, path:str, scale:list=None, colorKey:list=None) -> list:
        try:
            self.image[key] = loadImageDir(path, scale, colorKey)
        except (FileNotFoundError) as err: ...
    
    def loadImageSheet(self, key:str, path:str, frameSize:int, colorKey:list=None) -> list:
        try:
            self.image[key] = loadImageSheet(path, frameSize, colorKey)
        except (FileNotFoundError) as err: ...
# ------------------------------------------------------------ #

# ------------------------------------------------------------ #
class Animation:
    def __init__(self, frames: list[pg.Surface], loop:bool=1, frameDuration:float=5, frameOffset:list[int]=[0, 0]) -> None:
        self.done = 0
        self.frame = 0
        self.loop = loop
        self.frames = frames
        self.frameOffset = frameOffset
        self.frameDuration = frameDuration
   
    def getFrame(self):
        return self.frames[int(self.frame / self.frameDuration)]

    def update(self) -> None:
        if self.loop:
            self.frame = (self.frame + 1) % (self.frameDuration * len(self.frames))
        else:
            self.frame = min(self.frame + 1, self.frameDuration * len(self.frames) - 1)
            if self.frame >= self.frameDuration * len(self.frames) - 1:
                self.done = 1
# ------------------------------------------------------------ #

# ------------------------------------------------------------ #
class Particle(Sprite):
    def __init__(self, lifeSpan: float, size:list[int], location:list[float], color:list[int]=[0, 255, 0], wireSize: int=0) -> None:
        super().__init__(size, 0.0, location, color)
        self.lifeSpan: float = lifeSpan
        self.setImage(color=color, wireSize=wireSize)

    def kill(self) -> None:
        del self

    def update(self, deltaTime: float) -> None:
        super().update(deltaTime)
        
        self.lifeSpan -= 1.0 * deltaTime

        kill = 0
        if self.lifeSpan <= 0:
            kill = 1

        return kill
# ------------------------------------------------------------ #

# ------------------------------------------------------------ #
class ParticleSystem:
    def __init__(self, assetManager: AssetManager, renderer: Renderer, location: list[int], maximum: int) -> None:
        self.particles = []
        self.maximum = maximum
        self.location = location
        self.renderer = renderer
        self.assetManager = assetManager

    def addParticle(self, lifeSpan: float, size: list[int], location, velocity:list[float]=Vector2(0, 0), color: list[int]=[255, 255, 255], wireSize: int=0, asset: str=None) -> None:
        if len(self.particles)+1 > self.maximum: return None
        particle = Particle(lifeSpan, size, [
            location[0] + self.location[0],
            location[1] + self.location[1]
        ], color, wireSize)
        particle.velocity = Vector2(velocity)
        if asset:
            try:
                image = self.assetManager.getImage(asset)
                particle.setImage(image)
            except KeyError as e: pass
        self.particles.append(particle)
        self.renderer.addSprite(particle)

    def update(self, deltaTime: float) -> None:
        for particle in self.particles:
            if particle.update(deltaTime):
                self.particles.remove(particle)
                self.renderer.remSprite(particle)
                particle.kill()
# ------------------------------------------------------------ #

# ------------------------------------------------------------ #
class DevDisplay:
    def __init__(self, size: list[int], location: list[float], fontPath:str, textColor:list[int]=[255, 255, 255], textSize: int=18):
        self.size: list[int] = size
        self.location: list[float] = location
        self.surface: pg.Surface = createSurface(size, textColor)
        
        self.textSize: int = textSize
        self.textFields: dict[str, str] = {}
        self.textColor: list[int] = textColor
        self.font: pg.Font = pg.Font(fontPath, textSize)

    def setTextField(self, field: str, text: str) -> bool:
        try:
            self.textFields[field] = text
            return True
        except KeyError as e:
            print(f"DevDisplay TextField Not Found: {field}")
            return False
    
    def remTextField(self, field: str) -> bool:
        try:
            self.textFields.pop(field)
            return True
        except KeyError as e:
            print(f"DevDisplay TextField Not Found: {field}")
            return False

    def render(self, window: pg.Surface) -> None:
        window.blit(self.font.render(f"Dev-Display", True, self.textColor), self.location)
        for index, field in enumerate(self.textFields.keys()):
            text = f"{field}: {self.textFields[field]}"
            textSurface = self.font.render(text, True, self.textColor)
            textLocation = [
                self.location[0],
                self.location[1] + (textSurface.get_size()[1] * (index + 1))
            ]
            window.blit(textSurface, textLocation)
# ------------------------------------------------------------ #

# ------------------------------------------------------------ #
def showMouse() -> None:
    pg.mouse.set_visible(True)

def hideMouse() -> None:
    pg.mouse.set_visible(False)

def createSurface(size:list[int], color:list[int]) -> pg.Surface:
    s:pg.Surface = pg.Surface(size)
    s.fill(color)
    return s

def createRect(location:list, size:list) -> pg.Rect :
    return pg.Rect(location, size)

def flipSurface(surface:pg.Surface, x:bool, y:bool) -> pg.Surface:
    return pg.transform.flip(surface, x, y)

def fillSurface(surface:pg.Surface, color:list[int]) -> None:
    surface.fill(color)

import pygame

def createSurfaceFADE(size, color, dx, dy):
    """
    Creates a surface with a color fading out to transparency in a given direction.
    
    Args:
        size (tuple): Width and height of the surface.
        color (tuple): RGB color to fade out.
        direction (str): Direction of fade ('left', 'right', 'up', 'down').
    
    Returns:
        pygame.Surface: Surface with the fade effect.
    """
    width, height = size
    fade_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    r, g, b = color

    if dx != 0:
        for x in range(width):
            alpha = 255 - int((x / width) * 255) if dx < 0 else int((x / width) * 255)
            pygame.draw.line(fade_surface, (r, g, b, alpha), (x, 0), (x, height - 1))
    elif dy != 0:
        for y in range(height):
            alpha = 255 - int((y / height) * 255) if dy > 0 else int((y / height) * 255)
            pygame.draw.line(fade_surface, (r, g, b, alpha), (0, y), (width - 1, y))
    
    return fade_surface

def createSurfaceLERP(size, start_color, end_color):
    """
    Creates a surface with a gradient linearly-interpolating between two colors.
    
    Args:
        size (tuple): Width and height of the surface.
        start_color (tuple): Starting RGB color.
        end_color (tuple): Ending RGB color.
    
    Returns:
        pygame.Surface: Surface with the gradient effect.
    """
    width, height = size
    gradient_surface = pygame.Surface((width, height))
    sr, sg, sb = start_color
    er, eg, eb = end_color

    for x in range(width):
        # Interpolate color
        t = x / (width - 1) if width > 1 else 0
        r = int(sr + (er - sr) * t)
        g = int(sg + (eg - sg) * t)
        b = int(sb + (eb - sb) * t)
        pygame.draw.line(gradient_surface, (r, g, b), (x, 0), (x, height - 1))
    
    return gradient_surface

def naturalKey(string_) -> list[int] :
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

def drawLine(display:pg.Surface, color:list[int], start:list[int|float], end:list[int|float], width:int=1) -> None :
    pg.draw.line(display, color, start, end, width=width)
    
def drawRect(display:pg.Surface, size:list[int], location:list[int|float], color:list[int]=[255,0,0], width:int=1) -> None :
    pg.draw.rect(display, color, pg.Rect(location, size), width=width)

def drawCircle(surface, color, center, radius, width=0):
    pg.draw.circle(surface, color, (int(center[0]), int(center[1])), radius, width)

def rotateSurface(surface:pg.Surface, angle:float) -> None :
    return pg.transform.rotate(surface, angle)

def scaleSurface(surface:pg.Surface, scale:list) -> pg.Surface :
    return pg.transform.scale(surface, scale)

def imageVisible(image:pg.Surface, threshold:int=1) -> bool:
    result = False
    pixels, noPixels = 0, 0
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            pixel = image.get_at([x, y])
            if pixel[3] == 0:
                noPixels += 1
            pixels += 1
    if pixels-noPixels >= threshold:
        result = True
    return result

def loadImage(file_path:str, scale:list=None, colorKey:list=None) -> pg.Surface :
    image:pg.Surface = pg.image.load(file_path).convert_alpha()
    image.set_colorkey(colorKey)
    if scale: image = scaleSurface(image, scale)
    return image

def loadImageDir(dirPath:str, scale:list=None, colorKey:list=None) -> list[pg.Surface] :
    images:list = []
    for _, __, image in os.walk(dirPath):
        sorted_images = sorted(image, key=naturalKey)
        for image in sorted_images:
            full_path = dirPath + '/' + image
            image_surface = loadImage(full_path, scale, colorKey)
            if imageVisible(image_surface):
                images.append(image_surface)
    return images
            
def loadImageSheet(sheetPath:str, frameSize:list[int], colorKey:list=None) -> list[pg.Surface] :
    sheet = loadImage(sheetPath)
    frame_x = int(sheet.get_size()[0] / frameSize[0])
    frame_y = int(sheet.get_size()[1] / frameSize[1])
    
    frames = []
    for row in range(frame_y):
        for col in range(frame_x):
            x = col * frameSize[0]
            y = row * frameSize[1]
            frame = pg.Surface(frameSize, pg.SRCALPHA).convert_alpha()
            frame.set_colorkey(colorKey)
            frame.blit(sheet, (0,0), pg.Rect((x, y), frameSize))   # blit the sheet at the desired coords (texture mapping)
            if imageVisible(frame):
                frames.append(frame)
    return frames
# ------------------------------------------------------------ #

