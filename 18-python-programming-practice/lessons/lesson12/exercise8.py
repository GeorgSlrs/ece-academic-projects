def binary_search(array, x, start, finish):
    middle = (start + finish) // 2
    if start > finish:
        return -1
    if x == array[middle]:
        return middle
    elif x < array[middle]:
        return binary_search(array, x, start, middle-1)
    else: # x > array[middle]
        return binary_search(array, x, middle + 1, finish)

my_list = [i * i for i in range(10)]
print(my_list)
print(binary_search(my_list, 9, 0, len(my_list) - 1))