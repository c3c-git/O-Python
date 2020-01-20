import time

t1 = time.time()

n = 10000
i = 2
c = 0
while i <= n:
   d = 2
   while i % d != 0:
       d += 1
   if d == i:
       c += 1
   i += 1

print('\n', c)

t2 = time.time()
print(f"\nВремя {(t2 - t1):0.3} c")


