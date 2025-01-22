import subprocess
import typing
import math
from intersecting_squares import get_intersecting_unit_squares as _get_intersecting_unit_squares
import os

class BiomeFinderProcess(typing.TypedDict):
	process: subprocess.Popen[bytes]
	claimed: bool

class SubprocessManager:
	def __init__(self):
		fn = f"biome_finder_out_{round(os.times().elapsed*100)}.out"
		self.out_filename: str | None = fn
		subprocess.run(["cp", "../example_find_biome_at.c", "./example_find_biome_at.c"], cwd=os.path.join(os.getcwd(), "cubiomes"))
		subprocess.run(["gcc", "example_find_biome_at.c", "libcubiomes.a", "-fwrapv", "-lm", "-o", "../"+fn], cwd=os.path.join(os.getcwd(), "cubiomes"))
		subprocess.run(["rm", "example_find_biome_at.c"], cwd=os.path.join(os.getcwd(), "cubiomes"))
		# process list
		self.processes: list[BiomeFinderProcess] = []
	def getProcess(self):
		for p in self.processes:
			if p["claimed"] == False:
				p["claimed"] = True
				# print(f"claimed process #{self.processes.index(p)+1}")
				return p["process"]
		return self.newProcess()
	def newProcess(self):
		if self.out_filename == None: raise AssertionError("Cannot create new processes after subprocess manager is deleted")
		p = subprocess.Popen(["./" + self.out_filename], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		self.processes.append({ "process": p, "claimed": True })
		# print(f"created and claimed process #{len(self.processes)}")
		return p
	def garbageCollectProcess(self, process: subprocess.Popen[bytes]):
		for p in self.processes:
			if p["process"] == process:
				p["claimed"] = False
				# print(f"un-claimed process #{self.processes.index(p)+1}")
	def __del__(self):
		if self.out_filename == None: return
		print(f"[deleting temporary out file]")
		os.remove(self.out_filename)
		self.out_filename = None
		print(f"[killing {len(self.processes)} processes]")
		for p in self.processes:
			proc = p["process"]
			if proc.stdin == None: raise AssertionError("stdin is missing??? you have problems!")
			proc.stdin.write(b"0 ")
			proc.stdin.flush()
			proc.wait()
		self.processes = []
manager = SubprocessManager()

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
		self.p: subprocess.Popen[bytes] | None = manager.getProcess()
		# write seed, dimension
		self.send(1)
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
		self.send(2)
		self.send(blockPos.x)
		self.send(blockPos.z)
		biome = self.readline()
		return biome.decode("UTF-8")

	def getSpawnPoint(self):
		self.send(3)
		x = int(self.readline())
		z = int(self.readline())
		return PosXZ(x, z)

	def getStructuresInRegion(self, regionX: int, regionZ: int):
		"""Get all the structures between (regionX*512, regionZ*512) and ((regionX+1)*512, (regionZ+1)*512)."""
		structures: list[Structure] = []
		self.send(4)
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
			self.send(4)
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
		manager.garbageCollectProcess(self.p)
		self.p = None

	def __del__(self):
		self.discard()

if __name__ == "__main__":
	import threading
	seeds: dict[int, str | None] = { i: None for i in range(10000) }
	def doSomethingClever(seed: int):
		world1 = MCWorld(0, 0)
		biome = world1.getBiomeAt(PosXZ(seed, 0))
		seeds[seed] = biome
	for i in range(10000): threading.Thread(target=doSomethingClever, name=f"asdf{i}", args=(i, )).start()
	import time
	while None in [*seeds.values()]: time.sleep(0.01)
	print("it totally finished! (wow!)")
