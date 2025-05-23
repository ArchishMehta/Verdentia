# get everything from settings
from settings import * 

class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, facing_direction):
        super().__init__(groups)

        # graphics 
        self.frame_index, self.frames = 0, frames
        self.facing_direction = facing_direction

        # movement
        self.direction = vector()
        self.speed = 250

        # sprite setup 
        self.image = self.frames[self.get_state()][self.frame_index]
        self.rect = self.image.get_frect(center = pos)
    
    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt 
        self.image = self.frames[self.get_state()][int(self.frame_index % len(self.frames[self.get_state()]))]
    
    def get_state(self):
        moving = bool(self.direction)
        if moving:
            if self.direction.x != 0: 
                self.facing_direction = 'right' if self.direction.x > 0 else 'left'
            if self.direction.y != 0: 
                self.facing_direction = 'down' if self.direction.y > 0 else 'up'
        return f'{self.facing_direction}{"_idle" if not moving else ""}'

class Character(Entity):
    def __init__(self, pos, frames, groups, facing_direction):
        super().__init__(pos, frames, groups, facing_direction)

# a class for the main player
class Player(Entity):
    # constrcutor for main player
    def __init__(self, pos, frames, groups, facing_direction):
        super().__init__(pos, frames, groups, facing_direction) 

    def input(self):
        # get the pressed key
        keys = pygame.key.get_pressed()
        input_vector = vector()
        # if UP
        if keys[pygame.K_UP]:
            input_vector.y -= 1
        # if DOWN
        if keys[pygame.K_DOWN]:
            input_vector.y += 1
        # if LEFT
        if keys[pygame.K_LEFT]:
            input_vector.x -= 1
        # if RIGHT
        if keys[pygame.K_RIGHT]:
            input_vector.x += 1
        self.direction = input_vector

    # move player based on direction and delta time
    def move(self, dt): 
        self.rect.center += self.direction * self.speed * dt 

    # update the player each frame
    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)