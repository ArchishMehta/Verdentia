# import everything from settings
import pygame
import os
from settings import *
from pytmx.util_pygame import load_pygame
from sprites import Sprite, AnimatedSprite
from entities import Player, Character
from groups import AllSprites
from support import * 


# game class
class Game:
    def __init__(self):
        # initialize all pygame modules
        pygame.init()
        # create main game window
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        # set title of the window
        pygame.display.set_caption('Verdentia')
        self.clock = pygame.time.Clock()
        # groups
        self.all_sprites = AllSprites()

        # load game assets
        self.import_assets()
        self.setup(self.tmx_maps['world'], 'house')

    def import_assets(self):
        # get path to current file
        base_path = os.path.dirname(os.path.abspath(__file__))

        # create paths to TMX map files
        world_map_path = os.path.join(base_path, '..', 'data', 'maps', 'world.tmx')
        hospital_map_path = os.path.join(base_path, '..', 'data', 'maps', 'hospital.tmx')

        # load maps
        self.tmx_maps = {
            'world': load_pygame(world_map_path),
            'hospital': load_pygame(hospital_map_path)
        }

        # create path for water animation and coast tileset
        water_path = os.path.join(base_path, '..', 'graphics', 'tilesets', 'water')
        coast_path = (24, 12, base_path, '..', 'graphics', 'tilesets', 'coast')
        characters_path = (base_path, '..', 'graphics', 'characters')

        # load animation and tiles
        self.overworld_frames = {
            'water': import_folder(water_path),
            'coast': coast_importer(*coast_path),
            'characters': all_character_import(*characters_path)
        }
    
    def setup(self, tmx_map, player_start_pos):
        # go through the 'Terrain' and 'Terrain Top' layer of map
        for layer in ['Terrain', 'Terrain Top']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)
        
        # go through the 'Objects' layer of map
        for obj in tmx_map.get_layer_by_name('Objects'):
            Sprite((obj.x, obj.y), obj.image, self.all_sprites)

        # go through the 'Entities' layer and place the player
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                if obj.properties['pos'] == player_start_pos:
                    self.player = Player(
                        pos = (obj.x, obj.y),
                        frames = self.overworld_frames['characters']['player'], 
                        groups = self.all_sprites,
                        facing_direction = obj.properties["direction"])
            else: 
                Character(
                    pos = (obj.x, obj.y),
                    frames = self.overworld_frames['characters'][obj.properties['graphic']], 
                    groups = self.all_sprites,
                    facing_direction = obj.properties["direction"])

        # go through the 'Water' layer and place the player
        for obj in tmx_map.get_layer_by_name('Water'):
            for x in range(int(obj.x), int(obj.x + obj.width), TILE_SIZE):
                for y in range(int(obj.y), int(obj.y + obj.height), TILE_SIZE):
                    AnimatedSprite((x,y), self.overworld_frames['water'], self.all_sprites)
        
        # go through the 'Coast' layer and place the player
        for obj in tmx_map.get_layer_by_name('Coast'):
            terrain = obj.properties['terrain']
            side = obj.properties['side']
            AnimatedSprite((obj.x, obj.y), self.overworld_frames['coast'][terrain][side], self.all_sprites)

    def run(self):
        # main game loop to keep the game running
        while True:
            # track the frame rate 
            # time difference between current frame and last frame
            dt = self.clock.tick() / 1000 # 1000 ms in second
            # game loop
            for event in pygame.event.get():
                # if the user clicks the close button
                if event.type == pygame.QUIT:
                    # exit 
                    pygame.quit()
                    exit()
            
            # looks at all sprites and update
            self.all_sprites.update(dt)
            self.display_surface.fill('black')
            # draw
            self.all_sprites.draw(self.player.rect.center)
            # update the display with any changes
            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()

