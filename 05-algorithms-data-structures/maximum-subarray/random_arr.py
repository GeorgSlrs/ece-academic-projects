import random

def create_array(size):
    return [random.randint(-100, 100) for _ in range(size)]
