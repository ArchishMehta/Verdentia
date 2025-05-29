# imports
import pygame
import os
from game_data import *
from settings import *
from pytmx.util_pygame import load_pygame
from sprites import Sprite, AnimatedSprite, MonsterPatchSprite, BorderSprite, CollidableSprite, TransitionSprite
from entities import Player, Character
from groups import AllSprites
from support import * 
from dialog import DialogTree
from monster import Monster
from monster_index import MonsterIndex
from battle import Battle
from timer import Timer  # type: ignore
from random import randint
from evolution import Evolution

# game class
class Game:
    # main
    def __init__(self):
        # initialize all pygame modules
        pygame.init()

        # create main game window
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        # set title of the window
        pygame.display.set_caption('Verdentia')
        self.clock = pygame.time.Clock()

        # timer 
        self.encounter_timer = Timer(2000, func = self.monster_encounter)

        # player monsters 
        self.player_monsters = {
            0: Monster('Charmadillo', 30),
            1: Monster('Friolera', 29),
            2: Monster('Larvea', 3),
            4: Monster('Atrox', 24),
            5: Monster('Gulfin', 17),
            6: Monster('Jacana', 3),
            7: Monster('Pouch', 3)
        }

        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.character_sprites = pygame.sprite.Group()
        self.transition_sprites = pygame.sprite.Group()
        self.monster_sprites = pygame.sprite.Group()

        # transition
        self.transition_target = None
        self.tint_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.tint_mode = 'untint'
        self.tint_progress = 0 
        self.tint_direction = -1 
        self.tint_speed = 600

        # load game assets
        self.import_assets()
        self.setup(self.tmx_maps['world'], 'house')
        self.audio['overworld'].play(-1)

        # overlays 
        self.dialog_tree = None
        self.monster_index = MonsterIndex(self.player_monsters, self.fonts, self.monster_frames)
        self.index_open = False
        self.battle = None
        self.evolution = None

    def import_assets(self):
        # get path to current file
        base_path = os.path.dirname(os.path.abspath(__file__))

        # create paths to TMX map files
        world_map_path = os.path.join(base_path, '..', 'data', 'maps', 'world.tmx')
        hospital_map_path = os.path.join(base_path, '..', 'data', 'maps', 'hospital.tmx')

        # load maps
        self.tmx_maps = tmx_importer(base_path, '..', 'data', 'maps')

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
        font_path2 = os.path.join(base_path, '..', 'graphics', 'fonts', 'dogicapixelbold.otf')

        # load fonts
        self.fonts = {
            'dialog': pygame.font.Font(font_path, 30),
            'regular': pygame.font.Font(font_path, 18),
            'small': pygame.font.Font(font_path, 14),
            'bold': pygame.font.Font(font_path2, 20)
        }

        # monster asset paths
        monsters_path = (4, 2, base_path, '..', 'graphics', 'monsters')
        icons_path = (base_path, '..', 'graphics', 'icons')
        ui_path = (base_path, '..', 'graphics', 'ui')

        # load monsters
        self.monster_frames = {
            'icons': import_folder_dict(*icons_path),
            'monsters': monster_importer(*monsters_path),
            'ui':import_folder_dict(*ui_path),
            'outlines': outline_creator(monster_importer(*monsters_path), 4),
            'attacks': attack_importer('..', 'graphics', 'attacks')
        }
        

        # battle fields
        battle_path = (base_path, '..', 'graphics', 'backgrounds')
        self.bg_frames = import_folder_dict(*battle_path)
        star_animation_path = os.path.join(base_path, '..', 'graphics', 'other', 'star animation')
        self.star_animation_frames = import_folder(star_animation_path)
        # audio
        audio_path = (base_path, '..', 'audio')
        self.audio = audio_importer(*audio_path)
        
    def setup(self, tmx_map, player_start_pos):
        # clear map 
        for group in (self.all_sprites, self.collision_sprites, self.transition_sprites, self.character_sprites):
            group.empty()

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
        
        # transition objects
        for obj in tmx_map.get_layer_by_name('Transition'):
            TransitionSprite((obj.x, obj.y), (obj.width, obj.height), (obj.properties['target'], obj.properties['pos']), self.transition_sprites)

        # collidable objects
        for obj in tmx_map.get_layer_by_name('Collisions'):
            BorderSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        # grass patches 
        for obj in tmx_map.get_layer_by_name('Monsters'):
            MonsterPatchSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.monster_sprites), obj.properties['biome'], obj.properties['monsters'], obj.properties['level'])

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
                    facing_direction = obj.properties['direction'], 
                    character_data = TRAINER_DATA[obj.properties['character_id']],
                    player = self.player,
                    create_dialog = self.create_dialog,
                    collision_sprites = self.collision_sprites,
                    radius = obj.properties['radius'], 
                    nurse = obj.properties['character_id'] == 'Nurse',
                    notice_sound = self.audio['notice'])

    def input(self):
        if not self.dialog_tree and not self.battle:
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
            if keys[pygame.K_RETURN]:
                self.index_open = not self.index_open
                self.player.blocked = not self.player.blocked
    
    def create_dialog(self, character):
        if not self.dialog_tree:
            self.dialog_tree = DialogTree(character, self.player, self.all_sprites, self.fonts['dialog'], self.end_dialog)
    
    def end_dialog(self, character):
        self.dialog_tree = None
        if character.nurse: 
            for monster in self.player_monsters.values():
                monster.health = monster.get_stat('max_health')
                monster.energy = monster.get_stat('max_energy')
            self.player.unblock()
        elif not character.character_data['defeated']:
            self.audio['overworld'].stop()
            self.audio['battle'].play(-1)
            self.transition_target = Battle(self.player_monsters, character.monsters, self.monster_frames, self.bg_frames[character.character_data['biome']], self.fonts, self.end_battle, character, self.audio)
            self.tint_mode = 'tint'
        else:
            self.player.unblock()
            self.check_evolution()

    # transitions
    def transition_check(self):
        sprites = [sprite for sprite in self.transition_sprites if sprite.rect.colliderect(self.player.hitbox)]
        if sprites:
            self.player.block()
            self.transition_target = sprites[0].target
            self.tint_mode = 'tint'

    def tint_screen(self, dt):
        if self.tint_mode == 'tint':
            self.tint_progress += self.tint_speed * dt
            if self.tint_progress >= 255:
                if type(self.transition_target) == Battle:
                    self.battle = self.transition_target
                elif self.transition_target == 'level':
                    self.battle = None
                else:
                    # perform map transition
                    self.setup(self.tmx_maps[self.transition_target[0]], self.transition_target[1])
                self.tint_mode = 'untint'
                self.transition_target = None

        elif self.tint_mode == 'untint':
            self.tint_progress -= self.tint_speed * dt
            self.tint_progress = max(0, self.tint_progress)

        if self.tint_progress > 0:
            self.tint_surf.fill((0, 0, 0))  # ensure the surface is black
            self.tint_surf.set_alpha(self.tint_progress)
            self.display_surface.blit(self.tint_surf, (0, 0))

    def end_battle(self, character):
        self.audio['battle'].stop()
        self.transition_target = 'level'
        self.tint_mode = 'tint'
        if character:
            character.character_data['defeated'] = True 
            self.create_dialog(character)
        elif not self.evolution: 
            self.player.unblock()
            self.check_evolution()

    def check_evolution(self):
        for index, monster in self.player_monsters.items():
            if monster.evolution:
                if monster.level == monster.evolution[1]:
                    self.audio['evolution'].play()
                    self.player.block()
                    self.evolution = Evolution(self.monster_frames['monsters'], monster.name, monster.evolution[0], self.fonts['bold'], self.end_evolution, self.star_animation_frames)
                    self.player_monsters[index] = Monster(monster.evolution[0], monster.level)
        if not self.evolution:
            self.audio['overworld'].play()
    
    def end_evolution(self):
        self.evolution = None 
        self.player.unblock()
        self.audio['evolution'].stop()
        self.audio['overworld'].play(-1)
    # monsters in grass 
    def check_monster(self):
        if [sprite for sprite in self.monster_sprites if sprite.rect.colliderect(self.player.hitbox)] and not self.battle and self.player.direction:
            if not self.encounter_timer.active:
                self.encounter_timer.activate() 
    
    def monster_encounter(self):
        sprites = [sprite for sprite in self.monster_sprites if sprite.rect.colliderect(self.player.hitbox)]
        if sprites and self.player.direction:
            self.encounter_timer.duration = randint(800, 2500)
            self.player.block()
            self.audio['overworld'].stop()
            self.audio['battle'].play(-1)
            self.transition_target = Battle(self.player_monsters, {index:Monster(monster, sprites[0].level + randint(-3, 3)) for index, monster in enumerate(sprites[0].monsters)}, self.monster_frames, self.bg_frames[sprites[0].biome], self.fonts, self.end_battle, None, self.audio)
            self.tint_mode = 'tint'

    def run(self):
        # main game loop to keep the game running
        while True:
            # track the frame rate 
            # time difference between current frame and last frame
            dt = self.clock.tick() / 1000 # 1000 ms in second
            self.display_surface.fill('black')

            # game loop
            for event in pygame.event.get():
                # if the user clicks the close button
                if event.type == pygame.QUIT:
                    # exit 
                    pygame.quit()
                    exit()
            
            # looks at all sprites and update
            self.encounter_timer.update()
            self.input()
            self.transition_check()
            self.all_sprites.update(dt)
            self.check_monster()
    
            # draw
            self.all_sprites.draw(self.player)

            # overlays 
            if self.dialog_tree:
                self.dialog_tree.update()
            if self.index_open:
                self.monster_index.update(dt)
            if self.battle:
                self.battle.update(dt)
            if self.evolution:
                self.evolution.update(dt)

            # screen tint (fade to black for transition)
            self.tint_screen(dt)

            # update the display with any changes
            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()