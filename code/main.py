# import everything from settings
import pygame
import os
from game_data import *
from settings import *
from pytmx.util_pygame import load_pygame
from sprites import Sprite, AnimatedSprite, MonsterPatchSprite, BorderSprite, CollidableSprite
from entities import Player, Character
from groups import AllSprites
from support import * 
from dialog import DialogTree


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
        self.collision_sprites = pygame.sprite.Group()
        self.character_sprites = pygame.sprite.Group()

        # load game assets
        self.import_assets()
        self.setup(self.tmx_maps['world'], 'house')

        self.dialog_tree = None 

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

        # create path for fonts
        font_path = os.path.join(base_path, '..', 'graphics', 'fonts', 'PixeloidSans.ttf')

        # load fonts
        self.fonts = {
            'dialog': pygame.font.Font(font_path, 30)
        }
    
    def setup(self, tmx_map, player_start_pos):
        # go through the 'Terrain' and 'Terrain Top' layer of map
        for layer in ['Terrain', 'Terrain Top']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, WORLD_LAYERS['bg'])
        
        # go through the 'Water' layer and place the player
        for obj in tmx_map.get_layer_by_name('Water'):
            for x in range(int(obj.x), int(obj.x + obj.width), TILE_SIZE):
                for y in range(int(obj.y), int(obj.y + obj.height), TILE_SIZE):
                    AnimatedSprite((x,y), self.overworld_frames['water'], self.all_sprites,  WORLD_LAYERS['water'])
        
        # go through the 'Coast' layer and place the player
        for obj in tmx_map.get_layer_by_name('Coast'):
            terrain = obj.properties['terrain']
            side = obj.properties['side']
            AnimatedSprite((obj.x, obj.y), self.overworld_frames['coast'][terrain][side], self.all_sprites, WORLD_LAYERS['bg'])
        
        # go through the 'Objects' layer of map
        for obj in tmx_map.get_layer_by_name('Objects'):
            if obj.name == 'top':
                Sprite((obj.x, obj.y), obj.image, self.all_sprites, WORLD_LAYERS['top'])
            else:
                CollidableSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        # collidable objects
        for obj in tmx_map.get_layer_by_name('Collisions'):
            BorderSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        # grass patches 
        for obj in tmx_map.get_layer_by_name('Monsters'):
            MonsterPatchSprite((obj.x, obj.y), obj.image, self.all_sprites, obj.properties['biome'])

        # go through the 'Entities' layer and place the player
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                if obj.properties['pos'] == player_start_pos:
                    self.player = Player(
                        pos = (obj.x, obj.y),
                        frames = self.overworld_frames['characters']['player'], 
                        groups = self.all_sprites,
                        facing_direction = obj.properties["direction"], 
                        collision_sprites = self.collision_sprites)
            else: 
                Character(
                    pos = (obj.x, obj.y),
                    frames = self.overworld_frames['characters'][obj.properties['graphic']], 
                    groups = (self.all_sprites, self.collision_sprites, self.character_sprites),
                    facing_direction = obj.properties["direction"], 
                    character_data = TRAINER_DATA[obj.properties['character_id']],
                    player = self.player,
                    create_dialog = self.create_dialog,
                    collision_sprites = self.collision_sprites,
                    radius = obj.properties['radius'])

    def input(self):
        if not self.dialog_tree:
            keys = pygame.key.get_just_pressed()
            if keys[pygame.K_SPACE]:
                for character in self.character_sprites:
                    if check_connections(100, self.player, character):
                        # block player input 
                        self.player.block()
                        # entities face each other
                        character.change_facing_direction(self.player.rect.center)
                        # dialog
                        self.create_dialog(character)
                        character.can_rotate = False
    
    def create_dialog(self, character):
        if not self.dialog_tree:
            self.dialog_tree = DialogTree(character, self.player, self.all_sprites, self.fonts['dialog'], self.end_dialog)
    
    def end_dialog(self, character):
        self.dialog_tree = None 
        self.player.unblock()

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
            self.input()
            self.all_sprites.update(dt)
            self.display_surface.fill('black')

            # draw
            self.all_sprites.draw(self.player)

            # overlays 
            if self.dialog_tree: self.dialog_tree.update()

            # update the display with any changes
            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()

