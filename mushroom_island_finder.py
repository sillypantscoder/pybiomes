import library as mc

island_dist = 150
island_positions: list[mc.PosXZ] = []
for x in [-1, 0, 1]:
	for z in [-1, 0, 1]:
		island_positions.append(mc.PosXZ(x*island_dist, z*island_dist))

class MushroomSeedFinder(mc.SeedFinder):
	def __init__(self, start_seed: int, end_seed: int):
		super().__init__(start_seed, end_seed)
		self.confirm = "possible mushroom island near spawn"
	@staticmethod
	def create():
		return MushroomSeedFinder(0, 0)
	def is_seed_good(self, world: mc.MCWorld):
		# biomes that may be mushroom island
		j = False
		for biome in world.getBiomesAt(island_positions):
			if biome == "mushroom_island":
				j = True
		if j:
			spawn = world.getSpawnPoint()
			if spawn.length() > island_dist * 0.5:
				return None
			return f"Spawn: {spawn}"
		else: return None

if __name__ == "__main__":
	seed =     0
	end_seed = 5000000
	finder = MushroomSeedFinder(seed, end_seed)
	finder.run()
