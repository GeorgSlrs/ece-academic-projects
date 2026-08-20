import turtle
import math
import time
import random
#H βιβλιοθήκη turtle δημιουργήθηκε για να ζωραφιστεί το ποτάμι και ο δρόμος

# Δημιουργεί την οθόνη

t = turtle.Screen()
t.cv._rootwindow.resizable(False, False)
t.title("Frogger")
t.setup(600, 800)
t.bgcolor("white")
t.bgpic("background.gif")
t.tracer(0)

shapes = ["froggy.gif", "car1.gif", "car2.gif", "car3.gif", "log1.gif", "turtles2.gif",  "bike.gif","turtle.gif",
          "turtles3.gif",   "bus.gif", "home.gif", "goal.gif","tree1.gif","small_froggy.gif", "lives.gif", "one.gif",
          "two.gif", "three.gif", "time.gif", "tree2.gif", "30sec.gif", "40sec.gif"]
for shape in shapes:
    t.register_shape(shape)

pen = turtle.Turtle()
pen.speed(0)
pen.hideturtle()
pen.color("white")
pen.penup()

class Gameobj():
    def __init__(self, x, y, width, height, image):
        self.x = x; self.y = y; self.width = width; self.height = height; self.image = image
    def define(self, pen):
        pen.goto(self.x, self.y); pen.shape(self.image); pen.stamp()
    def iscollision(self, other):
        x_collision = (math.fabs(self.x - other.x) * 2) - (self.width + other.width)
        y_collision = (math.fabs(self.y - other.y) * 2) - (self.height + other.height)
        if x_collision < 0 and y_collision < 0:
            return (x_collision and y_collision)
    def update(self):
        pass

class Player(Gameobj):
    def __init__(self, x, y, width, height, image):
        Gameobj.__init__(self, x, y, width, height, image)
        self.dx = 0; self.collision = False; self.frogs_home = 0; self.max_time = 40
        self.start_time = time.time(); self.lives = 3
    def up(self): self.y += 40
    def down(self): self.y -= 40
    def right(self): self.x += 40
    def left(self): self.x -= 40
    def home(self):
        self.dx = 0; self.x = 0; self.y = -300; self.max_time = 40; self.start_time = time.time()
    def update(self):
        self.x += self.dx
        if self.x < -300 or self.x > 300:
            self.x = 0; self.y = -300
        self.elapsed_time = time.time() - self.start_time
        if self.elapsed_time > self.max_time:
            player.lives -= 1; self.home()

class Car(Gameobj):
    def __init__(self, x, y, width, height, image, dx):
        Gameobj.__init__(self, x, y, width, height, image); self.dx = dx
    def update(self):
        self.x += self.dx
        if self.x < -350: self.x = 350
        if self.x > 350: self.x = -350

class Log(Gameobj):
    def __init__(self, x, y, width, height, image, dx):
        Gameobj.__init__(self, x, y, width, height, image); self.dx = dx
    def update(self):
        self.x += self.dx
        if self.x < -400: self.x = 400
        if self.x > 400: self.x = -400

class Turtles(Gameobj):
    def __init__(self, x, y, width, height, image, dx):
        Gameobj.__init__(self, x, y, width, height, image)
        self.dx = dx; self.state = "full"; self.full_time = 8; self.half_time = 5; self.submerged_time = 3
        self.start_time = time.time()
    def update(self):
        self.x += self.dx
        if self.x < -400: self.x = 400
        if self.x > 400: self.x = -400

class Goal(Gameobj):
    def __init__(self, x, y, width, height, image):
        Gameobj.__init__(self, x, y, width, height, image); self.dx = 0

player = Player(0, -300, 50, 50, "froggy.gif")
player.define(pen)
level_1 = [Car(0, -135, 65, 20, "car1.gif", 2), Car(0, -215, 50, 20, "car3.gif", -1.5),
           Car(0, -255, 50, 20, "car2.gif", 1.7), Car(0,-95, 75, 20, "bus.gif", -1.4),
           Car(-320, -255, 50, 20, "car2.gif", 1.7), Log(-350, 95, 105, 20, "log1.gif", -1.3),
           Car(0,-175, 40, 20, "bike.gif", 1.9), Log(0, 55, 105, 20, "log1.gif", 1.1),
           Log(0, 95, 105, 20, "log1.gif", -1.3), Log(0, 135, 105, 20, "log1.gif", 1.2),
           Turtles(0, 175, 10, 20, "turtle.gif", -2), Turtles(0, 255, 60, 20, "turtles2.gif", -1.8),
           Turtles(0, 215, 110, 20, "turtles3.gif", 1.5), Goal(80, 0, 30, 20, "tree1.gif"),
           Goal(-215, 10, 70, 40, "tree2.gif"), Turtles(-300, 175, 10, 20, "turtle.gif", -2),
           Turtles(-280, 255, 60, 20, "turtles2.gif", -1.8), Turtles(-250, 215, 110, 20, "turtles3.gif", 1.5),
           Log(-350, 55, 105, 20, "log1.gif", 1.1)]
homes = [Goal(0, 315, 50, 20 ,"home.gif"), Goal(-100, 315, 50, 20 ,"home.gif"), Goal(-200, 315, 50, 20 ,"home.gif"), Goal(100, 315, 50, 20 ,"home.gif"), Goal(200, 315, 50, 20 ,"home.gif")]
objects = level_1 + homes
objects.append(player)

t.listen(); t.onkeypress(player.up, "Up"); t.onkeypress(player.down, "Down"); t.onkeypress(player.right, "Right"); t.onkeypress(player.left, "Left")

while True:
    for obj in objects:
        obj.define(pen); obj.update()
    pen.goto(-200, -325); pen.shape("small_froggy.gif")
    for life in range(player.lives):
        pen.goto(-285 + (life*30), -325); pen.stamp()
    pen.goto(-250, 375); pen.shape("lives.gif"); pen.stamp(); pen.goto(-205, 373)
    if player.lives == 3: pen.shape("three.gif"); pen.stamp()
    elif player.lives == 2: pen.shape("two.gif"); pen.stamp()
    elif player.lives == 1: pen.shape("one.gif"); pen.stamp()
    else: pen.shape("lives.gif"); pen.stamp()
    pen.goto(210,370); pen.shape("time.gif"); pen.stamp()
    player.dx = 0; player.collision = False
    for obj in objects:
        if player.iscollision(obj):
            if isinstance(obj, Car):
                player.lives -= 1; player.home(); break
            elif isinstance(obj, Log):
                player.dx = obj.dx; player.collision = True; break
            elif isinstance(obj, Turtles) and obj.state != "submerged":
                player.dx = obj.dx; player.collision = True; break
            elif isinstance(obj, Goal):
                if obj in homes:
                    player.home(); obj.image = "goal.gif"; player.frogs_home += 1
                elif obj in level_1:
                    if player.x < obj.x: player.x -= 40; break
                    elif player.x > obj.x: player.x += 40; break
                    elif player.y < obj.y: player.y -= 40
                    else: player.y += 40
    if player.y > 40 and player.collision != True:
        player.lives -= 1; player.home()
    pen.goto(255, 370); pen.shape("40sec.gif" if player.frogs_home < 3 else "30sec.gif"); pen.stamp()
    if player.y < -300: player.y += 40
    if player.frogs_home == 5:
        player.home(); player.frogs_home = 0; player.lives = 3
        for home in homes: home.image = "home.gif"
    if player.lives == 0:
        player.home(); player.frogs_home = 0
        for home in homes: home.image = "home.gif"
        player.lives = 3
    if player.frogs_home == 3: player.max_time = 30
    t.update(); pen.clear()

t.mainloop()
