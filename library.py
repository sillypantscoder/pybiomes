import subprocess
import typing
import math
from intersecting_squares import get_intersecting_unit_squares as _get_intersecting_unit_squares
import os

class CFileLock:
	def __init__(self):
		fn = f"biome_finder_out_{round(os.times().elapsed*100)}.out"
		self.filename: str | None = fn
		subprocess.run(["cp", "../example_find_biome_at.c", "./example_find_biome_at.c"], cwd=os.path.join(os.getcwd(), "cubiomes"))
		subprocess.run(["gcc", "example_find_biome_at.c", "libcubiomes.a", "-fwrapv", "-lm", "-o", "../"+fn], cwd=os.path.join(os.getcwd(), "cubiomes"))
		subprocess.run(["rm", "example_find_biome_at.c"], cwd=os.path.join(os.getcwd(), "cubiomes"))
	def __del__(self):
		if self.filename == None: return
		print("[deleting temporary out file]")
		os.remove(self.filename)
		self.filename = None
_out_file = CFileLock()

class PosXZ:
	def __init__(self, x: int, z: int):
		self.x = x
		self.z = z
	def __add__(self, other: "PosXZ"):
		return PosXZ(self.x + other.x, self.z + other.z)
	def __sub__(self, other: "PosXZ"):
		return PosXZ(self.x - other.x, self.z - other.z)
	def __abs__(self):
		return PosXZ(abs(self.x), abs(self.z))
	def length(self):
		return math.sqrt((self.x * self.x) + (self.z * self.z))
	def __repr__(self):
		return f"PosXZ({self.x}, {self.z})"

class Structure:
	def __init__(self, pos: PosXZ, typeID: str):
		self.pos = pos
		self.typeID = typeID
	def __repr__(self):
		return f"Structure({self.pos}, {self.typeID})"

class MCWorld:
	def __init__(self, seed: int, dimension: typing.Literal[-1, 0, 1]):
		if _out_file.filename == None: raise AssertionError("biome finder file is missing!")
		self.p: subprocess.Popen[bytes] | None = subprocess.Popen(["./" + _out_file.filename], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		# write seed, dimension
		self.send(seed)
		self.send(dimension)

	def send(self, instruction: int):
		if self.p == None: raise AssertionError("process is missing")
		if self.p.stdin == None: raise AssertionError("standard in is missing")
		self.p.stdin.write(str(instruction).encode("UTF-8") + b" ")
		self.p.stdin.flush()

	def readline(self):
		if self.p == None: raise AssertionError("process is missing")
		if self.p.stdout == None: raise AssertionError("standard out is missing")
		line = self.p.stdout.readline()[:-1]
		# print(line)
		return line

	def getBiomeAt(self, blockPos: PosXZ):
		self.send(1)
		self.send(blockPos.x)
		self.send(blockPos.z)
		biome = self.readline()
		return biome.decode("UTF-8")

	def getSpawnPoint(self):
		self.send(2)
		x = int(self.readline())
		z = int(self.readline())
		return PosXZ(x, z)

	def getStructuresInRegion(self, regionX: int, regionZ: int):
		"""Get all the structures between (regionX*512, regionZ*512) and ((regionX+1)*512, (regionZ+1)*512)."""
		structures: list[Structure] = []
		self.send(3)
		self.send(regionX)
		self.send(regionZ)
		structType = self.readline()
		while structType != b"end":
			x = int(self.readline())
			z = int(self.readline())
			structures.append(Structure(PosXZ(x, z), structType.decode("UTF-8")))
			structType = self.readline()
		return structures

	def getStructuresInRegionsMatching(self, regions: list[PosXZ], filter: typing.Callable[[ Structure ], bool]):
		structures: list[Structure] = []
		for r in regions:
			self.send(3)
			self.send(r.x)
			self.send(r.z)
			structType = self.readline()
			while structType != b"end":
				x = int(self.readline())
				z = int(self.readline())
				structure = Structure(PosXZ(x, z), structType.decode("UTF-8"))
				if filter(structure): structures.append(structure)
				structType = self.readline()
		return structures

	def getStructuresInRadius(self, center: PosXZ, radius: int):
		regions: list[PosXZ] = [PosXZ(x[0] * 512, x[1] * 512) for x in _get_intersecting_unit_squares(
			center.x / 512, center.z / 512, radius / 512
		)]
		structures = self.getStructuresInRegionsMatching(regions, lambda structure : abs(structure.pos - center).length() < radius)
		return structures

	def discard(self):
		if self.p == None: return
		try:
			self.send(0)
			self.p.wait()
			self.p = None
		except BrokenPipeError:
			# subprocess is killed if the user presses ctrl-c.
			# so it's probably fine.
			print("[broken pipe from MCWorld]")

	def __del__(self):
		self.discard()

if __name__ == "__main__":
	seed = 300000
	end_seed = 350000
	done = False
	information = []
	interesting = False
	while not done:
		# print information
		if interesting: print(*information, sep="")
		information = [f"for seed: {seed}"]
		interesting = False
		if seed > end_seed: done = True
		# make world
		seed += 1
		world = MCWorld(seed, 0)
		# spawn point
		spawnPos = world.getSpawnPoint()
		dist = spawnPos.length()
		# print(f"[Spawn:{spawnPos.x} {spawnPos.z} {round(dist)}]", end="")
		if dist > 20:
			information.append(f" - spawn failed ({round(dist)})")
			continue
		else:
			information.append(f" - spawn success ({round(dist)})")
		# biomes
		# positions = [PosXZ(-35, -35), PosXZ(35, -35), PosXZ(-35, 35), PosXZ(35, 35)]
		# biome_count = 0
		# for pos in positions:
		# 	biome = world.getBiomeAt(pos)
		# 	if biome == "cherry_grove":
		# 		biome_count += 1
		# if biome_count < len(positions):
		# 	print(f" - biomes failed ({biome_count})")
		# 	continue
		# else:
		# 	print(f" - biomes success ({biome_count})", end="")
		# structures
		structures = world.getStructuresInRadius(spawnPos, 75)
		correct = 0
		for s in structures:
			if s.typeID == "village":
				correct += 1
		if correct > 0: interesting = True
		if correct < 3:
			information.append(f" - structures failed ({correct})")
			continue
		else:
			information.append(f" - structures success ({correct})")
		# finish
		done = True
		interesting = True
		print()
	# print last information
	print("Finished", "(interesting)" if interesting else "(boring)", "at seed", seed)
	if interesting:
		print(*information, sep="")
