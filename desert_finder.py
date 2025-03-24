import library as mc

step = 50
desert_dist = step*6
desert_positions1d = [*range(-desert_dist, desert_dist + step, step)]
desert_positions: list[mc.PosXZ] = []
for x in desert_positions1d:
	for z in desert_positions1d:
		desert_positions.append(mc.PosXZ(x, z))

class DesertSeedFinder(mc.SeedFinder):
	def __init__(self, start_seed: int, end_seed: int):
		super().__init__(start_seed, end_seed)
		self.confirm = "desert around spawn"
	@staticmethod
	def create():
		return DesertSeedFinder(0, 0)
	def is_seed_good(self, world: mc.MCWorld):
		if world.getBiomeAt(mc.PosXZ(0, 0)) != "desert": return None
		# biomes that must be desert
		for biome in world.getBiomesAt(desert_positions):
			if biome != "desert":
				return None
		# spawn
		spawn = world.getSpawnPoint()
		if spawn.length() > desert_dist * 0.1:
			return None
		# villages
		structures = world.getStructuresInRegionsMatching([
			mc.PosXZ( 0,  0),
			mc.PosXZ(-1,  0),
			mc.PosXZ( 0, -1),
			mc.PosXZ(-1, -1)
		], lambda s: True)
		closest: mc.PosXZ = mc.PosXZ(-100000, -100000)
		for s in structures:
			if s.typeID != "village":
				continue
			if s.pos.length() < 410:
				# Village is too close!
				return None
			elif s.pos.length() < closest.length():
				closest.x = s.pos.x
				closest.z = s.pos.z
		return f"Spawn: {spawn}\nClosest village: X {closest.x} Z {closest.z} ({round(closest.length())} blocks away)"

if __name__ == "__main__":
	seed =     10000000000
	end_seed = 10100000000
	finder = DesertSeedFinder(seed, end_seed)
	finder.run()
