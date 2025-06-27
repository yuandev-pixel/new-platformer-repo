import pygame

class StaticEntity:
    def __init__(self, x:int, y:int,image:pygame.Surface,hitbox:pygame.Rect) -> None:
        self.x = x
        self.y = y
        self.image = image
        self.hitbox = hitbox

    def draw(self, screen:pygame.Surface) -> None:
        screen.blit(self.image, (self.x, self.y))

class AnimatedEntity:
    def __init__(self, x:int, y:int,image:list,hitbox:pygame.Rect,interval:int) -> None:
        self.x = x
        self.y = y
        self.image = image
        self.hitbox = hitbox
        self.frame = 0
        self.interval = interval
        self.tclock = interval - 1
        self.length = len(image)

    def update(self,x:int,y:int) -> None:
        self.x = x
        self.y = y
        self.tclock += 1
        if self.tclock == self.interval:
            self.tclock = 0
            self.frame += 1
            if self.frame >= self.length:
                self.frame = 0

    def draw(self, screen:pygame.Surface) -> None:
        screen.blit(self.image[self.frame], (self.x, self.y))
        