"""
Thank you, chatGPT
NOTE: WAIT 2 MINUTES MAX FOR THE PRGRAM TO RUN
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.cm import ScalarMappable
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection

class FancyPlot:
    def __init__(self, x, y, cmap='viridis'):
        self.fig, self.ax = plt.subplots()
        self.x = x
        self.y = y
        self.cmap = cmap
        self.create_shader()
    
    def create_shader(self):
        # Define the shader function
        def shader(x, y):
            r = np.sqrt(x**2 + y**2)
            c = 1.0 / np.abs(r)
            return c
        
        # Generate a grid of points for the shader
        n = 500
        x = np.linspace(-10, 10, n)
        y = np.linspace(-10, 10, n)
        xx, yy = np.meshgrid(x, y)
        z = shader(xx, yy)
        
        # Create a colormap and normalization for the shader output
        cmap = plt.get_cmap(self.cmap)
        norm = plt.Normalize(vmin=np.min(z), vmax=np.max(z))
        self.scalar_map = ScalarMappable(norm=norm, cmap=cmap)
        
        # Create a collection of patches to be used in the shader
        patches = []
        for i in range(n):
            for j in range(n):
                x = xx[i,j]
                y = yy[i,j]
                r = Rectangle((x, y), 0.5, 0.5)
                patches.append(r)
        
        # Create a patch collection with the shader output
        self.shader = PatchCollection(patches, cmap=cmap, norm=norm)
        self.shader.set_array(z.flatten())
        
    def plot(self):
        # Plot the function data
        self.ax.plot(self.x, self.y, color='black')
        
        # Add the shader to the plot
        self.ax.add_collection(self.shader)
        
        # Add a colorbar to the plot
        cbar = self.fig.colorbar(self.scalar_map)
        cbar.ax.set_ylabel('1/|Ω|', rotation=0)
        
        # Set the plot limits and labels
        self.ax.set_xlim([-10, 10])
        self.ax.set_ylim([-10, 10])
        self.ax.set_xlabel('Ω')
        self.ax.set_ylabel('f(Ω)')
        self.ax.set_title('Plot of sqrt(2-2cos(Ω))/abs(Ω)')
        
        # Show the plot
        plt.show()

# Generate some data for the function
x = np.linspace(-10, 10, 1000)
y = ((2-2*np.cos(x))/x**2)**0.5

# Create a fancy plot object and plot the function
fp = FancyPlot(x, y)
fp.plot()
