import random
import time
import sys

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.temperature = None
    def __repr__(self):
        return f"x coordinate: {self.x:3d}, y coordinate: {self.y:3d}, temperature: {self.temperature:.2f}"

class TempMeas:
    def __init__(self, num_points=100000, lower_bound_cor=0, upper_bound_cor=999):
        self.lower_bound_cor = lower_bound_cor
        self.upper_bound_cor = upper_bound_cor
        self.num_points = num_points
        self.points = self.generate_points()
    def generate_points(self):
        return [Point(random.randint(self.lower_bound_cor, self.upper_bound_cor), random.randint(self.lower_bound_cor, self.upper_bound_cor)) for _ in range(self.num_points)]
    def generate_measurements(self, num_measurements, lower_bound_temp=-10, upper_bound_temp=90):
        measurements = []
        for _ in range(num_measurements):
            point = random.choice(self.points)
            temp = round(random.uniform(lower_bound_temp, upper_bound_temp), 2)
            point.temperature = temp
            measurements.append((point, temp))
        return measurements

class MinHeap:
    def __init__(self, arr=[]):
        self.array = []
        self.pos = {}
        self.size = len(arr)
        for i, item in enumerate(arr):
            self.array.append((item[0], item[1]))
            self.pos[item[0]] = i
        for i in range(self.size // 2, -1, -1):
            self.heapify(i)
    def isEmpty(self):
        return self.size == 0
    def heapify(self, i):
        smallest = i
        le = 2 * i + 1
        ri = 2 * i + 2
        if le < self.size and self.array[le][1] < self.array[smallest][1]:
            smallest = le
        if ri < self.size and self.array[ri][1] < self.array[smallest][1]:
            smallest = ri
        if smallest != i:
            self.pos[self.array[smallest][0]] = i
            self.pos[self.array[i][0]] = smallest
            self.array[smallest], self.array[i] = self.array[i], self.array[smallest]
            self.heapify(smallest)
    def getMin(self):
        return self.array[0] if self.size > 0 else None
    def extractMin(self):
        if self.size == 0:
            return None
        root = self.array[0]
        lastNode = self.array[self.size - 1]
        self.array[0] = lastNode
        self.pos[lastNode[0]] = 0
        del self.pos[root[0]]
        self.size -= 1
        self.heapify(0)
        return root
    def insert(self, item):
        if self.size < len(self.array):
            self.array[self.size] = (item[0], 10**80)
        else:
            self.array.append((item[0], 10**80))
        self.pos[item[0]] = self.size
        self.size += 1
        self.decreaseKey(item)
    def decreaseKey(self, item):
        i = self.pos[item[0]]
        val = item[1]
        if self.array[i][1] <= val:
            return
        self.array[i] = item
        p = (i - 1) // 2
        while p >= 0 and self.array[i][1] < self.array[p][1]:
            self.pos[self.array[i][0]] = p
            self.pos[self.array[p][0]] = i
            self.array[p], self.array[i] = self.array[i], self.array[p]
            i = p
            p = (i - 1) // 2
    def deleteKey(self, item):
        self.decreaseKey((item[0], float('-inf')))
        self.extractMin()

class Median:
    def __init__(self):
        self.max_heap = MinHeap()
        self.min_heap = MinHeap()
        self.cur_median = 0
        self.point_heap_map = {}
    def add_temperature(self, point, temp):
        if point in self.point_heap_map:
            old_temp, heap_type = self.point_heap_map.pop(point)
            if heap_type == 'max':
                self.max_heap.deleteKey((point, -old_temp))
            else:
                self.min_heap.deleteKey((point, old_temp))
        if temp < self.cur_median:
            self.max_heap.insert((point, -temp))
            self.point_heap_map[point] = (temp, 'max')
        else:
            self.min_heap.insert((point, temp))
            self.point_heap_map[point] = (temp, 'min')
        if self.max_heap.size > self.min_heap.size + 1:
            moved_point, moved_temp = self.max_heap.extractMin()
            self.min_heap.insert((moved_point, -moved_temp))
            self.point_heap_map[moved_point] = (-moved_temp, 'min')
        elif self.min_heap.size > self.max_heap.size:
            moved_point, moved_temp = self.min_heap.extractMin()
            self.max_heap.insert((moved_point, -moved_temp))
            self.point_heap_map[moved_point] = (moved_temp, 'max')
        if self.max_heap.size > self.min_heap.size:
            self.cur_median = -self.max_heap.getMin()[1]
        elif self.min_heap.size > self.max_heap.size:
            self.cur_median = self.min_heap.getMin()[1]
        else:
            self.cur_median = (-self.max_heap.getMin()[1] + self.min_heap.getMin()[1]) / 2.0
    def return_median(self):
        return self.cur_median

def pick_points_add_temp(temp_measurements, num_measurements):
    median_calculator = Median()
    measurements = temp_measurements.generate_measurements(num_measurements)
    for i, (point, temp) in enumerate(measurements):
        median_calculator.add_temperature(point, temp)
        k = median_calculator.return_median()
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
