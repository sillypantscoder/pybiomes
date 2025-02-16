import subprocess
import typing
import math
from intersecting_squares import get_intersecting_unit_squares as _get_intersecting_unit_squares
import os
import datetime
import multiprocessing_alt as multi
import random

class BiomeFinderProcess(typing.TypedDict):
	process: subprocess.Popen[bytes]
	claimed: bool

class SubprocessManager:
	def __init__(self):
		managerID = random.randint(0, 100000000)
		fn = f"biome_finder_out_{managerID}.out"
		self.out_filename: str | None = fn
		subprocess.run(["cp", "../example_find_biome_at.c", f"./example_find_biome_at_{managerID}.c"], cwd=os.path.join(os.getcwd(), "cubiomes"))
		subprocess.run(["gcc", f"example_find_biome_at_{managerID}.c", "libcubiomes.a", "-fwrapv", "-lm", "-o", "../"+fn], cwd=os.path.join(os.getcwd(), "cubiomes"))
		subprocess.run(["rm", f"example_find_biome_at_{managerID}.c"], cwd=os.path.join(os.getcwd(), "cubiomes"))
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
		# print(f"[deleting temporary out file]")
		os.remove(self.out_filename)
		self.out_filename = None
		# print(f"[killing {len(self.processes)} processes]")
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

	def getBiomesAt(self, positions: list[PosXZ]):
		for pos in positions:
			self.send(2)
			self.send(pos.x)
			self.send(pos.z)
		biomes = [self.readline().decode("UTF-8") for _ in positions]
		return biomes

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

# seeds/second per thread
assumed_seed_checking_rate = 1100

processes = 3

def _fmt_time(total_seconds: float):
	mins = round(total_seconds // 60)
	hrs = round(mins // 60)
	secs = round(total_seconds - (mins * 60))
	mins -= hrs * 60
	return f"{hrs}h {mins}m {secs}s"

def _fmt_n(n: int) -> str:
	return "{:,}".format(n).replace(",", " ")

class SeedFinder(multi.Copiable):
	def __init__(self, start_seed: int, end_seed: int):
		self.start_seed = start_seed
		self.end_seed = end_seed
		self.stats()
		self.start_time = datetime.datetime.now()
		self.confirm = "something"
	def stats(self):
		amt = self.end_seed - self.start_seed
		if amt == 0: return
		total_seconds = amt / (assumed_seed_checking_rate * processes)
		print(f"{_fmt_n(amt)} seeds to check, expected time {_fmt_time(total_seconds)}")
	def run(self):
		self.start_time = datetime.datetime.now()
		# Make seed list
		seeds: list[str] = []
		seed = self.start_seed
		while seed <= self.end_seed:
			seeds.append(str(seed))
			seed += 1
		# Run all the checkers
		try:
			multi.pool(self.__class__.__name__, seeds, self.updateProgress, processes)
		except KeyboardInterrupt:
			print("\nStopping early due to KeyboardInterrupt! Output statistics are probably not accurate!")
		# Times
		end_time = datetime.datetime.now()
		diff = (end_time - self.start_time).total_seconds()
		ms_per_seed = 1000 * diff / (self.end_seed - self.start_seed)
		print(f"Total time taken: {diff}s or {_fmt_time(diff)}")
		print(f"Average ms per seed: {ms_per_seed}")
		print(f"Average seeds per second: {1000/ms_per_seed}")
		print(f"Average seeds per second per thread: {(1000/ms_per_seed)/processes}")
		# Calculate new initial checking rate
		per_thread = ((self.end_seed - self.start_seed) / processes) / diff
		avg = (assumed_seed_checking_rate + per_thread) / 2
		print(f"New avg checking rate: {avg}")
	def updateProgress(self, chunk_size: int, completed: int, total: int):
		# find eta
		seconds_elapsed = (datetime.datetime.now() - self.start_time).total_seconds()
		seed_checking_rate = (completed * chunk_size) / seconds_elapsed
		if seed_checking_rate == 0: seed_checking_rate = assumed_seed_checking_rate * processes
		seeds_left = (total - completed) * chunk_size
		total_seconds = seeds_left / seed_checking_rate
		# Print data
		print(f"[lib reports {completed}/{total} x{chunk_size}; probably about {round(100*(completed/total), 2)}% done? " +
			f"Speed: {round(seed_checking_rate)} seeds/second or {round(seed_checking_rate/processes)} seeds/second/process; ETA: {_fmt_time(total_seconds)}]",
			end="\n", flush=True)
	def runTask(self, data: str):
		seed = int(data)
		# make world
		world = MCWorld(seed, 0)
		# check the seed
		valid = False
		try:
			valid = self.is_seed_good(world)
		except KeyboardInterrupt:
			return
		if valid != None:
			# save this!
			display = valid.replace("\n", "\n\t")
			f = open("seeds.txt", "a")
			f.write(f"\n\n\n\nFound {self.confirm} for seed: {seed}\n")
			f.write(f"data:\n{display}")
			f.close()
			print(f"[found result for seed: {seed}]")
	def is_seed_good(self, world: MCWorld) -> str | None:
		return None
