def max_subarray_n3(arr):
    n = len(arr)
    max_sum = float('-inf')
    start_index, end_index = 0, 0
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
    for start in range(n):
        sum_cur = 0
        for end in range(start, n):
            sum_cur += arr[end]
            if sum_cur > max_sum:
                max_sum = sum_cur
                start_index = start
                end_index = end
    return start_index, end_index, max_sum

def max_subarray_nlogn(arr, low, high):
    if low == high:
        return arr[low], low, high
    mid = (low + high) // 2
    left_sum, left_start, left_end = max_subarray_nlogn(arr, low, mid)
    right_sum, right_start, right_end = max_subarray_nlogn(arr, mid + 1, high)
    cross_sum, cross_start, cross_end = spanning_sum(arr, low, mid, high)
    if left_sum >= right_sum and left_sum >= cross_sum:
        return left_sum, left_start, left_end
    elif right_sum >= left_sum and right_sum >= cross_sum:
        return right_sum, right_start, right_end
    return cross_sum, cross_start, cross_end

def spanning_sum(arr, low, mid, high):
    left_sum = float('-inf')
    right_sum = float('-inf')
    total = 0
    left_start = mid
    right_end = mid + 1
    for i in range(mid, low-1, -1):
        total += arr[i]
        if total > left_sum:
            left_sum = total
            left_start = i
    total = 0
    for i in range(mid + 1, high + 1):
        total += arr[i]
        if total > right_sum:
            right_sum = total
            right_end = i
    return left_sum + right_sum, left_start, right_end

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
