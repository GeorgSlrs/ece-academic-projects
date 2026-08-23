def max_subarray_n3(arr):
    n = len(arr)
    max_sum = float('-inf')  # We can't initialize max_sum = 0, due to the fact that the maximum sum might indeed be negative

    
    start_index, end_index = 0, 0

     # Check every subarray and for each subarray calculate the sum of the elements
    for i in range(n):
        for j in range(i, n + 1):
            sum_cur = 0
            for k in range(i, j):
                sum_cur += arr[k]
            if sum_cur > max_sum:
                max_sum = sum_cur
                start_index = i
                end_index = j

    return start_index, end_index, max_sum

def max_subarray_n2(arr):
    n = len(arr)
    max_sum = float('-inf')
    start_index = end_index = 0

 # Same as before but instead of recalculating the sum for each subarray from scratch
# we keep track of it checking every subarray with the same start index

    for start in range(n):
        sum_cur = 0
        for end in range(start, n):
            sum_cur += arr[end]
            if sum_cur > max_sum:
                max_sum = sum_cur
                start_index = start
                end_index = end

    return start_index, end_index, max_sum



# 1) Split the array into 2 halves
# 2) Recursively solve each subproblem
# 3) Consider 3 possibilities:
# a) max sum is in the right half
# b) max sum is in the left half
# c) max sum spans across the midpoint 


def max_subarray_nlogn(arr, low, high):
    if low == high:
        return arr[low], low, high # Array has only one element, hence we have found the max sum

    mid = (low + high) // 2
    left_sum, left_start, left_end = max_subarray_nlogn(arr, low, mid)
    right_sum, right_start, right_end = max_subarray_nlogn(arr, mid + 1, high)
    cross_sum, cross_start, cross_end = spanning_sum(arr, low, mid, high)

    if left_sum >= right_sum and left_sum >= cross_sum:
        return left_sum, left_start, left_end
    elif right_sum >= left_sum and right_sum >= cross_sum:
        return right_sum, right_start, right_end
    else:
        return cross_sum, cross_start, cross_end

def spanning_sum(arr, low, mid, high):
    left_sum = float('-inf')
    right_sum = float('-inf')
    sum = 0

    for i in range(mid, low-1, -1):
        sum += arr[i]
        if sum > left_sum:
            left_sum = sum

    sum = 0
    for i in range(mid + 1, high + 1):
        sum += arr[i]
        if sum > right_sum:
            right_sum = sum

    return left_sum + right_sum, low, high



# Iterate through the array one time
# Calculate the max current sum so far by comparing arr[i] and array[i] + max_cur
# If array[i] is less than arr[i] + max_cur, update start_index to the current index
# If the global max is less than the current max, update start_index and end_index accordingly

def max_subarray_kadane(arr):
    if not arr:
        return None, None, None

    max_cur = max_gl = arr[0]
    start_index = end_index = temp_start_index = 0

    for i in range(1, len(arr)):
        if arr[i] > max_cur + arr[i]:
            max_cur = arr[i]
            temp_start_index = i
        else:
            max_cur += arr[i]

        if max_cur > max_gl:
            max_gl = max_cur
            start_index = temp_start_index
            end_index = i

    return max_gl, start_index, end_index