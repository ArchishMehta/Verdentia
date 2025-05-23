from settings import *
from os.path import join
from os import walk
from pytmx.util_pygame import load_pygame

# imports
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
		'topleft': (0, 0), 'top': (1, 0), 'topright': (2, 0), 
		'left': (0, 1), 'right': (2, 1), 'bottomleft': (0, 2), 
		'bottom': (1, 2), 'bottomright': (2, 2)
	}
	# for loop for every terrain type build nested dictionary of side variations
	for index, terrain in enumerate(terrains):
		new_dict[terrain] = {}

		for key, pos in sides.items():
			# get all variations down the vertical axis (every 3 rows)
			new_dict[terrain][key] = [frame_dict[(pos[0] + index * 3, pos[1] + row)] for row in range(0, rows, 3)]
	return new_dict