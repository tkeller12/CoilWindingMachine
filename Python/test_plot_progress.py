import numpy as np
from matplotlib.pylab import *

import time

turns_per_layer = 10 # number of turns per layer
layers = 4 # number of layers
turns = turns_per_layer * layers


ion()
figure()

lines = []
for layer in range(layers):
    for turn in range(turns_per_layer):
#        line = plot(turn,layer, marker = 'o', fillstyle = 'none', color = 'black')
        circle = Circle((turn,layer), radius = 0.5, linewidth = 0)

        c = matplotlib.collections.PatchCollection([circle])

        ax = gca()
        ax.add_collection(c)
        if layer == 2 and turn == 2:
            c.set_color('red')


xlim(-0.5,(turns_per_layer)-0.5)
ylim(-0.5,(layers)-0.5)

ax = gca()
ax.set_aspect('equal')
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
