import time

def cup(com):
    print(com, flush=True)

while True:
    cup('print HELLO')
    time.sleep(1)
    cup('print WORLD!')
    time.sleep(1)