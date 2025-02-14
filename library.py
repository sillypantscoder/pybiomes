import subprocess
import typing
import math
from intersecting_squares import get_intersecting_unit_squares as _get_intersecting_unit_squares
import os
import datetime
import threading
import multiprocessing
import time

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

seed_finder_queues: "dict[int, multiprocessing.Queue[int]]" = {}
seed_finder_cancellation_queues: "dict[int, multiprocessing.Queue[int]]" = {}

# seeds/second per thread
seed_checking_rate = 995

processes = 3

def _fmt_time(total_seconds: float):
	mins = round(total_seconds // 60)
	hrs = round(mins // 60)
	secs = round(total_seconds - (mins * 60))
	mins -= hrs * 60
	return f"{hrs}h {mins}m {secs}s"

def _watch_seedfinder_queue(seedfinder: "SeedFinder"):
	while not seedfinder.ended:
		time.sleep(0.5)
		if seedfinder.ended or seedfinder.id not in seed_finder_queues:
			print("Watcher thread exited")
			return
		if seed_finder_queues[seedfinder.id].empty(): continue
		seed = seed_finder_queues[seedfinder.id].get(True, 1)
		seedfinder.checkpoints_hit += 1
		# find eta
		seconds_elapsed = (datetime.datetime.now() - seedfinder.start_time).total_seconds()
		seed_checking_rate = (seedfinder.checkpoints_hit * seedfinder.checkpoints_amt) / seconds_elapsed
		seeds_left = (seedfinder.checkpoints_total - seedfinder.checkpoints_hit) * seedfinder.checkpoints_amt
		total_seconds = seeds_left / seed_checking_rate
		# print data
		print(f"[finished checking seed: {seed}, " +
			f"probably about {round(100*(seedfinder.checkpoints_hit/seedfinder.checkpoints_total), 2)}% done? " +
			f"Speed: {round(seed_checking_rate)} seeds/second; ETA: {_fmt_time(total_seconds)}]")

class SeedFinder:
	def __init__(self, start_seed: int, end_seed: int):
		self.start_seed = start_seed
		self.end_seed = end_seed
		self.stats()
		self.start_time = datetime.datetime.now()
		self.confirm = "something"
		self.stop_once_found = False
		self.checkpoints_amt = 80000
		self.checkpoints_total = round((self.end_seed - self.start_seed) / self.checkpoints_amt) + 1
		self.checkpoints_hit = 0
		self.ended = False
		self.id = max([0, *seed_finder_queues.keys()]) + 1
		seed_finder_queues[self.id] = multiprocessing.Queue()
		seed_finder_cancellation_queues[self.id] = multiprocessing.Queue()
		threading.Thread(target=_watch_seedfinder_queue, name=f"queue_watcher_{self.id}", args=(self, )).start()
	def stats(self):
		amt = self.end_seed - self.start_seed
		total_seconds = amt / (seed_checking_rate * processes)
		print(f"{amt} seeds to check, expected time {_fmt_time(total_seconds)}")
	def run(self):
		self.start_time = datetime.datetime.now()
		# Make seed list
		seeds: list[int] = []
		seed = self.start_seed
		while seed <= self.end_seed:
			seeds.append(seed)
			seed += 1
		# Run all the checkers
		pool = multiprocessing.Pool(processes=processes)
		try:
			pool.map(self.check_seed, seeds)
		except KeyboardInterrupt:
			print("Stopping early due to KeyboardInterrupt")
		pool.close()
		# Signal ended
		self.ended = True
		if self.id in seed_finder_queues.keys():
			del seed_finder_queues[self.id]
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
		avg = (seed_checking_rate + per_thread) / 2
		print(f"New avg checking rate: {avg}")
	def check_seed(self, seed: int):
		if self.id not in seed_finder_cancellation_queues.keys():
			print("Aaaaa, seed finder was deleted!")
			return
		if not seed_finder_cancellation_queues[self.id].empty(): return
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
			f = open("seeds.txt", "a")
			f.write(f"\n\n\n\nFound {self.confirm} for seed: {seed}\n")
			f.write(f"data: {valid}")
			f.close()
			print(f"[found result for seed: {seed}]")
			if self.stop_once_found:
				seed_finder_cancellation_queues[self.id].put(seed)
		# seed checkpoints
		if seed % self.checkpoints_amt == 0:
			if self.id not in seed_finder_cancellation_queues.keys():
				print("Aaaaa, seed finder was deleted really fast!")
				return
			seed_finder_queues[self.id].put(seed)
			# print(f"[finished checking seed: {seed}, probably about {round(100*(seed - self.start_seed)/(self.end_seed - self.start_seed), 1)}% done?]")
	def is_seed_good(self, world: MCWorld) -> str | None:
		return None
