from settings import * 
from support import import_image
from entities import Entity
import os

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector()
        # base path of the current file
        base_path = os.path.dirname(os.path.abspath(__file__))
        # create full path to img
        shadow_image_path = os.path.join(base_path, '..', 'graphics', 'other', 'shadow')
        # load image
        self.shadow_surf = import_image(shadow_image_path)

    def draw(self, player_center):
        self.offset.x = - (player_center[0] - WINDOW_WIDTH / 2)
        self.offset.y = - (player_center[1] - WINDOW_HEIGHT / 2)

        # get all background sprites that come before the main layer
        bg_sprites = [sprite for sprite in self if sprite.z < WORLD_LAYERS['main']]
        # on main layer
        main_sprites = sorted([sprite for sprite in self if sprite.z == WORLD_LAYERS['main']], key = lambda sprite: sprite.y_sort)
        # after main layer
        fg_sprites = [sprite for sprite in self if sprite.z > WORLD_LAYERS['main']]

        for layer in (bg_sprites, main_sprites, fg_sprites):
            for sprite in layer: 
                if isinstance(sprite, Entity):
                    self.display_surface.blit(self.shadow_surf, sprite.rect.topleft + self.offset + vector(40, 110))
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
                