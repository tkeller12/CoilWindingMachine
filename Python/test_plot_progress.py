import numpy as np
from matplotlib.pylab import *

import time
import serial

turns_per_layer = 12 # number of turns per layer
layers = 10 # number of layers
turns = turns_per_layer * layers

wire_diameter = 0.85
radius = wire_diameter / 2.

port = 'COM6'
#ser = serial.Serial(power, baudrate = 115200,timeout = 1)

print('Wait for device to initialize...')
time.sleep(0.1)
print('Done.')

print('Home Axis')
print('G28 X')
print('Done.')
print('')


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

print(circles)
for layer in range(layers):
    for turn in range(turns_per_layer):
        x_position = turn*2.*radius + radius * (layer % 2)
        x_positions[layer][turn] = x_position
        circle = Circle((turn*2.*radius + radius * (layer % 2),2.*radius * layer*np.sqrt(3)/2), radius = radius, linewidth = 0)

        circles[layer][turn] = matplotlib.collections.PatchCollection([circle])
        ax.add_collection(circles[layer][turn])
#        pause(0.001)

for layer in range(layers):
    for turn in range(turns_per_layer):
        print('G0 X%0.02f'%x_positions[layer][turn])
        print('ROTATE 1 TIME')
        circles[layer][turn].set_color('green')
        pause(0.1)



circles = []

#for layer in range(layers):
#    for turn in range(turns_per_layer):
##        line = plot(turn,layer, marker = 'o', fillstyle = 'full', color = 'black')
#        circle = Circle((turn,layer), radius = 0.5, linewidth = 0, color = 'red')
#        c = matplotlib.collections.PatchCollection([circle])
#        ax = gca()
#        ax.add_collection(c)
#        circles.append(c)
#        pause(0.1)


show()
