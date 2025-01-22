// check the biome at a block position
#include "generator.h"
#include "finders.h"
#include <stdio.h>
#include <unistd.h>
#include <inttypes.h>

uint64_t getnumber() {
	uint64_t number;
	scanf("%" SCNu64, &number);
	return number;
}

int main()
{

	// Set up a biome generator that reflects the biome generation of
	// Minecraft 1.18.
	Generator g;
	setupGenerator(&g, MC_1_21_WD, 0);

	// Seeds are internally represented as unsigned 64-bit integers.
	uint64_t seed = getnumber();
	// (get dimension)
	uint64_t dim = getnumber();
	// Apply the seed to the generator for the Overworld dimension.
	if (dim == 0) applySeed(&g, DIM_OVERWORLD, seed);
	if (dim ==  1) applySeed(&g, DIM_END     , seed);
	if (dim == -1) applySeed(&g, DIM_NETHER  , seed);
	// get instructions
	uint64_t instruction = getnumber();
	while (instruction != 0) {
		if (instruction == 1) {
			// To get the biome at a single block position, we can use getBiomeAt().
			int scale = 1; // scale=1: block coordinates, scale=4: biome coordinates
			int x = getnumber(), y = 63, z = getnumber();
			int biomeID = getBiomeAt(&g, scale, x, y, z);
			// random stuff
			if (biomeID == river) printf("river\n");
			else if (biomeID == forest) printf("forest\n");
			else if (biomeID == cherry_grove) printf("cherry_grove\n");
			else if (biomeID == pale_garden) printf("pale_garden\n");
			else if (biomeID == plains) printf("plains\n");
			else if (biomeID == taiga) printf("taiga\n");
			else if (biomeID == stone_shore) printf("stony_shore\n");
			else if (biomeID == meadow) printf("meadow\n");
			else if (biomeID == beach) printf("beach\n");
			else if (biomeID == jungle) printf("jungle\n");
			else if (biomeID == dark_forest) printf("dark_forest\n");
			else if (biomeID == birch_forest) printf("birch_forest\n");
			else if (biomeID == tall_birch_forest) printf("tall_birch_forest\n");
			// ocean variants
			else if (biomeID == ocean) printf("ocean\n");
			else if (biomeID == cold_ocean) printf("cold_ocean\n");
			else if (biomeID == warm_ocean) printf("warm_ocean\n");
			else if (biomeID == deep_ocean) printf("deep_ocean\n");
			else if (biomeID == deep_cold_ocean) printf("deep_cold_ocean\n");
			else if (biomeID == deep_warm_ocean) printf("deep_warm_ocean\n");
			else if (biomeID == frozen_ocean) printf("frozen_ocean\n");
			else if (biomeID == deep_frozen_ocean) printf("deep_frozen_ocean\n");
			else if (biomeID == deep_lukewarm_ocean) printf("deep_lukewarm_ocean\n");
			// other
			else printf("other/%d\n", biomeID);
			fflush(stdout);
		} else if (instruction == 2) {
			Pos spawn = estimateSpawn(&g, NULL);
			printf("%d\n%d\n", spawn.x, spawn.z);
			fflush(stdout);
		} else if (instruction == 3) {
			Pos pos;
			int regionX = getnumber(), regionZ = getnumber();
			int structure[] = { Desert_Pyramid, Jungle_Temple, Swamp_Hut, Igloo, Village,
				Ocean_Ruin, Shipwreck, Monument, Mansion, Outpost, Ruined_Portal, Ruined_Portal_N,
				Ancient_City, Treasure, Mineshaft, Desert_Well, Geode, Trail_Ruins, Trial_Chambers };
				//Fortress, Bastion, End_City, End_Gateway, End_Island
			char *names[] = { "desert_pyramid", "2", "swamp_hut", "igloo", "village",
				"ocean_ruin", "shipwreck", "ocean_monument", "mansion", "10", "ruined_portal", "ruined_portal",
				"ancient_city", "14", "mineshaft", "16", "amethyst_geode", "trail_ruins", "trial_chambers" };
			// village variants: { plains, desert, savanna, taiga, snowy_tundra }
			for (int i = 0; i < sizeof(structure) / sizeof(structure[0]); i++) {
				getStructurePos(structure[i], MC_1_21_WD, seed, regionX, regionZ, &pos);
				int meta = 1;
				if (structure[i] == Village) {
					meta = 5;
				}
				for (int j = 0; j < meta; j++) {
					if (isViableStructurePos(structure[i], &g, pos.x, pos.z, j)) printf("%s\n%d\n%d\n", names[i], pos.x, pos.z);
				}
			}
			printf("end\n");
			fflush(stdout);
		}
		instruction = getnumber();
	}

	return 0;
}
