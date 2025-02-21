import subprocess
import sys
import typing
import inspect
import json
import math
import time

# FOR PARENT PROCESSES

def get_caller_file_path():
	# Get the caller's stack frame (the one that imported this module)
	caller_frame = inspect.stack()[-1]
	return caller_frame.filename

class Copiable:
	@staticmethod
	def create() -> "Copiable":
		raise RuntimeError("create method in copiable object needs to be overridden.")
	def runTask(self, data: str) -> None:
		raise RuntimeError("runTask method in copiable object needs to be overridden. Data: " + repr(data))

class Process:
	def __init__(self, clazz: typing.Type[Copiable] | str, tasks: list[str]):
		classname = clazz if isinstance(clazz, str) else clazz.__name__
		self.process = subprocess.Popen([sys.executable, __file__, get_caller_file_path(), classname], stdin=subprocess.PIPE)
		if self.process.stdin == None: raise ValueError("it doesn't exist ?????")
		taskData = json.dumps(tasks).encode("UTF-8") + b"\n\n"
		# print("Task data:", repr(taskData))
		self.process.stdin.write(taskData)
		self.process.stdin.flush()
	def is_alive(self):
		return self.process.poll() == None
	def wait(self):
		self.process.wait()
	def __del__(self):
		if self.process.poll() == None:
			self.process.kill()
		self.process.wait()

def pool(clazz: typing.Type[Copiable] | str, tasks: list[str], progress_callback: typing.Callable[[ int, int, int ], None], max_processes: int = 3):
	chunks: list[list[str]] = []
	chunk_size = math.ceil(len(tasks) / (max_processes * 10))
	chunk_size = 50000
	for t in tasks:
		if len(chunks) == 0 or len(chunks[-1]) >= chunk_size:
			chunks.append([])
		chunks[-1].append(t)
	totalChunks = len(chunks)
	completed = 0
	progress_callback(chunk_size, completed, totalChunks)
	# Run one process for each chunk
	processes: list[Process] = []
	def poll_processes(target_processes: int):
		rm: list[Process] = []
		for p in processes:
			if not p.is_alive():
				rm.append(p)
		for p in rm: finish(p)
		# print("[", len(processes), "/", target_processes, "]", sep="", end="", flush=True)
	def finish(p: Process):
		nonlocal completed
		processes.remove(p)
		# Progress
		completed += 1
		progress_callback(chunk_size, completed, totalChunks)
	while len(chunks) > 0:
		while len(processes) >= max_processes:
			time.sleep(1)
			# Poll all the processes
			poll_processes(max_processes)
		chunk = chunks[0]
		processes.append(Process(clazz, chunk))
		chunks.remove(chunk)
		poll_processes(max_processes)
	while len(processes) > 0:
		time.sleep(1)
		# Poll all the processes
		poll_processes(0)

# FOR CHILD PROCESSES

def get_module(filepath: str):
	import importlib.util
	spec = importlib.util.spec_from_file_location("seed_finder_main", filepath)
	if spec == None: raise FileNotFoundError(filepath)
	module = importlib.util.module_from_spec(spec)
	if spec.loader == None: raise FileNotFoundError("loader is missing")
	spec.loader.exec_module(module)
	return module

def runTasks(clazz: typing.Type[Copiable]):
	obj = clazz.create()
	tasks = json.loads(input())
	for task in tasks:
		obj.runTask(task)

if __name__ == "__main__":
	module = get_module(sys.argv[1])
	try:
		clazz: typing.Type[Copiable] = getattr(module, sys.argv[2])
		# We have totally re-created the `clazz` object (from line 23)
		# Now, execute the tasks
		runTasks(clazz)
	except AttributeError:
		print("Cannot find the requested class in the module:", sys.argv[2])
