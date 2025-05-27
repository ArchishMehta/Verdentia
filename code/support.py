from settings import *
from os.path import join
from os import walk
from pytmx.util_pygame import load_pygame

# import functions
# imports a single image from a specified path
def import_image(*path, alpha = True, format = 'png'):
	# combine path and add file extension
	full_path = join(*path) + f'.{format}'
	# load image with or without alpha transparency
	surf = pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()
	return surf

# imports all images in a folder into a list sorted numerically by filename
def import_folder(*path):
	frames = []
	for folder_path, sub_folders, image_names in walk(join(*path)):
		for image_name in sorted(image_names, key = lambda name: int(name.split('.')[0])):
			full_path = join(folder_path, image_name)
			surf = pygame.image.load(full_path).convert_alpha()
			frames.append(surf)
	return frames

# imports all images in a folder into a dictionary using the filename (w/o extension) as the key
def import_folder_dict(*path):
	frames = {}
	for folder_path, sub_folders, image_names in walk(join(*path)):
		for image_name in image_names:
			full_path = join(folder_path, image_name)
			surf = pygame.image.load(full_path).convert_alpha()
			frames[image_name.split('.')[0]] = surf
	return frames

# imports each subfolder inside a folder and stores their content as lists in a dictionary
def import_sub_folders(*path):
	frames = {}
	for _, sub_folders, __ in walk(join(*path)):
		if sub_folders:
			for sub_folder in sub_folders:
				frames[sub_folder] = import_folder(*path, sub_folder)
	return frames

# splits a tilemap image into single tile surfaces and store them in a dictionary with (col, row) as keys
def import_tilemap(cols, rows, *path):
	frames = {}
	# load full tilemap image
	surf = import_image(*path)
	# get tile size
	cell_width, cell_height = surf.get_width() / cols, surf.get_height() / rows
	for col in range(cols):
		for row in range(rows):
			# the rect area for each tile
			cutout_rect = pygame.Rect(col * cell_width, row * cell_height,cell_width,cell_height)
			# a surface for each tile
			cutout_surf = pygame.Surface((cell_width, cell_height))
			cutout_surf.fill('green')
			cutout_surf.set_colorkey('green')
			cutout_surf.blit(surf, (0,0), cutout_rect)
			# store tile in dictionary with (col, row) key
			frames[(col, row)] = cutout_surf
	return frames

# creates dictionary of terrain types and the coastal tile frames
def coast_importer(cols, rows, *path):
	# get tilemap split into (col, row) frames
	frame_dict = import_tilemap(cols, rows, *path)
	new_dict = {}
	# list of terrain types
	terrains = ['grass', 'grass_i', 'sand_i', 'sand', 'rock', 'rock_i', 'ice', 'ice_i']
	# offset represents each tile type 
	sides = {
		'topleft': (0,0), 'top': (1,0), 'topright': (2,0), 
		'left': (0,1), 'right': (2,1), 'bottomleft': (0,2), 
		'bottom': (1,2), 'bottomright': (2,2)
		}
	# for loop for every terrain type build nested dictionary of side variations
	for index, terrain in enumerate(terrains):
		new_dict[terrain] = {}
		for key, pos in sides.items():
			# get all variations down the vertical axis (every 3 rows)
			new_dict[terrain][key] = [frame_dict[(pos[0] + index * 3, pos[1] + row)] for row in range(0, rows, 3)
]
	return new_dict

# import character animation frames from tilemap image by slicing into a grid
def character_importer(cols, rows, *path):
	# load tilemap and convert it into a dictionary
	frame_dict = import_tilemap(cols, rows, *path)
	new_dict = {}
	# assign directional animations by row - 0=down, 1=left, 2=right, 3=up
	for row, direction in enumerate(('down', 'left', 'right', 'up')):
		new_dict[direction] = [frame_dict[(col, row)] for col in range(cols)]
		new_dict[f'{direction}_idle'] = [frame_dict[(0, row)]]
	return new_dict

# loads all character tilemaps in a folder and generates animation dictionaries
def all_character_import(*path):
	new_dict = {}
	# recursively go thru the directory to find image files
	for _, __, image_names in walk(join(*path)):
		# strip file extension to use as dictionary key
		for image in image_names:
			image_name = image.split('.')[0]
			# import character frames 
			new_dict[image_name] = character_importer(4,4,*path, image_name)
	return new_dict

def tmx_importer(*path): 
	tmx_dict = {}
	for folder_path, sub_folders, file_names in walk(join(*path)):
		for file in file_names:
			tmx_dict[file.split('.')[0]] = load_pygame(join(folder_path, file))
	return tmx_dict

def monster_importer(cols, rows, *path):
	monster_dict = {}
	for folder_path, sub_folders, image_names in walk(join(*path)):
		for image in image_names:
			image_name = image.split('.')[0]
			monster_dict[image_name]= {}
			frame_dict = import_tilemap(cols, rows, *path, image_name)
			for row, key in enumerate(('idle', 'attack')):
				monster_dict[image_name][key] = [frame_dict[(col, row)] for col in range(cols)]
	return monster_dict

def outline_creator(frame_dict, width):
    return frame_dict

# game functions 
def check_connections(radius, entity, target, tolerance = 30):
	relation = vector(target.rect.center) - vector(entity.rect.center)
	if relation.length() < radius:
		if entity.facing_direction == 'left' and relation.x < 0 and abs(relation.y) < tolerance or\
		   entity.facing_direction == 'right' and relation.x > 0 and abs(relation.y) < tolerance or\
		   entity.facing_direction == 'up' and relation.y < 0 and abs(relation.x) < tolerance or\
		   entity.facing_direction == 'down' and relation.y > 0 and abs(relation.x) < tolerance:
			return True
		
def draw_bar(surface, rect, value, max_value, color, bg_color, radius = 1):
	ratio = rect.width / max_value 
	bg_rect = rect.copy()
	progress = max(0, min(rect.width, value * ratio))
	progress_rect = pygame.FRect(rect.topleft, (progress, rect.height))
	pygame.draw.rect(surface, bg_color, bg_rect, 0, radius)
	pygame.draw.rect(surface, color, progress_rect, 0, radius)
