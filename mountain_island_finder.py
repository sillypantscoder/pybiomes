import library as mc

not_ocean_dist = 150
not_ocean_positions: list[mc.PosXZ] = []
is_ocean_dist = [300, 350, 400]
is_ocean_positions: list[mc.PosXZ] = []
for x in [-1, 0, 1]:
	for z in [-1, 0, 1]:
		not_ocean_positions.append(mc.PosXZ(x*not_ocean_dist, z*not_ocean_dist))
		if x == 0 and z == 0: continue
		for d in is_ocean_dist:
			is_ocean_positions.append(mc.PosXZ(x * d, z * d))

class MountainIslandSeedFinder(mc.SeedFinder):
	def __init__(self, start_seed: int, end_seed: int):
		super().__init__(start_seed, end_seed)
		self.confirm = "possible MOUNTAIN island spawn"
	@staticmethod
	def create():
		return MountainIslandSeedFinder(0, 0)
	def is_seed_good(self, world: mc.MCWorld):
		# biomes that should be ocean
		validity = 0
		for biome in world.getBiomesAt(is_ocean_positions):
			if "ocean" not in biome:
				validity -= 0.5
		# biomes that should not be ocean
		j = False
		for biome in world.getBiomesAt(not_ocean_positions):
			if "ocean" in biome:
				validity -= 0.75
			if biome == "jagged_peaks":
				validity += 0.25
				j = True
		if j: validity += 3
		if validity >= 2.75:
			return f"Validity: {validity}"
		else: return None

if __name__ == "__main__":
	seed =     1580000000
	end_seed = 1640000000
	finder = MountainIslandSeedFinder(seed, end_seed)
	finder.run()
