# all the imports
import pygame
from pygame.math import Vector2 as vector 
from sys import exit

# game window resolution
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
# size of each tile on the game map 
TILE_SIZE = 64 
# speed that animations update (lower = faster)
ANIMATION_SPEED = 6
# thickness for battle elements
BATTLE_OUTLINE_WIDTH = 4

# dictionaries
# colors used across game
COLORS = {
	'white': '#f4fefa', 
	'pure white': '#ffffff',
	'dark': '#2b292c',
	'light': '#c8c8c8',
	'gray': '#3a373b',
	'gold': '#ffd700',
	'light-gray': '#4b484d',
	'fire':'#f8a060',
	'water':'#50b0d8',
	'plant': '#64a990', 
	'black': '#000000', 
	'red': '#f03131',
	'blue': '#66d7ee'
}

# render order for layers in the world (lower = drawn first)
WORLD_LAYERS = {
	'water': 0,
	'bg': 1,
	'shadow': 2,
	'main': 3,
	'top': 4
}

# coordinates for where monsters stand during fight 
BATTLE_POSITIONS = {
	'left': {'top': (360, 260), 'center': (190, 400), 'bottom': (410, 520)},
	'right': {'top': (900, 260), 'center': (1110, 390), 'bottom': (900, 550)}
}

# draw order for elements in fights (lower = behind)
BATTLE_LAYERS =  {
	'outline': 0,
	'name': 1,
	'monster': 2,
	'effects': 3,
	'overlay': 4
}

# coordinates for where buttons are during fight
BATTLE_CHOICES = {
	'full': {
		'fight':  {'pos' : vector(30, -60), 'icon': 'sword'},
		'defend': {'pos' : vector(40, -20), 'icon': 'shield'},
		'switch': {'pos' : vector(40, 20), 'icon': 'arrows'},
		'catch':  {'pos' : vector(30, 60), 'icon': 'hand'}},
	
	'limited': {
		'fight':  {'pos' : vector(30, -40), 'icon': 'sword'},
		'defend': {'pos' : vector(40, 0), 'icon': 'shield'},
		'switch': {'pos' : vector(30, 40), 'icon': 'arrows'}}
}