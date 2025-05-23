# import everything from settings
from settings import * 

# custom sprite class - parent class
class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        # add this sprite to any sprite passed in groups
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)

# sub class
class AnimatedSprite(Sprite):
    def __init__(self, pos, frames, groups):
        # first frame of animation
        self.frame_index, self.frames = 0, frames
        # initialize parent sprite class with position, the initial image, and groups
        super().__init__(pos, frames[self.frame_index], groups)

    def animate(self, dt):
        # increase frame index based on time delta and animation speed
        self.frame_index += ANIMATION_SPEED * dt
        # loop animation so it wraps around when it reaches the end
        self.image = self.frames[int(self.frame_index % len(self.frames))]

    def update(self, dt):
        self.animate(dt)