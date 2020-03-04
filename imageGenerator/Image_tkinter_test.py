from tkinter import *
import math as m
import numpy as np
import random as r
master = Tk()
w = Canvas(master, width=200, height=200, bg="White")
w.pack()
possible_objects = ["Fast", "Roller_support", "Momentfritt",
                    "Free", "Arrow_up", "Arrow_down", "Moment_medurs",
                    "Moment_moturs", "Load", "Stångnod", "Balk"]
active_objects=[]
###
# @Params = coordinates for the bounding box of the object. up = boolean indicating in which direction the arrow points
# Output = An arrow at the center of the bounding box
###


def draw_arrow(x_min, y_min, x_max, y_max, up):
    height, width = y_max-y_min, x_max-x_min
    x_center = x_min + width/2
    # Create the head of the triangle
    if up:
        w.create_line(x_center, y_max, x_center, y_min, arrow="last") # "last" draws the arrow at the second point
    elif not up:
        w.create_line(x_center, y_min, x_center, y_max, arrow="last")
    arrow_info = ("Arrow", x_min, y_min, x_max, y_max, up)
    active_objects.append(arrow_info)

###
# @Params = coordinates of the bounding box of the object
# Output = a beam drawn inside the box
###


def draw_beam(x_min, y_min, x_max, y_max):
    corner_1 = x_min, y_min
    corner_2 = x_max, y_max
    w.create_rectangle(corner_1, corner_2)
    beam_info = ("Beam", x_min, y_min, x_max, y_max)
    active_objects.append(beam_info)


# @Params = coordinates for the bounding box of the object
# Output = a load drawn inside the box
###


def draw_load(x_min, y_min, x_max, y_max):
    height, width = y_max - y_min, x_max - x_min
    corner_1 = x_min, y_min
    corner_2 = x_max, y_max
    w.create_rectangle(corner_1, corner_2) # Kind of okay way to do it a bit yank
    no_arrows = m.ceil(width/height)
    arrow_separation = width/no_arrows
    for i in range(no_arrows + 1):
        draw_arrow(x_min + i * arrow_separation, y_min, x_min + i * arrow_separation, y_max, False)
    load_info = ("Load", x_min, y_min, x_max, y_max)
    active_objects.append(load_info)
###
# @Params = coordinates of the boundingbox
# Output = a trinagle draw inside the box
###


def draw_triangle(x_min, y_min, x_max, y_max):
    width = x_max- x_min
    corner_1 = x_min, y_max
    corner_2 = x_min + width/2, y_min
    corner_3 = x_max, y_max
    w.create_polygon(corner_1, corner_2, corner_3, fill="White", outline="Black")
    triangle_info = ("Triangle", x_min, y_min, x_max, y_max)
    active_objects.append(triangle_info)

###
# @Params: The coordinates for the bounding box of the object
# Output: A rolling support drawn inside the box, resized to look good
###


def draw_rolling(x_min, y_min, x_max, y_max):
    width, height = x_max - x_min, y_max - y_min
    center_x = x_min + width/2
    center_y = y_min + height/2
    # To ensure that the support looks nice
    if width >= height:
        x_min = center_x - height/2
        x_max = center_x + height/2
        center_x = x_min + (x_max - x_min)/2
    elif height >= width:
        y_min = center_y - width/2
        y_max = center_y + width/2
    y_max_triangle = y_max - height/3
    draw_triangle(x_min, y_min, x_max, y_max_triangle)
    w.create_oval(x_min, y_max, center_x, y_max_triangle)
    w.create_oval(center_x, y_max, x_max, y_max_triangle)
    rolling_info = ("Rolling_support", x_min, y_min, x_max, y_max)
    active_objects.append(rolling_info)


###
# @Params: Coordinates: floats for  the edges of the bounding box of the object
#          rotation: boolean, indicates clockwise or anti clockwise True = anti clockwise
#          right: indicates which side of the beam the moment should be drawn.
# Output: A moment arrow?? feels like the wrong word choice
###

###
# TODO:
# save image function
# convert the image to a reasonable format
###

def draw_moment(x_min, y_min, x_max, y_max, rotation):
    width, height = x_max - x_min, y_max - y_min
    center_x, center_y = x_min + width / 2, y_min + height / 2
    radius = height / 2
    ###
    # Function for determining orientation, might be better to have somewhere else but okay for now
    # @Params: "pseudo" - parameter active_objects
    # output boolean: True = right side
    # Only works with images which includes one beam
    ###

    def right_left():
        for e in active_objects:
            obj = e[0]
            if obj == "Beam":
                beam_center = e[3] - e[1]
                center_difference = beam_center - center_x
                if center_difference < 0:
                    return True
                else:
                    return False

    right = right_left()
    print(right)
    if right:
        p1x = center_x + radius * m.cos(m.radians(-60))
        p1y = center_y - radius * m.sin(m.radians(-60))
        if rotation:
            for t in range(1, 151):
                theta = -75 + t
                p2x = center_x + radius * m.cos(m.radians(theta))
                p2y = center_y - radius * m.sin(m.radians(theta))
                if t == 150:
                    w.create_line(p1x, p1y, p2x, p2y, arrow="last")
                else:
                    w.create_line(p1x, p1y, p2x, p2y)
                p1x = p2x
                p1y = p2y
        else:
            for t in range(1, 151):
                theta = -75 + t
                p2x = center_x + radius * m.cos(m.radians(theta))
                p2y = center_y - radius * m.sin(m.radians(theta))
                if t == 1:
                    p2x = center_x
                    p2y = p2y + (radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                    w.create_line(p1x, p1y, p2x, p2y, arrow="last")
                else:
                    w.create_line(p1x, p1y, p2x, p2y)
                p1x = p2x
                p1y = p2y
    else:
        p1x = center_x + radius * m.sin(m.radians(-30))
        p1y = center_y - radius * m.cos(m.radians(-30))
        if rotation:
            for t in range(1, 120):
                theta = -30 - t
                p2x = 50 + radius * m.sin(m.radians(theta))
                p2y = 50 - radius * m.cos(m.radians(theta))
                if t == 119:
                    w.create_line(p1x, p1y, p2x, p2y, arrow="last")
                else:
                    w.create_line(p1x, p1y, p2x, p2y)
                p1x = p2x
                p1y = p2y
        else:
            for t in range(1, 120):
                theta = 30 + t
                p2x = 50 + radius * m.sin(m.radians(theta))
                p2y = 50 - radius * m.cos(m.radians(theta))
                if t == 1:
                    w.create_line(p1x, p1y, p2x, p2y, arrow="first")
                else:
                    w.create_line(p1x, p1y, p2x, p2y)
                p1x = p2x
                p1y = p2y


# for t in range(20):
#     x_min = r.randint(0, 40)
#     y_min = r.randint(0, 40)
#     x_max = r.randint(50, 100)
#     y_max = r.randint(50, 100)
#     draw_load(x_min, y_min, x_max, y_max)
draw_beam(20, 30, 40, 50)
x1 = 50
x2 = 70
y1 = 30
y2 = 50
draw_moment(x1, y1, x2, y2, False)

mainloop()
