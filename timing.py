import library as mc
import datetime

amount = 10000

def doSomethingSlow(seed: int):
	world1 = mc.MCWorld(0, 0)
	world1.getBiomeAt(mc.PosXZ(seed, 0))
	# world1.getSpawnPoint()

startTime = datetime.datetime.now()
for i in range(amount): doSomethingSlow(i)
endTime = datetime.datetime.now()

diff = endTime - startTime
secs = diff.total_seconds()
print("took", secs, "seconds, avg", f"{1000*secs/amount:.10f}", "ms per thing")
