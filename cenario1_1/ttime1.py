import time

print("inicio ttime\n")
t = 0
for i in range(10000):
	t = round(time.monotonic()*1000)

print(round(time.monotonic()*1000))

