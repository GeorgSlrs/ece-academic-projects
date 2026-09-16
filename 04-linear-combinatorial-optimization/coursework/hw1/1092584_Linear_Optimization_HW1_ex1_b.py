import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Define the constraints:
# Π₁: 6x1 + 3x2 >= 12
# Π₂: 4x1 + 8x2 >= 16
# Π₃: 6x1 + 5x2 <= 30
# Π₄: 6x1 + 7x2 <= 36

# Create a grid for plotting the full feasible region
x1_vals = np.linspace(0, 6, 300)
x2_vals = np.linspace(0, 6, 300)
X1, X2 = np.meshgrid(x1_vals, x2_vals)

# Evaluate each constraint over the grid
cons1 = 6*X1 + 3*X2   # Π₁: must be >= 12
cons2 = 4*X1 + 8*X2   # Π₂: must be >= 16
cons3 = 6*X1 + 5*X2   # Π₃: must be <= 30
cons4 = 6*X1 + 7*X2   # Π₄: must be <= 36

# Full feasible region: all constraints and non-negativity
feasible = (cons1 >= 12) & (cons2 >= 16) & (cons3 <= 30) & (cons4 <= 36) & (X1 >= 0) & (X2 >= 0)

# Define functions for the boundary lines (for plotting)
def line_P1(x):  # 6x1+3x2 = 12  --> x2 = 4 - 2*x1
    return 4 - 2*x
def line_P2(x):  # 4x1+8x2 = 16  --> x2 = 2 - 0.5*x
    return 2 - 0.5*x
def line_P3(x):  # 6x1+5x2 = 30  --> x2 = (30 - 6*x1)/5
    return (30 - 6*x)/5.0
def line_P4(x):  # 6x1+7x2 = 36  --> x2 = (36 - 6*x1)/7
    return (36 - 6*x)/7.0

# List the vertices (from the full problem)
# A: (4/3, 4/3)       - Π₁ ∩ Π₂
# B: (5/2, 3)         - Π₃ ∩ Π₄
# Γ: (0, 36/7)        - Π₄ ∩ {x1=0}
# Δ: (4, 0)           - Π₂ ∩ {x2=0}
# Ε: (0, 4)           - Π₁ ∩ {x1=0}
# Ζ: (5, 0)           - Π₃ ∩ {x2=0}
vertices = {
    "A": (4/3, 4/3),
    "B": (5/2, 3),
    "Γ": (0, 36/7),
    "Δ": (4, 0),
    "Ε": (0, 4),
    "Ζ": (5, 0)
}

# Define a function to compute the objective at each vertex for a given c2
def compute_objectives(c2):
    Z_A = (4/3)*(1 + c2)
    Z_B = (5/2) + 3*c2
    Z_G = (36/7)*c2
    Z_D = 4
    Z_E = 4*c2
    Z_Z = 5
    return {"A": Z_A, "B": Z_B, "Γ": Z_G, "Δ": Z_D, "Ε": Z_E, "Ζ": Z_Z}

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(7,7))
plt.subplots_adjust(bottom=0.30)  # leave room for slider

# Plot the full feasible region
ax.scatter(X1[feasible], X2[feasible], color='cyan', marker='.', alpha=0.3, label="Feasible region")

# Plot all the constraint boundaries (only plotting in [0,6])
xx = np.linspace(0, 6, 300)
ax.plot(xx, line_P1(xx), 'b-', label="Π₁: 6x₁+3x₂=12")
ax.plot(xx, line_P2(xx), 'g-', label="Π₂: 4x₁+8x₂=16")
ax.plot(xx, line_P3(xx), 'orange', label="Π₃: 6x₁+5x₂=30")
ax.plot(xx, line_P4(xx), 'purple', label="Π₄: 6x₁+7x₂=36")

# Mark and label all vertices
for lab, (vx, vy) in vertices.items():
    ax.plot(vx, vy, 'ko', ms=8)
    ax.text(vx+0.1, vy+0.1, f"{lab} ({vx:.2f}, {vy:.2f})", color='k', fontsize=10)

ax.set_xlim(0, 6)
ax.set_ylim(0, 6)
ax.set_xlabel("$x_1$")
ax.set_ylabel("$x_2$")
ax.set_title("Full Feasible Region and Vertices")
ax.grid(True)
ax.legend(loc='upper right')

# --- Plot the objective level curve for the current optimum ---
# The level curve for x1 + c2*x2 = Z_opt is given by: x2 = (Z_opt - x1)/c2 (if c2 != 0)
def objective_line(c2, Z_opt):
    if c2 == 0:
        return xx, np.full_like(xx, Z_opt)
    else:
        return xx, (Z_opt - xx)/c2

# Initially, choose c2_init
c2_init = 1.0
objs = compute_objectives(c2_init)
# Determine the optimum vertex (the one with the smallest objective value)
opt_vertex = min(objs, key=objs.get)
Z_opt = objs[opt_vertex]

# Plot the objective level line
obj_x, obj_y = objective_line(c2_init, Z_opt)
mask = (obj_y >= 0)
(obj_line,) = ax.plot(obj_x[mask], obj_y[mask], 'm--', lw=2,
                       label=f"x1+{c2_init:.2f}x2 = {Z_opt:.2f}")

# Mark the optimum vertex with a distinct marker (unfilled black circle)
(opt_plot,) = ax.plot(vertices[opt_vertex][0], vertices[opt_vertex][1],
                       'ko', ms=12, markerfacecolor='none',
                       label=f"Optimum at {opt_vertex}")

ax.legend(loc='upper right')

# --- Add a slider to adjust c2 ---
slider_ax = plt.axes([0.20, 0.10, 0.60, 0.04])
slider_c2 = Slider(ax=slider_ax, label='c2', valmin=0.0, valmax=3.0,
                   valinit=c2_init, valstep=0.01)

def update_c2(val):
    c2 = slider_c2.val
    objs = compute_objectives(c2)
    # Determine the optimum vertex among all vertices
    opt_vertex = min(objs, key=objs.get)
    Z_opt = objs[opt_vertex]
    
    # Update the objective level line
    x_vals, y_vals = objective_line(c2, Z_opt)
    mask = (y_vals >= 0)
    obj_line.set_xdata(x_vals[mask])
    obj_line.set_ydata(y_vals[mask])
    obj_line.set_label(f"x1+{c2:.2f}x2 = {Z_opt:.2f}")
    
    # Update the optimum marker to the new optimum vertex
    opt_point = vertices[opt_vertex]
    opt_plot.set_xdata(opt_point[0])
    opt_plot.set_ydata(opt_point[1])
    
    # Update the title to indicate which vertex is optimum
    if opt_vertex == "A":
        title = "Optimum at A (intersection of Π₁ and Π₂)"
    else:
        title = f"Optimum at {opt_vertex}"
    ax.set_title(title)
    
    ax.legend(loc='upper right')
    fig.canvas.draw_idle()

slider_c2.on_changed(update_c2)

plt.show()
