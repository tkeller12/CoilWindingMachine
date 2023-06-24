import numpy as np
from matplotlib.pylab import *

import winder

import time
import serial

w = winder.Winder(verbose = True)
w.finish_moves()
w.set_feedrate_percent(100)
w.zero_current_position()

#w.home()
w.e_relative()
w.override_extrude()
#w.write('G0 Z10')
#w.write('G0 X10 Y10')
#w.set_rate(10000)
#w.set_feedrate_percent(100)
#
#
#print('Report Current Position:')
#w.flush()
#w.write('M154 S1')
#w.write('M155 S1')
##for ix in range(100):
##    w.read()
#print('Done.')



#w.unconditional_stop(message = 'Prepare Wire.')



x_start = 0

turns_per_layer = 12 # number of turns per layer
layers = 10 # number of layers
turns = turns_per_layer * layers

wire_diameter = 0.85
radius = wire_diameter / 2.


print('Wait for device to initialize...')
time.sleep(0.1)
print('Done.')

print('Home Axis')
print('G28 X')
print('Done.')
print('Absolute Mode Positioning')
print('G90')
print('Done.')
print('Extruder Relative Mode')
print('M83')
print('Done.')


ion()
figure()
xlim(-radius,(turns_per_layer)*2*radius)
ylim(-radius,2*radius*((layers-1)*np.sqrt(3)/2) + radius)
ax = gca()
ax.set_aspect('equal')
xlabel('x (mm)')
ylabel('y (mm)')

lines = []
circles = [[None for x in range(turns_per_layer)] for y in range(layers)]
x_positions = [[None for x in range(turns_per_layer)] for y in range(layers)]

for layer in range(layers):
    for turn in range(turns_per_layer):
        x_position = turn*2.*radius + radius * (layer % 2) + x_start
        x_positions[layer][turn] = x_position


        circle = Circle((turn*2.*radius + radius * (layer % 2),2.*radius * layer*np.sqrt(3)/2), radius = radius, linewidth = 0)

        circles[layer][turn] = matplotlib.collections.PatchCollection([circle])
        ax.add_collection(circles[layer][turn])
#        pause(0.001)

for ix in range(layers):
    if ix % 2 == 1:
        circles[ix] = circles[ix][::-1]
        x_positions[ix] = x_positions[ix][::-1]

for layer in range(layers):
    for turn in range(turns_per_layer):

#        circles[layer][turn].set_color('orange')
#        pause(0.01)
#        w.set_x(x_positions[layer][turn])
#        w.rotate(1)
        w.set_x_rotate(x_positions[layer][turn], 1)
#        w.finish_moves()

#        circles[layer][turn].set_color('green')
#        pause(0.01)




show()
