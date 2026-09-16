from random import randrange

numbers = {}
N = 10
for i in range(1, 6+1):
    numbers[i] = 0

print(numbers)

for _ in range(N):
    num = randrange(1, 6+1)
    numbers[num] += 1

print(numbers)

for i in range(1, 6+1):
    print(str(i) + ": " + str(numbers[i] / N))

