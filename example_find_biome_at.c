// check the biome at a block position
#include "biomes.h"
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

const char *stringifyBiome(int biome) {
	switch (biome) {
		case ocean: return "ocean";
		case plains: return "plains";
		case desert: return "desert";
		case mountains: return "mountains";
		case forest: return "forest";
		case taiga: return "taiga";
		case swamp: return "swamp";
		case river: return "river";
		case nether_wastes: return "nether_wastes";
		case the_end: return "the_end";
		case frozen_ocean: return "frozen_ocean";
		case frozen_river: return "frozen_river";
		case snowy_tundra: return "snowy_tundra";
		case snowy_mountains: return "snowy_mountains";
		case mushroom_fields: return "mushroom_fields";
		case mushroom_field_shore: return "mushroom_field_shore";
		case beach: return "beach";
		case desert_hills: return "desert_hills";
		case wooded_hills: return "wooded_hills";
		case taiga_hills: return "taiga_hills";
		case mountain_edge: return "mountain_edge";
		case jungle: return "jungle";
		case jungle_hills: return "jungle_hills";
		case jungle_edge: return "jungle_edge";
		case deep_ocean: return "deep_ocean";
		case stone_shore: return "stone_shore";
		case snowy_beach: return "snowy_beach";
		case birch_forest: return "birch_forest";
		case birch_forest_hills: return "birch_forest_hills";
		case dark_forest: return "dark_forest";
		case snowy_taiga: return "snowy_taiga";
		case snowy_taiga_hills: return "snowy_taiga_hills";
		case giant_tree_taiga: return "giant_tree_taiga";
		case giant_tree_taiga_hills: return "giant_tree_taiga_hills";
		case wooded_mountains: return "wooded_mountains";
		case savanna: return "savanna";
		case savanna_plateau: return "savanna_plateau";
		case badlands: return "badlands";
		case wooded_badlands_plateau: return "wooded_badlands_plateau";
		case badlands_plateau: return "badlands_plateau";
		case small_end_islands: return "small_end_islands";
		case end_midlands: return "end_midlands";
		case end_highlands: return "end_highlands";
		case end_barrens: return "end_barrens";
		case warm_ocean: return "warm_ocean";
		case lukewarm_ocean: return "lukewarm_ocean";
		case cold_ocean: return "cold_ocean";
		case deep_warm_ocean: return "deep_warm_ocean";
		case deep_lukewarm_ocean: return "deep_lukewarm_ocean";
		case deep_cold_ocean: return "deep_cold_ocean";
		case deep_frozen_ocean: return "deep_frozen_ocean";
		case seasonal_forest: return "seasonal_forest";
		case rainforest: return "rainforest";
		case shrubland: return "shrubland";
		case the_void: return "the_void";
		case sunflower_plains: return "sunflower_plains";
		case desert_lakes: return "desert_lakes";
		case gravelly_mountains: return "gravelly_mountains";
		case flower_forest: return "flower_forest";
		case taiga_mountains: return "taiga_mountains";
		case swamp_hills: return "swamp_hills";
		case ice_spikes: return "ice_spikes";
		case modified_jungle: return "modified_jungle";
		case modified_jungle_edge: return "modified_jungle_edge";
		case tall_birch_forest: return "tall_birch_forest";
		case tall_birch_hills: return "tall_birch_hills";
		case dark_forest_hills: return "dark_forest_hills";
		case snowy_taiga_mountains: return "snowy_taiga_mountains";
		case giant_spruce_taiga: return "giant_spruce_taiga";
		case giant_spruce_taiga_hills: return "giant_spruce_taiga_hills";
		case modified_gravelly_mountains: return "modified_gravelly_mountains";
		case shattered_savanna: return "shattered_savanna";
		case shattered_savanna_plateau: return "shattered_savanna_plateau";
		case eroded_badlands: return "eroded_badlands";
		case modified_wooded_badlands_plateau: return "modified_wooded_badlands_plateau";
		case modified_badlands_plateau: return "modified_badlands_plateau";
		case bamboo_jungle: return "bamboo_jungle";
		case bamboo_jungle_hills: return "bamboo_jungle_hills";
		case soul_sand_valley: return "soul_sand_valley";
		case crimson_forest: return "crimson_forest";
		case warped_forest: return "warped_forest";
		case basalt_deltas: return "basalt_deltas";
		case dripstone_caves: return "dripstone_caves";
		case lush_caves: return "lush_caves";
		case meadow: return "meadow";
		case grove: return "grove";
		case snowy_slopes: return "snowy_slopes";
		case jagged_peaks: return "jagged_peaks";
		case frozen_peaks: return "frozen_peaks";
		case stony_peaks: return "stony_peaks";
		case deep_dark: return "deep_dark";
		case mangrove_swamp: return "mangrove_swamp";
		case cherry_grove: return "cherry_grove";
		case pale_garden: return "pale_garden";
	}
	return NULL;
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
			const char* biomeName = stringifyBiome(biomeID);
			if (biomeName != NULL) {
				printf("%s\n", biomeName);
			} else {
				printf("other/%d\n", biomeID);
			}
			// // random stuff
			// if (biomeID == river) printf("river\n");
			// else if (biomeID == forest) printf("forest\n");
			// else if (biomeID == cherry_grove) printf("cherry_grove\n");
			// else if (biomeID == pale_garden) printf("pale_garden\n");
			// else if (biomeID == plains) printf("plains\n");
			// else if (biomeID == taiga) printf("taiga\n");
			// else if (biomeID == stone_shore) printf("stony_shore\n");
			// else if (biomeID == meadow) printf("meadow\n");
			// else if (biomeID == beach) printf("beach\n");
			// else if (biomeID == jungle) printf("jungle\n");
			// else if (biomeID == dark_forest) printf("dark_forest\n");
			// else if (biomeID == birch_forest) printf("birch_forest\n");
			// else if (biomeID == tall_birch_forest) printf("tall_birch_forest\n");
			// // ocean variants
			// else if (biomeID == ocean) printf("ocean\n");
			// else if (biomeID == cold_ocean) printf("cold_ocean\n");
			// else if (biomeID == warm_ocean) printf("warm_ocean\n");
			// else if (biomeID == deep_ocean) printf("deep_ocean\n");
			// else if (biomeID == deep_cold_ocean) printf("deep_cold_ocean\n");
			// else if (biomeID == deep_warm_ocean) printf("deep_warm_ocean\n");
			// else if (biomeID == frozen_ocean) printf("frozen_ocean\n");
			// else if (biomeID == deep_frozen_ocean) printf("deep_frozen_ocean\n");
			// else if (biomeID == deep_lukewarm_ocean) printf("deep_lukewarm_ocean\n");
			// other
			// else printf("other/%d\n", biomeID);
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
