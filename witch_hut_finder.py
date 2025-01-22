import library as mc

biome_test_dist = 50
biome_test_positions: list[mc.PosXZ] = []
for x in [-biome_test_dist, 0, biome_test_dist]:
	for z in [-biome_test_dist, 0, biome_test_dist]:
		biome_test_positions.append(mc.PosXZ(x, z))

seed =     15000000
end_seed = 35000000
while seed <= end_seed:
	if seed % 1000 == 0: print(f"[checked {seed} seeds...]")
	seed += 1
	# make world
	world = mc.MCWorld(seed, 0)
	# spawn point
	spawnPos = world.getSpawnPoint()
	dist = spawnPos.length()
	if dist > 30: continue
	# biomes
	correctBiomes = 0
	for pos in biome_test_positions:
		biome = world.getBiomeAt(pos)
		if biome == "swamp":
			correctBiomes += 1
	if correctBiomes < 3: continue
	# structures
	structures = world.getStructuresInRadius(mc.PosXZ(0, 0), 70)
	correctStructs: list[mc.PosXZ] = []
	for s in structures:
		if s.typeID == "swamp_hut":
			correctStructs.append(s.pos)
	if len(correctStructs) <= 0: continue
	# finish
	f = open("seeds.txt", "a")
	f.write(f"\n\n\n\nFound swamp hut! for seed: {seed}\n")
	for pos in biome_test_positions:
		biome = world.getBiomeAt(pos)
		f.write(f"- X: {pos.x} Z: {pos.z} Biome: {biome}\n")
	for pos in correctStructs:
		f.write(f"- Swamp Hut at X: {pos.x} Z: {pos.z}\n")
	f.close()
