from tkinter import *
import math as m
import numpy as np
import random as r
import pandas as pd
from scipy.interpolate import interp1d
from PIL import Image
import time
import sys
import os

root = Tk()
# The main canvas houses the image
m_cnv = Canvas(root, width=1000, height=1000)
m_cnv.pack(side=LEFT)
# The entry canvas houses the entries to change magnitudes
e_cnv = Canvas(root)
e_cnv.pack(side=RIGHT)

beam_list = []
node_list = []
truss_beams = []
# Counters for the FE-calculation scripts
force_number = 0
moment_number = 0
load_number = 0
number_of_forces = 0
number_of_moments = 0
number_of_loads = 0
# Points on beams, supports, roller-supports where a surface could be placed.
surface_points = {"Bottom": [], "Top": [], "Left": [], "Right": []} # To find the closest item for a surface. Each list: 
                                                                    # (the item, (starting coordinate), (ending coordinate)) 
"""
Function:
Reads the labels of the detected objects and saves them in a list.
-------------------------
Input:
None
-------------------------
Output:
List of the different labels detected by detector.py
-------------------------
"""


def get_classes():
    labels = []
    # file = open(r'C:\Users\tobia\Desktop\Kandidat\data_classes.txt')
    data_classes = os.path.join(os.getcwd(),"TrainYourOwnYOLO/Data/Model_Weights/data_classes.txt")
    file = open(data_classes)
    for line in file:
        labels.append(line.rstrip("\n"))
    return labels


labels = get_classes()
"""
Function:
Return the closest point on the closest beam to the coordinates passed to the function
-------------------------
Input:
coord   = the coordinates for the closest point to the beam on the object
sides   = Specifies which side to find the closest point in   
-------------------------
Output:
shortest_distance_coordinates   = the coordinates (x, y) for the closest point 
closest_beam                    = the beam closest to the input coordinates
"""


def find_closest_point(coord, sides=["Bottom", "Top", "Left", "Right"]):
    shortest_distance = m.inf
    shortest_distance_coordinates = (m.inf, m.inf)
    for beam in beam_list:
        for side in sides:
            for point in beam.points[side]:
                distance = compute_distance(coord, point)
                if distance < shortest_distance:
                    shortest_distance = distance
                    shortest_distance_coordinates = point
                    closest_beam = beam
    try:  # Ändra så den gör så även om inga andra objekt identifierats
        return shortest_distance_coordinates, closest_beam
    except UnboundLocalError:
        sys.exit("Error: no beam identified")


# Method for finding the closest possible object for a surface to be put on 
# (eg a beam or any kind of support). Returns the object, its coordinates 
# as they were on the input and the coordinates where it will be drawn.
"""
Function:
Finds the closest object to the detected surface
-------------------------
Input:
coord = 
sides = 
"""
def find_closest_object(coord, sides=["Bottom", "Top", "Left", "Right"]):
    shortest_distance = m.inf
    shortest_distance_coordinates = (m.inf, m.inf)
    print("got to line 102")
    for side in sides:
        print("sides")
        for item, point, corrected_point in surface_points[side]:
            distance = compute_distance(coord, point)
            if distance < shortest_distance:
                shortest_distance = distance
                shortest_distance_coordinates = corrected_point
                closest_item = item
                closest_side = side
    return closest_item, closest_side, shortest_distance_coordinates 


# Compute the distance between two points
def compute_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def create_label(obj, old_object=None):
    if old_object == None:
        if isinstance(obj, Force):
            global force_number
            force_number += 1
            if number_of_forces == 1:
                text = 'F'
            else: 
                text = 'F' + str(force_number)
        elif isinstance(obj, Moment):
            global moment_number
            moment_number += 1
            if number_of_moments == 1:
                text = 'M'
            else:
                text = 'M' + str(moment_number)
        elif isinstance(obj, Load):
            global load_number
            load_number += 1
            if number_of_loads == 1:
                text = 'W'
            else:
                text = 'W' + str(load_number)
    else:
        text = old_object.label


    if obj.closest_point in obj.beam.points["Bottom"]:
        x = obj.x_max + 10
        y = obj.y_max + 10
    elif obj.closest_point in obj.beam.points["Top"]:
        x = obj.x_max + 10
        y = obj.y_min - 10
    elif obj.closest_point in obj.beam.points["Left"]:
        x = obj.x_min - 10
        y = obj.y_min - 10
    elif obj.closest_point in obj.beam.points["Right"]:
        x = obj.x_max + 10
        y = obj.y_min - 10
    obj.label = text
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    sub_text = text.translate(SUB)
    
    m_cnv.create_text(x, y, font = ('Times', '15'), text=sub_text)
    return text
        

# Defining a beam
class Beam:
    def __init__(self, x_min, y_min, x_max, y_max, orientation):
        y_mid = (y_max + y_min)/2
        x_mid = (x_max + x_min)/2
        self.height = 4
        self.orientation = orientation
        self.points = {"Bottom": [], "Top": [], "Left": [], "Right": []}
        self.objects = {"Forces": [], "Loads": [], "Pins": [], "Rollers": [],
                        "Moments": [], "Surfaces": []} # gör om till tolftedelar istället för koordinater
        if orientation == "0":
            self.length = x_max - x_min
            self.y_max = y_mid + self.height/2
            self.y_min = y_mid - self.height/2
            self.x_max = x_max
            self.x_min = x_min
            point_distance = self.length/11
            # Creating twelve points on the top and bottom side of the beam and 
            # one on the middle of the left and right side.
            for i in range(12):
                self.points["Bottom"].append((self.x_min + i * point_distance, self.y_max))
                self.points["Top"].append((self.x_min + i * point_distance, self.y_min))
            self.points["Left"].append((self.x_min, y_mid))
            self.points["Right"].append((self.x_max, y_mid))
            # A suface could only be placed at any of the short ends of the beam.
            surface_points["Left"].append((self, (self.x_min, y_mid), (self.x_min, y_mid)))   # If the surface is connected to a beam the
            surface_points["Right"].append((self, (self.x_max, y_mid), (self.x_max, y_mid)))  # middle point were they connect won´t be changed
            self.surface_height = self.height*15

        elif orientation == "90":
            self.length = y_max - y_min
            self.x_max = x_mid + self.height/2
            self.x_min = x_mid - self.height/2
            self.y_min = y_min
            self.y_max = y_max
            point_distance = self.length/11
            # Creating twelve points on the top and bottom side of the beam and 
            # one on the middle of the left and right side.
            for i in range(12):
                self.points["Left"].append((self.x_min, self.y_min + i * point_distance))
                self.points["Right"].append((self.x_max, self.y_min + i * point_distance))
            self.points["Bottom"].append((x_mid, self.y_max))
            self.points["Top"].append((x_mid, self.y_min))
            # A suface could only be placed at any of the short ends of the beam.
            surface_points["Bottom"].append((self, (x_mid, self.y_max), (x_mid, self.y_max))) # If the surface is connected to a beam the
            surface_points["Top"].append((self, (x_mid, self.y_min), (x_mid, self.y_min)))    # middle point were they connect won´t be changed
            self.surface_width = self.height*15

    def __str__(self):
        return "Beam"

    def draw(self):
        m_cnv.create_rectangle(self.x_min, self.y_min, self.x_max, self.y_max, fill="")
        beam_list.append(self) 


# Defining a force of arbitrary vertical or horizontal direction  
class Force:
    def __init__(self, x_min, y_min, x_max, y_max, direction, old_object=None):
        self.direction = direction
        self.old_object = old_object
        x_mid = (x_max + x_min)/2
        y_mid = (y_max + y_min)/2
        if direction == "Up" or direction == "Down": # direction i raden under
            (closest_x, closest_y), self.beam = find_closest_point((x_mid, y_mid), ["Bottom", "Top"])
            self.closest_point = (closest_x, closest_y)
            self.x_mid = self.x_max = self.x_min = closest_x
            if self.closest_point in self.beam.points["Top"]:
                self.y_max = closest_y
                self.y_min = self.y_max - self.beam.length * 0.2 # Length of arrow is set to 20% of beam length
                self.point_index = self.beam.points['Top'].index(self.closest_point)
                self.side = 'Top'
            else:          
                self.y_min = closest_y
                self.y_max = self.y_min + self.beam.length * 0.2
                self.point_index = self.beam.points['Bottom'].index(self.closest_point)
                self.side = 'Bottom'
        elif direction == "Left" or direction == "Right":
            (closest_x, closest_y), self.beam = find_closest_point((x_min, y_mid), ["Left", "Right"])
            self.closest_point = (closest_x, closest_y)
            self.y_mid = self.y_max = self.y_min = closest_y
            if self.closest_point in self.beam.points["Right"]:
                self.x_max = closest_x
                self.x_min = self.x_max - self.beam.length * 0.2
                self.point_index = self.beam.points['Right'].index(self.closest_point)
                self.side = 'Right'
            else:
                self.x_min = closest_x
                self.x_max = self.x_min + self.beam.length * 0.2
                self.point_index = self.beam.points['Left'].index(self.closest_point)
                self.side = 'Left'

    def __str__(self):
        return "Force"

    # Drawing the arrow and appending it to the list of objects acting on the corresponding beam
    def draw(self):
        self.shapes = []
        if self.direction == "Up":
            self.shapes.append(m_cnv.create_line(self.x_mid, self.y_min, self.x_mid, self.y_max, arrow="first"))
        elif self.direction == "Down":
            self.shapes.append(m_cnv.create_line(self.x_mid, self.y_min, self.x_mid, self.y_max, arrow="last"))
        elif self.direction == "Left":
            self.shapes.append(m_cnv.create_line(self.x_min, self.y_mid, self.x_max, self.y_mid, arrow="first"))
        elif self.direction == "Right":
            self.shapes.append(m_cnv.create_line(self.x_min, self.y_mid, self.x_max, self.y_mid, arrow="last"))
        create_label(self, self.old_object)
        self.beam.objects["Forces"].append(self)


# Defining a pin support as a triangle with sidelength 15% of corresponding beams length
class PinSupport:
    def __init__(self, x_min, y_min, x_max, y_max, size=0.15):
        x_mid = (x_max + x_min)/2
        y_mid = (y_max + y_min)/2
        self.magnitude = None
        self.size = size
        self.closest_point, beam = find_closest_point((x_mid, y_mid))
        self.beam = beam
        self.surface_width = 1.2 * beam.length * size
        self.surface_height = self.surface_width
        if self.closest_point in beam.points["Bottom"]:
            self.x_mid = self.closest_point[0]
            self.x_min = self.x_mid - beam.length * size/2
            self.x_max = self.x_mid + beam.length * size/2
            self.y_min = self.closest_point[1]
            self.y_max = self.y_min + beam.length * m.sin(m.pi/3) * size
            self.side = "Bottom"
            self.corner1 = (self.x_mid, self.y_min) # corner1 is always the corner of the
            self.corner2 = (self.x_min, self.y_max) # triangle connected to the beam
            self.corner3 = (self.x_max, self.y_max)
            surface_points["Bottom"].append((self, (x_mid, y_max), (self.x_mid, self.y_max)))
        elif self.closest_point in beam.points["Top"]:
            self.x_mid = self.closest_point[0]
            self.x_min = self.x_mid - beam.length * size/2
            self.x_max = self.x_mid + beam.length * size/2
            self.y_max = self.closest_point[1]
            self.y_min = self.y_max - beam.length * m.sin(m.pi/3) * size
            self.side = "Top"
            self.corner1 = (self.x_mid, self.y_max)
            self.corner2 = (self.x_min, self.y_min)
            self.corner3 = (self.x_max, self.y_min)
            surface_points["Top"].append((self, (x_mid, y_min), (self.x_mid, self.y_min)))
        elif self.closest_point in beam.points["Left"]:
            self.x_max = self.closest_point[0]
            self.x_min = self.x_max - beam.length * m.sin(m.pi/3) * size
            self.y_mid = self.closest_point[1]
            self.y_max = self.y_mid + beam.length * size/2
            self.y_min = self.y_mid - beam.length * size/2
            self.side = "Left"
            self.corner1 = (self.x_max, self.y_mid)
            self.corner2 = (self.x_min, self.y_min)
            self.corner3 = (self.x_min, self.y_max)
            surface_points["Left"].append((self, (x_min, y_mid), (self.x_min, self.y_mid)))
        elif self.closest_point in beam.points["Right"]:
            self.x_min = self.closest_point[0]
            self.x_max = self.x_min + beam.length * m.sin(m.pi/3) * size
            self.y_mid = self.closest_point[1]
            self.y_max = self.y_mid + beam.length * size/2
            self.y_min = self.y_mid - beam.length * size/2
            self.side = "Right"
            self.corner1 = (self.x_min, self.y_mid)
            self.corner2 = (self.x_max, self.y_min)
            self.corner3 = (self.x_max, self.y_max)
            surface_points["Right"].append((self, (x_max, y_mid), (self.x_max, self.y_mid)))
        self.point_index = self.beam.points[self.side].index(self.closest_point)

    def __str__(self):
        return "PinSupport"

    def draw(self):
        m_cnv.create_polygon(self.corner1, self.corner2, self.corner3, fill="", outline="Black")
        self.beam.objects["Pins"].append(self)


# Defining a roller support as a pin support with sidelength 9.51% of corresponding beams length
# plus two extra circles with half that length as diameter
class RollerSupport:
    def __init__(self, x_min, y_min, x_max, y_max):
        x_mid = (x_min + x_max)/2
        y_mid = (y_min + y_max)/2
        self.magnitude = None
        pin_size = 0.0951
        ps = PinSupport(x_min, y_min, x_max, y_max, pin_size)
        self.ps = ps
        surface_points[self.ps.side].pop() # Removing the surface point that was added when the pin support was created
        self.surface_width = 1.2 * self.ps.beam.length * pin_size
        self.surface_height = self.surface_width
        if self.ps.side == "Bottom":
            self.circle_box1 = (ps.x_min, ps.y_max + ps.beam.length * pin_size/2, ps.x_mid, ps.y_max)
            self.circle_box2 = (ps.x_mid, ps.y_max + ps.beam.length * pin_size/2, ps.x_max, ps.y_max)
            self.side = "Bottom"
            surface_points["Bottom"].append((self, (x_mid, y_max), (ps.x_mid, ps.y_max + ps.beam.length * pin_size/2)))

        elif self.ps.side == "Top":
            self.circle_box1 = (ps.x_min, ps.y_min - ps.beam.length * pin_size/2, ps.x_mid, ps.y_min)
            self.circle_box2 = (ps.x_mid, ps.y_min - ps.beam.length * pin_size/2, ps.x_max, ps.y_min)
            self.side = "Top"
            surface_points["Top"].append((self, (x_mid, y_min), (ps.x_mid, ps.y_min - ps.beam.length * pin_size/2)))
        elif self.ps.side == "Left":
            self.circle_box1 = (ps.x_min - ps.beam.length * pin_size/2, ps.y_min, ps.x_min, ps.y_mid)
            self.circle_box2 = (ps.x_min - ps.beam.length * pin_size/2, ps.y_mid, ps.x_min, ps.y_max)
            self.side = "Left"
            surface_points["Left"].append((self, (x_min, y_mid), (ps.x_min - ps.beam.length * pin_size/2, ps.y_mid)))
        elif self.ps.side == "Right":
            self.circle_box1 = (ps.x_max, ps.y_min, ps.x_max + ps.beam.length * pin_size/2, ps.y_mid)
            self.circle_box2 = (ps.x_max, ps.y_mid, ps.x_max + ps.beam.length * pin_size/2, ps.y_max)
            self.side = "Right"
            surface_points["Right"].append((self, (x_max, y_mid), (ps.x_max + ps.beam.length * pin_size/2, ps.y_mid)))

    def __str__(self):
        return "RollerSupport"

    def draw(self):
        self.ps.draw()
        self.ps.beam.objects["Pins"].pop() # Elegant way of removing the extra pin support added to the objects dictionary
        m_cnv.create_oval(self.circle_box1)
        m_cnv.create_oval(self.circle_box2)
        self.ps.beam.objects["Rollers"].append(self)


class Moment:
    def __init__(self, x_min, y_min, x_max, y_max, rotation, side=None, old_object=None):
        self.old_object = old_object
        x_mid, y_mid = (x_min + x_max)/2, (y_min + y_max)/2
        self.side = side
        self.rotation = rotation
        if side == None:
            self.closest_point, self.beam = find_closest_point((x_mid, y_mid))
            if self.closest_point in self.beam.points["Bottom"]:
                self.side = "Bottom"
            if self.closest_point in self.beam.points["Top"]:
                self.side = "Top"
            if self.closest_point in self.beam.points["Left"]:
                self.side = "Left"
            if self.closest_point in self.beam.points["Right"]:
                self.side = "Right"    
        else:
            self.closest_point, self.beam = find_closest_point((x_mid, y_mid), [side])
        self.radius = self.beam.length * 0.075
        self.point_index = self.beam.points[side].index(self.closest_point)
        if self.side == "Bottom":
            self.x_mid = self.closest_point[0]
            self.x_min = self.x_mid - self.radius
            self.x_max = self.x_mid + self.radius
            self.y_min = self.closest_point[1] + self.radius/2
            self.y_max = self.y_min + self.radius
        elif self.side == "Top":
            self.x_mid = self.closest_point[0]
            self.x_min = self.x_mid - self.radius
            self.x_max = self.x_mid + self.radius
            self.y_max = self.closest_point[1] - self.radius/2
            self.y_min = self.y_max - self.radius
        elif self.side == "Left":
            self.x_max = self.closest_point[0] - self.radius/2
            self.x_min = self.x_max - self.radius
            self.y_mid = self.closest_point[1]
            self.y_min = self.y_mid - self.radius
            self.y_max = self.y_mid + self.radius
        elif self.side == "Right":
            self.x_min = self.closest_point[0] + self.radius/2
            self.x_max = self.x_min - self.radius
            self.y_mid = self.closest_point[1]
            self.y_min = self.y_mid - self.radius
            self.y_max = self.y_mid + self.radius

    def __str__(self):
        return "Moment"

    def draw(self):
        self.shapes = []
        if self.side == "Bottom":
            p1x = self.x_mid + self.radius * m.cos(m.radians(-15))
            p1y = self.y_min - self.radius * m.sin(m.radians(-15))
            p2y = self.y_min
            if self.rotation == "Counterclockwise":
                p2x = p1x + (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                self.shapes.append(m_cnv.create_line(p1x, p1y, p2x, p2y, arrow="last", width=2, arrowshape="12 14 4"))

            for t in range(1, 1509):
                theta = -15 - t / 10
                p2x = self.x_mid + self.radius * m.cos(m.radians(theta))
                p2y = self.y_min - self.radius * m.sin(m.radians(theta))
                self.shapes.append(m_cnv.create_line(p1x, p1y, p2x, p2y, width=2))
                p1x = p2x
                p1y = p2y

            if self.rotation == "Clockwise":
                p2x = p1x - (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                self.shapes.append(m_cnv.create_line(p1x, p1y, p2x, self.y_min, arrow="last", width=2, arrowshape="12 14 4"))

        elif self.side == "Top":
            p1x = self.x_mid + self.radius * m.cos(m.radians(15))
            p1y = self.y_max - self.radius * m.sin(m.radians(15))
            p2y = self.y_max
            if self.rotation == "Clockwise":
                p2x = p1x + (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                self.shapes.append(m_cnv.create_line(p1x, p1y, p2x, p2y, arrow="last", width=2, arrowshape="12 14 4"))
            for t in range(1, 1509):
                theta = -15 - t / 10
                p2x = self.x_mid + self.radius * m.cos(m.radians(theta))
                p2y = self.y_max - self.radius * m.sin(m.radians(theta))
                self.shapes.append(m_cnv.create_line(p1x, p1y, p2x, p2y, width=2))
                p1x = p2x
                p1y = p2y
            if self.rotation == "Counterclockwise":
                p2x = p1x - (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                self.shapes.append(m_cnv.create_line(p1x, p1y, p2x, self.y_max, arrow="last", width=2, arrowshape="12 14 4"))

        elif self.side == "Left":
            p1x = self.x_max + self.radius * m.cos(m.radians(255))
            p1y = self.y_mid - self.radius * m.sin(m.radians(255))
            p2x = self.x_max
            if self.rotation == "Counterclockwise":
                p2y = p1y + (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                self.shapes.append(m_cnv.create_line(p1x, p1y, p2x, p2y, arrow="last", width=2, arrowshape="12 14 4"))
            for t in range(1, 1509):
                theta = 255 - t / 10
                p2x = self.x_max + self.radius * m.cos(m.radians(theta))
                p2y = self.y_mid - self.radius * m.sin(m.radians(theta))
                self.shapes.append(m_cnv.create_line(p1x, p1y, p2x, p2y, width=2))
                p1x = p2x
                p1y = p2y
            if self.rotation == "Clockwise":
                p2y = p1y - (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                self.shapes.append(m_cnv.create_line(p1x, p1y, self.x_max, p2y, arrow="last", width=2, arrowshape="12 14 4"))

        elif self.side == "Right":
            p1x = self.x_min + self.radius * m.cos(m.radians(-75))
            p1y = self.y_mid - self.radius * m.sin(m.radians(-75))
            p2x = self.x_min
            # Draw the arrow part of the moment
            if self.rotation == "Clockwise":
                p2y = p1y + (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                self.shapes.append(m_cnv.create_line(p1x, p1y, p2x, p2y, arrow="last", width=2, arrowshape="12 14 4"))

            # Draws the rest of the moment
            for t in range(1, 1509):
                theta = -75 + t / 10
                p2x = self.x_min + self.radius * m.cos(m.radians(theta))
                p2y = self.y_mid - self.radius * m.sin(m.radians(theta))
                self.shapes.append(m_cnv.create_line(p1x, p1y, p2x, p2y, width=2))
                p1x = p2x
                p1y = p2y
            if self.rotation == "Counterclockwise":
                p2y = p1y - (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                self.shapes.append(m_cnv.create_line(p1x, p1y, self.x_min, p2y, arrow="last", width=2, arrowshape="12 14 4"))
        create_label(self, self.old_object)
        self.beam.objects["Moments"].append(self)


class Load:
    def __init__(self, x_min, y_min, x_max, y_max, direction, old_object=None):
        self.old_object = old_object
        y_mid = (y_min + y_max)/2
        self.direction = direction
        self.leftmost_point, self.beam = find_closest_point((x_min, y_mid), ["Bottom", "Top"])
        self.rightmost_point, self.beam = find_closest_point((x_max, y_mid), ["Bottom", "Top"])
        self.closest_point = self.rightmost_point
        self.x_min = self.leftmost_point[0]
        self.x_max = self.rightmost_point[0]
        self.length = self.x_max - self.x_min
        print("x_max", self.x_max, "\n", "x_min", self.x_min)
        self.height = self.beam.length/6
        if self.closest_point in self.beam.points["Bottom"]:
            self.y_min = self.closest_point[1]
            self.y_max = self.y_min + self.height
            self.side = 'Bottom'
        elif self.closest_point in self.beam.points["Top"]:
            self.y_max = self.closest_point[1]
            self.y_min = self.y_max - self.height
            self.side = 'Top'
        self.no_arrows = int(self.length/50)
        print("length", self.length, "\n", "number of arrows", self.no_arrows)
        self.sep = self.length / self.no_arrows
        self.point_index = (self.beam.points[self.side].index(self.leftmost_point), self.beam.points[self.side].index(self.rightmost_point))

    def __str__(self):
        return "Load"

    def draw(self):
        self.shapes = []
        py1 = self.leftmost_point[1]
        py2 = py1 - self.height
        if self.direction == "Down":
            for i in range(self.no_arrows + 1):
                px = self.leftmost_point[0] + i * self.sep
                self.shapes.append(m_cnv.create_line(px, py1, px, py2, arrow="first")) # Kan krympa med first/last som variabel
        elif self.direction == "Up":
            for i in range(self.no_arrows + 1):
                px = self.leftmost_point[0] + i * self.sep
                self.shapes.append(m_cnv.create_line(px, py1, px, py2, arrow="last"))

        self.shapes.append(m_cnv.create_line(self.leftmost_point[0], self.leftmost_point[1], 
                                            self.rightmost_point[0], self.rightmost_point[1]))
        self.shapes.append(m_cnv.create_line(self.leftmost_point[0], py2, self.rightmost_point[0], py2))
        create_label(self, self.old_object)
        self.beam.objects["Loads"].append(self)


class Surface:
    """

    """
    def __init__(self, x_min, y_min, x_max, y_max):
        self.magnitude = None
        self.x_min = x_min
        self.y_min = y_min
        self.x_mid = (x_min + x_max)/2
        self.y_mid = (y_min + y_max)/2
        self.x_max = x_max
        self.y_max = y_max
        height = y_max - y_min
        width = x_max - x_min
        if width > height:
            self.closest_item, self.side, self.closest_point = find_closest_object((self.x_mid, self.y_mid), ["Bottom", "Top"])
            self.x_mid = self.closest_point[0]
            self.width = self.closest_item.surface_width
            self.height = 10
            if self.side == "Bottom":
                self.y_min = self.closest_point[1]
                self.y_max = self.y_min + self.height
            elif self.side == "Top":
                self.y_max = self.closest_point[1]
                self.y_min = self.y_min - self.height
            self.no_lines = int(self.width/8) 
        elif width < height:
            self.closest_item, self.side, self.closest_point = find_closest_object((self.x_mid, self.y_mid), ["Left", "Right"])
            self.y_mid = self.closest_point[1]
            self.height = self.closest_item.surface_height 
            self.width = 10
            if self.side == "Left":
                self.x_max = self.closest_point[0]
                self.x_min = self.x_max - self.width
            elif self.side == "Right":
                self.x_min = self.closest_point[0]
                self.x_max = self.x_min + self.width
            self.no_lines = int(self.height/8)
            if isinstance(self.closest_item, Beam): # sammanfoga längst ner i draw?
                self.point_index = self.closest_item.points[self.side].index(self.closest_point)

    def __str__(self):
        return "Surface"

    def draw(self):
        """
        :return: draws the surface
        """
        if self.side == "Bottom":
            m_cnv.create_line(self.x_mid - self.width/2, self.y_min, self.x_mid + self.width/2, self.y_min)
            for i in range(self.no_lines):
                p1x = self.x_mid - self.width/2 + (i/(self.no_lines - 1))*self.width 
                p2x = p1x - self.width/(self.no_lines - 1)
                p1y = self.y_min
                p2y = self.y_max
                m_cnv.create_line(p1x, p1y, p2x, p2y)
        elif self.side == "Top":
            m_cnv.create_line(self.x_mid - self.width/2, self.y_max, self.x_mid + self.width/2, self.y_max)
            for i in range(self.no_lines):
                p1x = self.x_mid - self.width/2 + (i/(self.no_lines - 1))*self.width 
                p2x = p1x - self.width/(self.no_lines - 1)
                p1y = self.y_max
                p2y = self.y_min
                m_cnv.create_line(p1x, p1y, p2x, p2y)
        elif self.side == "Left":
            m_cnv.create_line(self.x_max, self.y_mid - self.height/2, self.x_max, self.y_mid + self.height/2)
            for i in range(self.no_lines):
                p1x = self.x_max
                p2x = self.x_min
                p1y = self.y_mid - self.height/2 + (i/(self.no_lines - 1))*self.height 
                p2y = p1y - self.height/(self.no_lines - 1)
                m_cnv.create_line(p1x, p1y, p2x, p2y)
        elif self.side == "Right":
            m_cnv.create_line(self.x_min, self.y_mid - self.height/2, self.x_min, self.y_mid + self.height/2)
            for i in range(self.no_lines):
                p1x = self.x_min
                p2x = self.x_max
                p1y = self.y_mid - self.height/2 + (i/(self.no_lines - 1))*self.height 
                p2y = p1y - self.height/(self.no_lines - 1)
                m_cnv.create_line(p1x, p1y, p2x, p2y)

        if isinstance(self.closest_item, Beam):
            self.closest_item.objects["Surfaces"].append(self) 


def find_closest_node(coord):
    """
    Finds the closest node to the input coordinates
    :param coord: coordinates for the endpoint of a truss_beam
    :return: the closest node to the endpoint
    """
    shortest_distance = m.inf
    shortest_distance_coordinates = (m.inf, m.inf)
    for node in node_list:
        distance = compute_distance(coord, node.center)
        if distance < shortest_distance:
            shortest_distance = distance
            shortest_distance_coordinates = node.center
            closest_node = node

    return shortest_distance_coordinates, closest_node

"""
class TrussBeam:
    def __init__(self, x_min, y_min, x_max, y_max, orientation):
        self.x_min, self.y_min, self.x_max, self.y_max, self.orientation = x_min, y_min, x_max, y_max, orientation
        length = (x_min + x_max)/2
        height = (y_min + y_max)/2
        self.center = ((x_min + x_max)/2, (y_min + y_max)/2)
        if orientation == 45:
            self.leftmost_point = (x_min, y_max)
            self.rightmost_point = (x_max, y_min)
        elif orientation == 135:
            self.leftmost_point = (x_min, y_min)
            self.rightmost_point = (x_max, y_max)
        elif orientation == 90:  # 0 refers to a straight beam.
            self.leftmost_point = (x_min + length/2, y_min)
            self.rightmost_point = (x_min + length/2, y_max)
        elif orientation == 0:
                self.leftmost_point = (x_min, y_min + height/2)
                self.rightmost_point = (x_max, y_min + height/2)

        def connected_nodes():
            node1 = find_closest_node(self.leftmost_point)
            node2 = find_closest_node(self.rightmost_point)
            return [node1, node2]

        self.nodes = connected_nodes()

        for node in self.nodes:
            node.beams.append(self)
        truss_beams.append(self)

    def draw(self):
        if self.orientation == 45:
            m_cnv.create_line(self.x_min, self.y_max, self.x_max, self.y_min)
        elif self.orientation == 135:
            m_cnv.create_line(self.x_min, self.y_min, self.x_max, self.y_max)
        elif self.orientation == 0:
            m_cnv.create_line(self.x_min, self.y_max, self.x_max, self.y_max)  # A bit ugly might fix later


class Node:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min, self.y_min, self.x_max, self.y_max = x_min, y_min, x_max, y_max
        self.center = ((x_max + x_min)/2, (y_max + y_min)/2)
        self.number = 0
        self.beams = []
        self.connected_nodes = []
        self.layer = 0
        node_list.append(self)
                
    def draw(self):
        m_cnv.create_oval(self.x_min, self.y_min, self.x_max, self.y_max, fill="")


class Truss:
    def __init__(self, nodes, truss_beams):
        self.nodes = nodes
        self.beams = truss_beams

        # Find the start node
        x_min = m.inf
        for node in self.nodes:
            if node.x_min <= x_min:
                x_min = node.x_min
                start_node = node

        # Moves the start node to the first element in the list
        index_sn = self.nodes.index(start_node)
        self.nodes.pop(index_sn)
        self.nodes.insert(0, start_node)

        # Connect nodes
        for beam in self.beams:
            for node in self.nodes:
                if node in beam.nodes:
                    node.beams.append[beam]
                    i = beam.nodes.index(node)
                    if i == 0:
                        node.connected_nodes.append(beam.nodes[1])
                    elif i == 1:
                        node.connected_nodes.append(beam.nodes[0])

        def get_beam (node_1, node_2):
            beams = node_1.beams
            for beam in beams:
                if node_1 and node_2 in beam.nodes:
                    return beam
                else:




        # Aligns the nodes horizontally
        layers = {0: {start_node}}
        start_node.layer = 0
        temp = [start_node]
        finished = []
        while finished != self.nodes:
            for node in temp:
                temp.append(node.connected_nodes)
                temp.remove(node)
                finished.append(node)
                for node_2 in temp:
                    beam = get_beam(node_1, node_2)
                    angle = beam.orientation
                    if angle == 0:
                        node_2.layer = node.layer
                        layers[node.layer].add(node_2)
"""

def get_objects():
    """
    Reads in the detected objects from Detection_Results.csv
    :return:
    """
    try:
        df = pd.read_csv(r'C:\Users\admin\Desktop\Detection_Results.csv')
    except:
        df = pd.read_csv(r'C:\Users\tobia\Desktop\resultatHebbeBatch16\Detection_Results.csv')
        # df = pd.read_csv(r'C:\Users\tobia\Desktop\Detection_Results_test.csv')
        # df = pd.read_csv(os.path.join(os.getcwd(), "TrainYourOwnYOLO/Data/Source_Images/Test_Image_Detection_Results/Detection_Results.csv")
    df1 = df[["xmin", "ymin", "xmax", "ymax", "label", "confidence", "x_size", "y_size"]]
    df1 = delete_overlapping_objects(df1)
    return (df1)


def delete_overlapping_objects(objects): # Sannolikheter, Momentpilar åt olika håll -> välj den som har rätt typ av balkpunkt närmast, grej för att ändra position om krock efter ändringar
    """
    Deletes overlapping objects based on some cool stuff
    :param objects:
    :return:
    """
    for index1, obj1 in objects.iterrows():
        for index2, obj2 in objects.iterrows():
            if index1 == index2:
                continue
            type1 = labels[int(obj1[4])]
            type2 = labels[int(obj2[4])]
            x_min1, y_min1, x_max1, y_max1 = obj1[0], obj1[1], obj1[2], obj1[3],
            x_min2, y_min2, x_max2, y_max2 = obj2[0], obj2[1], obj2[2], obj2[3],
            x_mid1 = (x_max1 + x_min1)/2
            y_mid1 = (y_max1 + y_min1)/2
            if x_min2 < x_mid1 < x_max2 and y_min2 < y_mid1 < y_max2:
                if type1 == type2:
                    if obj1[5] < obj2[5]:
                        objects = objects.drop(index1, axis=0)
                #elif type1 == "BeamLine":
                #    objects = objects.drop(index1, axis=0)
                elif type1 in ["arrow_up", "arrow_down", "arrow_left", "arrow_right"] and type2 in ["load_up", "load_down"]:
                    objects = objects.drop(index1, axis=0)
                elif type1 == "Node" and type2 == "roller_support":
                    objects = objects.drop(index1, axis=0)
                elif type1 in ["counterclockwise_right", "counterclockwise_top", "counterclockwise_bottom", "counterclockwise_left", 
                                "clockwise_right", "clockwise_left", "clockwise_top", "clockwise_bottom"] and type2 in ["counterclockwise_right", 
                                "counterclockwise_top", "counterclockwise_bottom", "counterclockwise_left", 
                                "clockwise_right", "clockwise_left", "clockwise_top", "clockwise_bottom"]:
                    if obj1[5] < obj2[5]:
                        objects = objects.drop(index1, axis=0)
                    #else:
                     #   objects = objects.drop(index2, axis=0)
    return objects


def draw_all_objects():
    """
    Draws all the detected objects by detector.py
    :return:
    """
    objects = get_objects()
    for index, row in objects.iterrows():
        obj_type = labels[int(row[4])]
        if obj_type in ['arrow_up', 'arrow_down', 'arrow_left', 'arrow_right']: # ändra alla ' till " eller tvärt om?
            global number_of_forces
            number_of_forces += 1
        elif obj_type in ["clockwise_right", "clockwise_top", "clockwise_left", "clockwise_bottom", 
                          "counterclockwise_right", "counterclockwise_top", "counterclockwise_left", "counterclockwise_bottom"]:
            global number_of_moments
            number_of_moments += 1
        elif obj_type in ["load_up", "load_down"]:
            global number_of_loads
            number_of_loads += 1

    for index, row in objects.iterrows():
        m_x = interp1d([0, max(row[6], row[7])], [0, 800])
        m_y = interp1d([0, max(row[6], row[7])], [0, 800])
        obj_type = labels[int(row[4])]
        x_min, y_min, x_max, y_max = float(m_x(row[0])), float(m_y(row[1])), float(m_x(row[2])), float(m_y(row[3]))
        if obj_type == "beam":
            beam = Beam(x_min, y_min, x_max, y_max, "0")
            beam.draw()
            print("got to 838")
        elif obj_type == "beam_90":
            beam = Beam(x_min, y_min, x_max, y_max, "90")
            beam.draw()
            print("got to 842")
    for index, row in objects.iterrows():
        m_x = interp1d([0, max(row[6], row[7])], [0, 800])
        m_y = interp1d([0, max(row[6], row[7])], [0, 800])
        obj_type = labels[int(row[4])]
        x_min, y_min, x_max, y_max = float(m_x(row[0])), float(m_y(row[1])), float(m_x(row[2])), float(m_y(row[3]))
        if obj_type == "arrow_down":
            force = Force(x_min, y_min, x_max, y_max, "Down")
            force.draw()

        elif obj_type == "arrow_up":
            force = Force(x_min, y_min, x_max, y_max, "Up")
            force.draw()

        elif obj_type == "arrow_left":
            force = Force(x_min, y_min, x_max, y_max, "Left")
            force.draw()

        elif obj_type == "arrow_right":
            force = Force(x_min, y_min, x_max, y_max, "Right")
            force.draw()

        elif obj_type == "support":
            pin = PinSupport(x_min, y_min, x_max, y_max)
            pin.draw()

        elif obj_type == "roller_support":
            roller = RollerSupport(x_min, y_min, x_max, y_max)
            roller.draw()

        elif obj_type == "load_up":
            print("load_up")
            load = Load(x_min, y_min, x_max, y_max, "Up")
            load.draw()

        elif obj_type == "load_down":
            print("load_up")
            load = Load(x_min, y_min, x_max, y_max, "Down")
            load.draw()

        elif obj_type == "clockwise_bottom":
            moment = Moment(x_min, y_min, x_max, y_max, "Clockwise", "Bottom")
            moment.draw()
        
        elif obj_type == "clockwise_top":
            moment = Moment(x_min, y_min, x_max, y_max, "Clockwise", "Top")
            moment.draw()

        elif obj_type == "clockwise_left":
            moment = Moment(x_min, y_min, x_max, y_max, "Clockwise", "Left")
            moment.draw()

        elif obj_type == "clockwise_right":
            moment = Moment(x_min, y_min, x_max, y_max, "Clockwise", "Right")
            moment.draw()

        elif obj_type == "counterclockwise_bottom":
            moment = Moment(x_min, y_min, x_max, y_max, "Counterclockwise", "Bottom")
            moment.draw()

        elif obj_type == "counterclockwise_top":
            moment = Moment(x_min, y_min, x_max, y_max, "Counterclockwise", "Top")
            moment.draw()

        elif obj_type == "counterclockwise_left":
            moment = Moment(x_min, y_min, x_max, y_max, "Counterclockwise", "Left")
            moment.draw()

        elif obj_type == "counterclockwise_right":
            moment = Moment(x_min, y_min, x_max, y_max, "Counterclockwise", "Right")
            moment.draw()
    for index, row in objects.iterrows():
        m_x = interp1d([0, max(row[6], row[7])], [0, 800])
        m_y = interp1d([0, max(row[6], row[7])], [0, 800]) # Om vanligt koordinatsystem, byt 3 och 1 nedan och 800, 0 t.v.
        obj_type = labels[int(row[4])]
        x_min, y_min, x_max, y_max = float(m_x(row[0])), float(m_y(row[1])), float(m_x(row[2])), float(m_y(row[3]))
        
        if obj_type == "ground":
            surface = Surface(x_min, y_min, x_max, y_max)
            surface.draw()



def fe_input():
    """
    :return:
    """
    output = {}
    for beam in beam_list:
        index = beam_list.index(beam)
        beam_objects = []
        for obj_type in beam.objects:
            for obj in beam.objects[obj_type]:
                if beam.orientation == "0":
                    if obj.side in ["Top", "Bottom"]:
                        beam_objects.append((str(obj), obj.point_index, obj.magnitude)) 
                    elif obj.side == "Left":
                        beam_objects.append((str(obj), 0, obj.magnitude)) 
                    elif obj.side == "Right":
                        beam_objects.append((str(obj), 11, obj.magnitude)) 
                elif beam.orientation == "90":
                    if obj.side in ["Left", "Right"]:
                        beam_objects.append((str(obj), obj.point_index, obj.magnitude)) 
                    elif obj.side == "Top":
                        beam_objects.append((str(obj), 0, obj.magnitude))
                    elif obj.side == "Bottom":
                        beam_objects.append((str(obj), 11, obj.magnitude))
        output['Beam' + str(index)] = beam_objects
    return output


def delete_object(obj):
    """
    Deletes an object
    :param obj:
    :return:
    """
    obj.beam.objects[str(obj) + "s"].remove(obj)
    for shape in obj.shapes:
        m_cnv.delete(shape)


def set_magnitude(obj, entry):
    """
    Unclear
    :param obj:
    :param entry:
    :return:
    """
    if entry >= 0:
        if isinstance(obj, Moment):
            if obj.rotation == 'Clockwise':
                obj.magnitude = entry*(-1)
            else:
                obj.magnitude = entry
        else:
            if obj.direction in ['Up', 'Right']:
                obj.magnitude = entry
            else:
                obj.magnitude = entry*(-1)
    else:
        if isinstance(obj, Force):
            if obj.direction == 'Up':
                new_obj = Force(obj.x_min, obj.y_min, obj.x_max, obj.y_max, 'Down', obj)
                new_obj.magnitude = entry
            elif obj.direction == 'Down':
                new_obj = Force(obj.x_min, obj.y_min, obj.x_max, obj.y_max, 'Up', obj)
                new_obj.magnitude = entry*(-1)
            elif obj.direction == 'Left':
                new_obj = Force(obj.x_min, obj.y_min, obj.x_max, obj.y_max, 'Right', obj)
                new_obj.magnitude = entry
            elif obj.direction == 'Right':
                new_obj = Force(obj.x_min, obj.y_min, obj.x_max, obj.y_max, 'Left', obj)
                new_obj.magnitude = entry*(-1)
        elif isinstance(obj, Moment):
            if obj.rotation == 'Clockwise':
                new_obj = Moment(obj.x_min, obj.y_min, obj.x_max, obj.y_max, 'Counterclockwise', obj.side, obj)
                new_obj.magnitude = entry*(-1)
            elif obj.rotation == 'Counterclockwise':
                new_obj = Moment(obj.x_min, obj.y_min, obj.x_max, obj.y_max, 'Clockwise', obj.side, obj)
                new_obj.magnitude = entry
        elif isinstance(obj, Load):
            if obj.direction == 'Up':
                new_obj = Load(obj.x_min, obj.y_min, obj.x_max, obj.y_max, 'Down', obj)
                new_obj.magnitude = entry
            if obj.direction == 'Down':
                new_obj = Load(obj.x_min, obj.y_min, obj.x_max, obj.y_max, 'Up', obj)
                new_obj.magnitude = entry*(-1)
        new_obj.draw()
        delete_object(obj)
        obj = new_obj
    return obj


def create_entries():
    """
    Adds entries for changing the magnitude and direction of moment, loads and forces.
    :return: entries, labels, and listboxes for units.
    """
    force_entries = []
    moment_entries = []
    load_entries = []
    objects = beam_list[0].objects
    # len item in Loads = 4
    # len item in Forces = 3
    # len item in Moment = 3

    def calculate():
        # fe_input = fe_input()
        """
        Converts the image to a format usable in the FE-calculation script.
        ----------------------------
        :param: none.
        ----------------------------
        :return: a dictionary where the keys are the beams in the image and the values are the different objects
                 connected to the beam
        """
        def convert_unit(unit):
            """
            Converts the prefixes (kN, MNm, N/m) to powers of ten (1000, 1000000, 1).
            :param unit: A prefix followed by the unit corresponding to loads, moments and forces (N, Nm, N/m)
            :return:
            """
            split = unit.split("N")[0]
            output = 1
            if split == "k":
                output = 1000
            elif split == "M":
                output = 1000000
            elif split == "G":
                output = 1000000000
            return output

        for e in force_entries:
            magnitude = float(e[0].get())
            scale_factor = convert_unit(str(e[2].get()))
            scaled_magnitude = magnitude * scale_factor
            obj = e[1].cget("text")
            for beam in beam_list:
                for force in beam.objects["Forces"]:
                    if force.label == obj:
                        ob = force
            set_magnitude(ob, scaled_magnitude)
            e[0].delete(0, END)
            e[0].insert(0, str(abs(magnitude)))

        for e in moment_entries:
            magnitude = float(e[0].get())
            scale_factor = convert_unit(str(e[2].get()))
            scaled_magnitude = magnitude * scale_factor
            obj = e[1].cget("text")
            for beam in beam_list:
                for moment in beam.objects["Moments"]:
                    if moment.label == obj:
                        ob = moment
            set_magnitude(ob, scaled_magnitude)
            e[0].delete(0, END)
            e[0].insert(0, str(abs(magnitude)))

        for e in load_entries:
            magnitude = float(e[0].get())
            scale_factor = convert_unit(str(e[2].get()))
            scaled_magnitude = magnitude * scale_factor
            obj = e[1].cget("text")
            for beam in beam_list:
                for load in beam.objects["Loads"]:
                    if load.label == obj:
                        ob = load
            set_magnitude(ob, scaled_magnitude)
            e[0].delete(0, END)
            e[0].insert(0, str(abs(magnitude)))

        print("Output to the FE-calculation script")
        print(fe_input())

    calc_button = Button(e_cnv, text="Calculate", command=lambda: calculate())
    calc_button.pack(side=BOTTOM)

    for load in objects["Loads"]:
        entry_field = Canvas(e_cnv)
        entry_field.pack()

        unit = Spinbox(entry_field, values=("N/m", "kN/m", "MN/m", "GN/m"))
        unit.pack(side=RIGHT)

        label = Label(entry_field, text=load.label)
        label.pack(side=LEFT)

        entry = Entry(entry_field)
        entry.pack(side=LEFT)
        entry.insert(0, "1.0")

        load_entries.append((entry, label, unit))

    for force in objects["Forces"]:
        entry_field = Canvas(e_cnv)
        entry_field.pack()

        unit = Spinbox(entry_field, values=("N", "kN", "MN", "GN"))
        unit.pack(side=RIGHT)

        label = Label(entry_field, text=force.label)
        label.pack(side=LEFT)

        entry = Entry(entry_field)
        entry.pack(side=LEFT)
        entry.insert(0, "1.0")

        force_entries.append((entry, label, unit))

    for moment in objects["Moments"]:
        entry_field = Canvas(e_cnv)
        entry_field.pack()

        label = Label(entry_field, text=moment.label)
        label.pack(side=LEFT)

        unit = Spinbox(entry_field, values=("Nm", "kNm", "MNm", "GNm"))
        unit.pack(side=RIGHT)

        entry = Entry(entry_field)
        entry.pack(side=LEFT)
        entry.insert(0, "1.0")

        moment_entries.append((entry, label, unit))



draw_all_objects()

create_entries()
# m_cnv.update()
m_cnv.postscript(file="imageGenerator/bild.png", colormode='color')

im1 = Image.open(os.path.join(os.getcwd(),"imageGenerator/bild.png"))
# im1.save(os.path.join(os.getcwd(),"imageGenerator/bild.jpg"))

mainloop()
