import random
import time
import sys


# Each point is associated with a temperature
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.temperature = None 

    def __repr__(self):
        return f"x coordinate: {self.x:3d}, y coordinate: {self.y:3d}, temperature: {self.temperature:.2f}"


# Class which is responsible for creating the temp measurements
class TempMeas:
    def __init__(self, num_points=100000, lower_bound_cor=0, upper_bound_cor=999):
        self.lower_bound_cor = lower_bound_cor
        self.upper_bound_cor = upper_bound_cor
        self.num_points = num_points
        self.points = self.generate_points()

    # Return a list with Point() * num_points elements
    def generate_points(self):
        return [Point(random.randint(self.lower_bound_cor, self.upper_bound_cor), random.randint(self.lower_bound_cor, self.upper_bound_cor)) for _ in range(self.num_points)]

    # Select a random point from the list and match it with a temperature. The points are less than the measurements, hence
    # the number of iteration is  the provided number of measurements
    def generate_measurements(self, num_measurements, lower_bound_temp=-10, upper_bound_temp=90):
        measurements = []
        for _ in range(num_measurements):
            point = random.choice(self.points)  # Choose a random point
            temp = round(random.uniform(lower_bound_temp, upper_bound_temp), 2)  # Generate a random temperature in the specified range and round it up to 2 decimals
            point.temperature = temp 
            measurements.append((point, temp))
        return measurements


class MinHeap:
    def __init__(self, arr=[]):
        self.array = [] 
        self.pos = {}  # Position of key in array
        self.size = len(arr)  # Number of elements in min heap

        for i, item in enumerate(arr):
            self.array.append((item[0], item[1]))
            self.pos[item[0]] = i

        for i in range(self.size // 2, -1, -1): # Heapify the array starting from the last non-leaf node in order for the min-heap property to be maintained
            self.heapify(i)


    def display(self):
        print('array =', end=' ')
        for i in range(self.size):
            print(f'({self.array[i][0]} : {self.array[i][1]})', end=' ')
        print()

    def isEmpty(self):
        return self.size == 0

    def heapify(self, i):
        # Maintain the min-heap property by comparing the current node with its children
        smallest = i
        le = 2 * i + 1  # left child index
        ri = 2 * i + 2  # right child index

        # If the left child exists and is smaller than the current node, update smallest
        if le < self.size and self.array[le][1] < self.array[smallest][1]:
            smallest = le

        # If the right child exists and is smaller than the current node (or the left child), update smallest
        if ri < self.size and self.array[ri][1] < self.array[smallest][1]:
            smallest = ri

        # If the smallest value is not the current node, swap them and continue heapifying
        if smallest != i:
            self.pos[self.array[smallest][0]] = i
            self.pos[self.array[i][0]] = smallest

            self.array[smallest], self.array[i] = self.array[i], self.array[smallest]

            self.heapify(smallest)

    def getMin(self):
        return self.array[0] if self.size > 0 else None # Because we have min-heap


    """
    Removes and returns the smallest element from the min heap
    aka the root of it.
    The logic goes like this:
    
    1.If the heap is empty, there is nothing to extract.
    2.Replace the root of the tree with the last node and then perform heapify()
    """
    def extractMin(self):
        if self.size == 0:
            return None

        root = self.array[0]
        lastNode = self.array[self.size - 1]

        # Move the last element to the root and decrease the size of the heap
        self.array[0] = lastNode
        self.pos[lastNode[0]] = 0
        del self.pos[root[0]]

        self.size -= 1 # because one element has been removed
        self.heapify(0)

        return root

    # Check  if there is already space so as the new element can be accomondated
    # If there is not, append it to the heap array
    def insert(self, item):
        if self.size < len(self.array):
            self.array[self.size] = (item[0], 10**80)
        else:
            self.array.append((item[0], 10**80))

        self.pos[item[0]] = self.size # Map the element's key to it's index in the array
        self.size += 1 # Increase heap size because a new element has been added.
        self.decreaseKey(item) # So as the min-heap invariant is maintained

    # Compare the specified element with its parent and swap them if the
    # min-heap property is violated
    def decreaseKey(self, item):
        i = self.pos[item[0]]
        val = item[1]

        # If the new value is greater than or equal to the current value, do nothing
        if self.array[i][1] <= val:
            return

        # Update the value at the given position in the heap array
        self.array[i] = item

        # Move the element up the heap until the min-heap property is restored
        p = (i - 1) // 2
        while p >= 0 and self.array[i][1] < self.array[p][1]:
            # Update positions in the position map
            self.pos[self.array[i][0]] = p
            self.pos[self.array[p][0]] = i

            # Swap the current element with its parent
            self.array[p], self.array[i] = self.array[i], self.array[p]

            # Move up to the parent's position and continue checking if the min-heap property holds
            i = p
            p = (i - 1) // 2


    def deleteKey(self, item):
        self.decreaseKey((item[0], float('-inf')))
        self.extractMin()

# Class tasked with calculating the median
class Median:
    def __init__(self):
        self.max_heap = MinHeap()
        self.min_heap = MinHeap()
        self.cur_median = 0
        self.point_heap_map = {}

    def add_temperature(self, point, temp):
        # Check if the point already exists in the point_heap_map
        if point in self.point_heap_map:
            # Retrieve the old temperature and the heap type (max / min)
            old_temp, heap_type = self.point_heap_map.pop(point)
            # Remove the old temperature from the appropriate heap
            if heap_type == 'max':
                self.max_heap.deleteKey((point, -old_temp))
            else:
                self.min_heap.deleteKey((point, old_temp))

        # Add the new temperature into the max / min  heap
        if temp < self.cur_median:
            self.max_heap.insert((point, -temp))
            self.point_heap_map[point] = (temp, 'max')
        else:
            self.min_heap.insert((point, temp))
            self.point_heap_map[point] = (temp, 'min')

        # Balance the heaps if necessary
        if self.max_heap.size > self.min_heap.size + 1:
            # Move the root of max-heap to min-heap
            moved_point, moved_temp = self.max_heap.extractMin()
            self.min_heap.insert((moved_point, -moved_temp))
            self.point_heap_map[moved_point] = (-moved_temp, 'min')
        elif self.min_heap.size > self.max_heap.size:
            # Move the root of min-heap to max-heap
            moved_point, moved_temp = self.min_heap.extractMin()
            self.max_heap.insert((moved_point, -moved_temp))
            self.point_heap_map[moved_point] = (moved_temp, 'max')

        # Calculate the new median
        if self.max_heap.size > self.min_heap.size:
            # If max-heap has more elements, the median is the root of max-heap
            self.cur_median = -self.max_heap.getMin()[1]
        elif self.min_heap.size > self.max_heap.size:
            # If min-heap has more elements, the median is the root of min-heap
            self.cur_median = self.min_heap.getMin()[1]
        else:
            # If both heaps have the same number of elements, the median is the average of the roots of both heaps
            self.cur_median = (-self.max_heap.getMin()[1] + self.min_heap.getMin()[1]) / 2.0
            # Explanation: self.max_heap.getMin() returns a tuple (point, -temperature)
            # self.min_heap.getMin() returns a tuple (point, temperature)
        

    def return_median(self):
            return self.cur_median


# Create the list of measurements and display median
def pick_points_add_temp(temp_measurements, num_measurements):
    median_calculator = Median()
    measurements = temp_measurements.generate_measurements(num_measurements)

    for i, (point, temp) in enumerate(measurements):  # temp is for temperature
        median_calculator.add_temperature(point, temp)
        k = median_calculator.return_median()  # Calculate the median after each measurement but do not display it
        if i == num_measurements // 2 - 1:
            print(f"Median after {num_measurements // 2} measurements: {k:.2f}")
        elif i == num_measurements - 1:
            print(f"Final median after {num_measurements} measurements: {k:.2f}")

    print(f"Memory usage of points: {sys.getsizeof(temp_measurements.points)} bytes")
    print(f"Memory usage of measurements: {sys.getsizeof(measurements)} bytes")
    print(f"Memory usage of max_heap: {sys.getsizeof(median_calculator.max_heap.array)} bytes")
    print(f"Memory usage of min_heap: {sys.getsizeof(median_calculator.min_heap.array)} bytes")
    print(f"Memory usage of point_heap_map: {sys.getsizeof(median_calculator.point_heap_map)} bytes")


def main():
    start_time = time.time()
    temp_measurements = TempMeas()

    pick_points_add_temp(temp_measurements, 500000)
    print(f"Execution time for 500,000 measurements: {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    pick_points_add_temp(temp_measurements, 1000000)
    print(f"Execution time for 1,000,000 measurements: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
