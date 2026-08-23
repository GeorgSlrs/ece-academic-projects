import random

def create_array(size):
    return [random.randint(-100, 100) for _ in range(size)] # return a list with size 'size' containinf integers in [-100, 100]