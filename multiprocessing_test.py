import multiprocessing_alt as multi
import random
import time

class Something(multi.Copiable):
	def __init__(self):
		self.id = random.randint(0, 100000000)
	@staticmethod
	def create():
		return Something()
	def runTask(self, data: str):
		time.sleep(random.random())
		# print("id", self.id, "data", data)

if __name__ == "__main__":
	p = multi.Process(Something, ["some secret data!", "some more secret data!"], lambda p: print(f"the process totally ended", p, "wow"))
	p.wait()
	multi.pool(Something, [
		*"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	], lambda completed, total: print(f"Progress: {completed}/{total}"))
