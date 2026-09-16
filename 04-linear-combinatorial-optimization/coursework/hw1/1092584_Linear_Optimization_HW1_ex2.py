import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Define the range for x1
x1 = np.linspace(5, 8, 400)

# Constraint lines
con1 = (2.7 - 0.3 * x1) / 0.1  # 0.3x1 + 0.1x2 ≤ 2.7
con2 = 12 - x1                  # 0.5x1 + 0.5x2 = 6
con3 = (6 - 0.6 * x1) / 0.4     # 0.6x1 + 0.4x2 ≥ 6

# Vertices of the feasible region
vertices = np.array([[6, 6], [7.5, 4.5]])

# Plot setup
fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(bottom=0.25)

# Plot constraints
ax.plot(x1, con1, color='blue', label='0.3x₁ + 0.1x₂ ≤ 2.7')
ax.plot(x1, con2, color='green', label='0.5x₁ + 0.5x₂ = 6')
ax.plot(x1, con3, color='red', label='0.6x₁ + 0.4x₂ ≥ 6')

# Highlight feasible region (colored line segment between vertices)
ax.plot(vertices[:, 0], vertices[:, 1], color='lime', linewidth=4, alpha=0.5, label='Feasible Region')
ax.scatter(vertices[:, 0], vertices[:, 1], color='black', zorder=5)

# Labels and limits
ax.set_xlabel('x₁ (kilorads)')
ax.set_ylabel('x₂ (kilorads)')
ax.set_xlim(5, 8)
ax.set_ylim(4, 7)
ax.grid(True)
ax.legend()

# Objective function line (Z = 0.4x₁ + 0.5x₂ = c)
obj_line, = ax.plot([], [], 'orange', linestyle='dotted', linewidth=2, label='Z = 0.4x₁ + 0.5x₂ = c')

# Slider for adjusting c
ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03])
c_slider = Slider(
    ax=ax_slider,
    label='c',
    valmin=5.2,
    valmax=5.5,
    valinit=5.25,
    valstep=0.01
)

# Update function for the slider
def update(val):
    c = c_slider.val
    obj_x2 = (c - 0.4 * x1) / 0.5
    obj_line.set_data(x1, obj_x2)
    fig.canvas.draw_idle()

c_slider.on_changed(update)
update(None)  # Initialize the objective line

plt.show()