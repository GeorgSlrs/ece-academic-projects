import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# 1) Create a grid to show the feasible region
x1_vals = np.linspace(0, 6, 200)
x2_vals = np.linspace(0, 6, 200)
X1, X2 = np.meshgrid(x1_vals, x2_vals)

# Constraints:
# Π1: 6x1+3x2 >= 12
# Π2: 4x1+8x2 >= 16
# Π3: 6x1+5x2 <= 30
# Π4: 6x1+7x2 <= 36
c1 = 6*X1 + 3*X2
c2 = 4*X1 + 8*X2
c3 = 6*X1 + 5*X2
c4 = 6*X1 + 7*X2

feasible_mask = (c1 >= 12) & (c2 >= 16) & (c3 <= 30) & (c4 <= 36)

# 2) Functions for the constraint boundary lines
def line_p1(x1):
    # 6x1 + 3x2 = 12 => x2 = (12 - 6*x1)/3
    return (12 - 6*x1)/3.0

def line_p2(x1):
    # 4x1 + 8x2 = 16 => x2 = (16 - 4*x1)/8
    return (16 - 4*x1)/8.0

def line_p3(x1):
    # 6x1 + 5x2 = 30 => x2 = (30 - 6*x1)/5
    return (30 - 6*x1)/5.0

def line_p4(x1):
    # 6x1 + 7x2 = 36 => x2 = (36 - 6*x1)/7
    return (36 - 6*x1)/7.0

# 3) The six vertices with your labels:
# A(4/3,4/3), B(5/2,3), Γ(0,36/7), Δ(4,0), Ε(0,4), Ζ(5,0)
vertices = {
    "A": (4/3, 4/3),
    "B": (5/2, 3),
    "Γ": (0, 36/7),
    "Δ": (4, 0),
    "Ε": (0, 4),
    "Ζ": (5, 0),
}

# 4) Set up the figure and main plotting area
fig, ax = plt.subplots(figsize=(7,7))
# Make space below for the slider
plt.subplots_adjust(bottom=0.25)

# -- Plot the feasible region as dots --
ax.scatter(X1[feasible_mask], X2[feasible_mask],
           color='cyan', marker='.', alpha=0.3, label="Feasible region")

# -- Plot each boundary line in [0,6] range --
x_line = np.linspace(0, 6, 300)
ax.plot(x_line, line_p1(x_line), label="Π1: 6x1+3x2=12")
ax.plot(x_line, line_p2(x_line), label="Π2: 4x1+8x2=16")
ax.plot(x_line, line_p3(x_line), label="Π3: 6x1+5x2=30")
ax.plot(x_line, line_p4(x_line), label="Π4: 6x1+7x2=36")

# -- Mark the vertices --
for label, (vx, vy) in vertices.items():
    ax.plot(vx, vy, 'ro')  # red dot
    ax.text(vx+0.1, vy+0.1, f"{label}({vx:.2f},{vy:.2f})", color='red')

# -- Plot the objective line for an initial c --
c_init = 10
y_obj_init = c_init - 3*x_line
(obj_line,) = ax.plot(x_line[y_obj_init>=0], y_obj_init[y_obj_init>=0],
                     'm--', linewidth=2, label=f"3x1 + x2 = {c_init}")

ax.set_xlim(0,6)
ax.set_ylim(0,6)
ax.set_xlabel("$x_1$")
ax.set_ylabel("$x_2$")
ax.set_title("Feasible Region and the Line 3x1 + x2 = c")
ax.legend()
ax.grid(True)

# 5) Create a slider below the plot to adjust c
#    The slider axes: [left, bottom, width, height]
slider_ax = plt.axes([0.20, 0.08, 0.60, 0.03])
slider_c = Slider(
    ax=slider_ax,
    label='c',
    valmin=0,
    valmax=20,
    valinit=c_init,
    valstep=0.1  # ← smaller increments
)

# 6) Define what happens when the slider is moved
def update(val):
    c = slider_c.val
    new_y = c - 3*x_line
    valid = (new_y >= 0)
    # Update line data
    obj_line.set_xdata(x_line[valid])
    obj_line.set_ydata(new_y[valid])
    # Update label
    obj_line.set_label(f"3x1 + x2 = {c:.1f}")
    ax.legend()
    fig.canvas.draw_idle()

slider_c.on_changed(update)

plt.show()
