import library as mc

biome_test_dist = 50
biome_test_positions: list[mc.PosXZ] = []
for x in [-biome_test_dist, 0, biome_test_dist]:
	for z in [-biome_test_dist, 0, biome_test_dist]:
		biome_test_positions.append(mc.PosXZ(x, z))

class WitchHutSeedFinder(mc.SeedFinder):
	def __init__(self, start_seed: int, end_seed: int):
		super().__init__(start_seed, end_seed)
		self.confirm = "swamp hut spawn"
	def is_seed_good(self, world: mc.MCWorld) -> str | None:
		# biomes
		incorrectBiomes = 0
		for pos in biome_test_positions:
			biome = world.getBiomeAt(pos)
			if biome != "swamp":
				incorrectBiomes += 1
				if incorrectBiomes >= 4: return
		# spawn point
		spawnPos = world.getSpawnPoint()
		dist = spawnPos.length()
		if dist > 30: return
		# structures
		structures = world.getStructuresInRadius(mc.PosXZ(0, 0), 70)
		correctStructs: list[mc.PosXZ] = []
		for s in structures:
			if s.typeID == "swamp_hut":
				correctStructs.append(s.pos)
		if len(correctStructs) <= 0: return
		# finish
		data = ""
		for pos in biome_test_positions:
			biome = world.getBiomeAt(pos)
			data += f"\n- X: {pos.x} Z: {pos.z} Biome: {biome}"
		for pos in correctStructs:
			data += f"\n- Swamp Hut at X: {pos.x} Z: {pos.z}"
		return data+"\n\n"

seed =     0
end_seed = 1000000
finder = WitchHutSeedFinder(seed, end_seed)
finder.run()
