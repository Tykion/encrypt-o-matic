import time

def custom_operation(x_range):
    if x_range is None:
        return
    
    start, end = map(int, x_range.split('-')) # parse it from string and split with '-' to create a range
    total = end - start
    
    for i in range(start, end):
        time.sleep(0.001)
        #if i % 10000 == 0:
        print(f"\rCustom operation: {i - start}/{total}", end="", flush=True)
    print(f"\rCustom operation: {total}/{total}")