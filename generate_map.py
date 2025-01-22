import library as mc
import pygame
import threading
import typing
import math

seed = 2845528

# make image
img_size = 600
img_scale = 2
img = pygame.Surface((img_size, img_size))
img.fill((128, 128, 128))

I2C: typing.Callable[[ int ], int] = lambda x: (x - (img_size // 2)) * img_scale
C2I: typing.Callable[[ int ], int] = lambda x: (x // img_scale) + (img_size // 2)

# biomes
biomes: list[list[str]] = []
def map_seed():
	world = mc.MCWorld(seed, 0)
	unknown_biomes: list[str] = []
	amt_done = 0
	for z in range(img_size):
		row: list[str] = []
		biomes.append(row)
		for x in range(img_size):
			loc = mc.PosXZ(I2C(x), I2C(z))
			biome = world.getBiomeAt(loc)
			row.append(biome)
			color = (128, 128, 128)
			if "ocean" in biome:
				_color = [0, 0, 100]
				if "warm" in biome: _color[0] += 32
				if "luke" in biome: _color[0] -= 16
				if "cold" in biome: _color[0] += 32; _color[1] += 32; _color[2] += 32
				if "deep" in biome: _color[0] //= 2; _color[1] //= 2; _color[2] //= 2
				color = (_color[0], _color[1], _color[2])
			elif biome == "plains": color = (128-64, 255-64, 128-64)
			elif biome == "river": color = (0, 0, 255)
			elif biome == "forest": color = (0, 128, 0)
			elif biome == "stony_shore": color = (150, 150, 150)
			elif biome == "taiga": color = (100, 200, 200)
			elif biome == "beach": color = (230, 180, 0)
			elif biome == "jungle": color = (0, 255, 64)
			elif biome == "dark_forest": color = (128, 64, 0)
			elif biome == "birch_forest": color = (180, 180, 230)
			elif biome == "tall_birch_forest": color = (200, 200, 255)
			elif biome not in unknown_biomes:
				print(f"[unknown biome: {biome}]")
				unknown_biomes.append(biome)
			img.set_at((x, z), color)
			amt_done += 1
		# if z % 20 == 0: print(f"[{round(100*amt_done/(img_size*img_size), 2)}% done...]")
	# print(f"[finished mapping]")
	world.discard()
	pygame.image.save(img, "generated_map.png")
threading.Thread(target=map_seed, name="mapping_thread", args=()).start()

def getSpawnPoint():
	world = mc.MCWorld(seed, 0)
	pos = world.getSpawnPoint()
	world.discard()
	return pos

# spawn point
spawnPos = getSpawnPoint()

def getStructures():
	world = mc.MCWorld(seed, 0)
	structures = world.getStructuresInRadius(mc.PosXZ(0, 0), img_size)
	world.discard()
	return structures

# structures
structures = getStructures()
unknown_structures: list[str] = []

# display
pygame.font.init()
font_size = 16
font = pygame.font.SysFont(pygame.font.get_default_font(), font_size)

mousePos: tuple[int, int] = (img_size + 5, img_size + 5)

screen = pygame.display.set_mode((img_size, img_size + font_size))

running = True
c = pygame.time.Clock()
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.MOUSEMOTION:
			mousePos = (event.pos[0], event.pos[1])
	screen.fill((255, 255, 255))
	# biomes
	screen.blit(img, (0, 0))
	# spawn pos
	pygame.draw.circle(screen, (255, 255, 255), (
		C2I(spawnPos.x),
		C2I(spawnPos.z)
	), 16)
	pygame.draw.circle(screen, (0, 0, 0), (
		C2I(spawnPos.x),
		C2I(spawnPos.z)
	), 16, 1)
	# structures
	for s in structures:
		color = (128, 128, 128)
		rad = 4
		if s.typeID == "village": color = (255, 128, 0); rad = 16
		elif s.typeID == "shipwreck": color = (64, 32, 0); rad = 8
		elif s.typeID == "ruined_portal": color = (255, 0, 255)
		elif s.typeID == "mineshaft": color = (128, 64, 0)
		elif s.typeID == "amethyst_geode": color = (128, 0, 255)
		elif s.typeID == "trial_chambers": color = (255, 128, 0)
		elif s.typeID == "ocean_monument": color = (64, 255, 128); rad = 8
		elif s.typeID == "ocean_ruin": color = (0, 64, 64)
		elif s.typeID not in unknown_structures:
			print("unknown structure type: " + s.typeID)
			unknown_structures.append(s.typeID)
		pygame.draw.circle(screen, color, (
			C2I(s.pos.x),
			C2I(s.pos.z)
		), rad)
		pygame.draw.circle(screen, (0, 0, 0), (
			C2I(s.pos.x),
			C2I(s.pos.z)
		), rad, 1)
	# text
	try:
		textStr = biomes[mousePos[1]][mousePos[0]]
		if math.dist((I2C(mousePos[0]), I2C(mousePos[1])), (spawnPos.x, spawnPos.z)) < 16: textStr += " (Spawn)"
		for s in structures:
			if math.dist((I2C(mousePos[0]), I2C(mousePos[1])), (s.pos.x, s.pos.z)) < 16: textStr += " (Structure: " + s.typeID + ")"
		text = font.render(textStr, True, (0, 0, 0))
		screen.blit(text, (0, img_size))
	except IndexError:
		pass
	# update
	pygame.display.flip()
	c.tick(60)

# discard

del mc._out_file # type: ignore
