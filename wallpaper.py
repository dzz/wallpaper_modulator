#!/usr/bin/python3

import time
import os
from math import floor
import subprocess


#state for IIR filters
previous_load = None
previous_free = None


#sleep time to yield to other processes (effectively dropping framerate)
sleep_time = 0.1
samplerate = 1 / sleep_time

#how many seconds the filter takes to get halfway to current system state
halflife = 5
inv_scalar = pow(0.5, 1.0/(halflife * samplerate))
scalar = 1.0 - inv_scalar

while True:

    cycle_start = time.time()

    #get and parse load
    file = open('/proc/loadavg')
    data = file.read()
    load_pieces = data.split(' ')
    parsed_load = float(load_pieces[0])

    #get and parse free memory
    parsed_free = float(os.popen("free | grep Mem | awk '{print $3/$2 * 100.0}'").read().replace("\n",""))


    if(previous_load is None):
        previous_load = parsed_load

    if(previous_free is None):
        previous_free = parsed_free



    filtered_load = (scalar * parsed_load)+(inv_scalar*previous_load)
    previous_load = filtered_load

    filtered_free = (scalar*parsed_free)+(inv_scalar*previous_free)
    previous_free = filtered_free;

    scaledHue = floor( filtered_load * 100);
    scaledFree = floor( 100 - ( 0.3*previous_free) );
    
    os.system('convert base.jpg -modulate 100,{0},{1} output.jpg'.format(scaledFree, scaledHue))
    os.system('feh output.jpg --bg-scale')

    delta = time.time()-cycle_start

    #keep updates at as consistent a framerate as we can...
    if(delta<sleep_time):
        time.sleep(sleep_time-delta)

