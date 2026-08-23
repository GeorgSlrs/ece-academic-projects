import time
from max_subarray import max_subarray_n3, max_subarray_n2, max_subarray_nlogn, max_subarray_kadane  
from random_arr import create_array

def main():
    arrays = {}
    sizes = {
    "n^3": [500,1000],  
    "n^2": [5000, 10000],  
    "nlogn": [500000, 1000000],  
    "n": [15000000, 30000000]  
}

    for cmplxty, (size1, size2) in sizes.items():
         arrays[cmplxty] = [create_array(size1), create_array(size2)]

    for complexity in arrays.keys():
        print(f"\nTesting for complexity: {complexity}")
        for i in range(len(arrays[complexity])):
            arr = arrays[complexity][i]
            if complexity == "n^3":
                start_time = time.time()
                max_subarray_n3(arr)
                end_time = time.time()
                print(f"n^3 algorithm took {end_time - start_time} seconds for array size {len(arr)}.")
            elif complexity == "n^2":
                start_time = time.time()
                max_subarray_n2(arr)
                end_time = time.time()
                print(f"n^2 algorithm took {end_time - start_time} seconds for array size {len(arr)}.")
            elif complexity == "nlogn":
                start_time = time.time()
                max_subarray_nlogn(arr, 0, len(arr) - 1)
                end_time = time.time()
                print(f"nlogn algorithm took {end_time - start_time} seconds for array size {len(arr)}.")
            elif complexity == "n":
                start_time = time.time()
                max_subarray_kadane(arr)
                end_time = time.time()
                print(f"n algorithm took {end_time - start_time} seconds for array size {len(arr)}.")

if __name__ == "__main__":
    main()
