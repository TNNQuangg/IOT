import time

def cup(com):
    print(com, flush=True)

while True:
    cup('getid')
    id = input()
    cup('print My ID is: '+id)
    time.sleep(1)

    cup('getname')
    name = input()
    cup('print My Name is: '+name)
    time.sleep(1)

    cup('getxy')
    xy = input()
    cup('print My GPS Coords are: '+xy)
    time.sleep(1)

    cup('getx')
    x = input()
    cup('print My Longitude is: '+x)
    time.sleep(1)

    cup('gety',)
    y = input()
    cup('print My Latitude is: '+y)
    time.sleep(1)

    cup('ismarked')
    y = input()
    cup('print Marked: '+y)
    time.sleep(1)