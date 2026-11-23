import time

def cup(com):
    print(com, flush=True)

while True:
    cup('mark')
    time.sleep(1)
    cup('unmark')
    time.sleep(1)