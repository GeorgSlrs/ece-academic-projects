import time
from max_subarray import max_subarray_n3, max_subarray_n2, max_subarray_nlogn, max_subarray_kadane
from random_arr import create_array

def main():
    arrays = {}
    sizes = {
        "n^3": [500, 1000],
        "n^2": [5000, 10000],
        "nlogn": [500000, 1000000],
        "n": [15000000, 30000000],
    }
    for complexity, (size1, size2) in sizes.items():
        arrays[complexity] = [create_array(size1), create_array(size2)]
    for complexity in arrays:
        print(f"\nTesting for complexity: {complexity}")
        for arr in arrays[complexity]:
            start_time = time.time()
            if complexity == "n^3":
                max_subarray_n3(arr)
            elif complexity == "n^2":
                max_subarray_n2(arr)
            elif complexity == "nlogn":
                max_subarray_nlogn(arr, 0, len(arr) - 1)
            else:
                max_subarray_kadane(arr)
            print(f"{complexity} algorithm took {time.time() - start_time} seconds for array size {len(arr)}.")

if __name__ == "__main__":
    main()
