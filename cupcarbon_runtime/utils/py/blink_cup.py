# Example node script using the predefined cup_* functions.
# The import below is only for IDE auto-completion; CupCarbon removes it
# and injects the real definitions when the simulation starts.
from cup_functions import *

while True:
    cup_mark()
    cup_print('Hello')
    cup_wait(1)
    cup_unmark()
    cup_print('World !')
    cup_wait(1)
