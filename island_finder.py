import library as mc

biome_test_dist = 250
biome_test_positions: list[mc.PosXZ] = []
for x in [-biome_test_dist, 0, biome_test_dist]:
	for z in [-biome_test_dist, 0, biome_test_dist]:
		if x == 0 and z == 0: continue
		biome_test_positions.append(mc.PosXZ(x, z))

class IslandSeedFinder(mc.SeedFinder):
	def __init__(self, start_seed: int, end_seed: int):
		super().__init__(start_seed, end_seed)
		self.confirm = "possible village island spawn"
	def is_seed_good(self, world: mc.MCWorld):
		# biomes
		for pos in biome_test_positions:
			biome = world.getBiomeAt(pos)
			if "ocean" not in biome:
				return None
			if "frozen" in biome:
				return None
		# spawn point
		spawnPos = world.getSpawnPoint()
		dist = spawnPos.length()
		if dist > 30: return None
		# structures
		structures = world.getStructuresInRadius(mc.PosXZ(0, 0), 100)
		correctStructs: list[mc.PosXZ] = []
		for s in structures:
			if s.typeID == "village":
				correctStructs.append(s.pos)
		if len(correctStructs) <= 0: return None
		# yay
		return "It worked"

seed =     13000000
end_seed = 13001000
finder = IslandSeedFinder(seed, end_seed)
finder.run()
