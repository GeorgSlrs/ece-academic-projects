numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,43,444444444443,7777777777777777777777]
cnt = 1
maximum = numbers[0]
while cnt < len(numbers):
    if numbers[cnt] > maximum:
        maximum = numbers[cnt]
    cnt += 1

print(maximum)


