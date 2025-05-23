# import everything from settings
from settings import * 

# custom sprite class
class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        # add this sprite to any sprite passed in groups
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
