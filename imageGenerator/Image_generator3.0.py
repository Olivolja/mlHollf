from tkinter import *
import math as m
import numpy as np
import random as r
import pandas as pd
from scipy.interpolate import interp1d
from PIL import Image
import time
import sys
root = Tk()
m_cnv = Canvas(root, width=1000, height=1000)
m_cnv.pack(side=LEFT)
e_cnv = Canvas(root, bg="red")
e_cnv.pack(side=RIGHT)
beam_list = []
node_list = []
truss_beams = []
force_number = 0
moment_number = 0
load_number = 0
number_of_forces = 0
number_of_moments = 0
number_of_loads = 0
surface_points = {"Bottom": [], "Top": [], "Left": [], "Right": []} # To find the closest item for a surface. Each list: 
                                                                    # (the item, (starting coordinate), (ending coordinate)) 
def get_classes():
    labels = []
    file = open(r'C:\Users\tobia\Desktop\Kandidat\data_classes.txt')
    for line in file:
        labels.append(line.rstrip("\n"))
    return labels


labels = get_classes()
print(labels)

<<<<<<< HEAD
labels = ["PinSupport", "RollerSupport", "BeamLine0", "Surface", "Node", "ArrowUp", "ArrowDown", 
          "ArrowLeft", "ArrowRight", "ClockwiseRight", "ClockwiseTop", "ClockwiseLeft", "ClockwiseBottom", 
          "CounterclockwiseRight", "CounterclockwiseTop", "CounterclockwiseLeft", "CounterclockwiseBottom", 
          "Beam0", "BeamLine45", "BeamLine90", "Beam90", "BeamLine135", "Beam135", "LoadDown", "LoadUp"]
labels = ["LoadDown", "LoadUp", "Beam0", "Counterclockwise", "CounterclockwiseRight", "ArrowRight", 
          "CounterclockwiseTop", "ArrowDown", "Clockwise", "ClockwiseRight", "ArrowLeft", 
          "CounterclockwiseBottom", "ArrowUp", "ClockwiseLeft", "Support", "ClockwiseTop", 
          "ClockwiseBottom", "CounterclockwiseLeft", "Surface", "RollerSupport", "Beam90"]
=======
>>>>>>> adca8deb3bf77232d111f85583d3f9997c3be6b8

# Method for finding closest point on any beam returning that point and the corresponding beam
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

    return shortest_distance_coordinates, closest_beam
    try:
        return shortest_distance_coordinates, closest_beam
    except UnboundLocalError:
        sys.exit("Error: no beam identified")


# Method for finding the closest possible object for a surface to be put on 
# (eg a beam or any kind of support). Returns the object, its coordinates 
# as they were on the input and the coordinates where it will be drawn.
def find_closest_object(coord, sides=["Bottom", "Top", "Left", "Right"]):
    shortest_distance = m.inf
    shortest_distance_coordinates = (m.inf, m.inf)
    for side in sides:
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


def create_label(obj):
    if isinstance(obj, Force):
        global force_number
        force_number += 1
        text = 'F' + str(force_number)
        if number_of_forces == 1:
            text = 'F'
        else: 
            text = 'F' + str(force_number)
    elif isinstance(obj, Moment):
        global moment_number
        moment_number += 1
        text = 'M' + str(moment_number)
        if number_of_moments == 1:
            text = 'M'
        else:
            text = 'M' + str(moment_number)
    elif isinstance(obj, Load):
        global load_number
        load_number += 1
        text = 'W' + str(load_number)
        if number_of_loads == 1:
            text = 'W'
        else:
            text = 'W' + str(load_number)

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
        
print("Snälla funka")

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

    def draw(self):
        m_cnv.create_rectangle(self.x_min, self.y_min, self.x_max, self.y_max, fill="")
        beam_list.append(self) 


# Defining a force of arbitrary vertical or horizontal direction  
class Force:
    def __init__(self, x_min, y_min, x_max, y_max, direction):
        self.direction = direction
        x_mid = (x_max + x_min)/2
        y_mid = (y_max + y_min)/2
        if direction == "Up" or direction == "Right":
            self.magnitude = 1
        else:
            self.magnitude = -1
        if direction == "Up" or direction == "Down": # direction i raden under
            # Checking if the top or bottom of the force is closest to a beam, where
            # index 1 corresponds to the top of the force and index 2 to the bottom
            (closest_x1, closest_y1), beam1 = find_closest_point((x_mid, y_min), ["Bottom", "Top"])
            (closest_x2, closest_y2), beam2 = find_closest_point((x_mid, y_max), ["Bottom", "Top"])
            dist1 = compute_distance((closest_x1, closest_y1), (x_mid, y_min))
            dist2 = compute_distance((closest_x2, closest_y2), (x_mid, y_max))
            if dist1 > dist2: # True if bottom point of force is closest to a beam
                self.beam = beam2
                self.x_mid = closest_x2
                self.y_max = closest_y2
                self.y_min = self.y_max - self.beam.length * 0.2 # Length of arrow is set 
                self.closest_point = (closest_x2, closest_y2)    # to 20% of beam length
            else:
                self.beam = beam1                
                self.x_mid = closest_x1
                self.y_min = closest_y1
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
                self.closest_point = (closest_x1, closest_y1)
            self.x_max, self.x_min = self.x_mid, self.x_mid
                self.point_index = self.beam.points['Bottom'].index(self.closest_point)
                self.side = 'Bottom'
        elif direction == "Left" or direction == "Right":
            # Checking if the left or right side of the force is closest to a beam, where
            # index 1 corresponds to the left side and index 2 to the right
            (closest_x1, closest_y1), beam1 = find_closest_point((x_min, y_mid), ["Left", "Right"])
            (closest_x2, closest_y2), beam2 = find_closest_point((x_max, y_mid), ["Left", "Right"])
            dist1 = compute_distance((closest_x1, closest_y1), (x_min, y_mid))
            dist2 = compute_distance((closest_x2, closest_y2), (x_max, y_mid)) 
            if dist1 > dist2: # True if right side of force is closest to a beam
                self.beam = beam2
                self.x_max = closest_x2
                self.y_mid = closest_y2
            (closest_x, closest_y), self.beam = find_closest_point((x_min, y_mid), ["Left", "Right"])
            self.closest_point = (closest_x, closest_y)
            self.y_mid = self.y_max = self.y_min = closest_y
            if self.closest_point in self.beam.points["Right"]:
                self.x_max = closest_x
                self.x_min = self.x_max - self.beam.length * 0.2
                self.closest_point = (closest_x2, closest_y2)
                self.point_index = self.beam.points['Right'].index(self.closest_point)
                self.side = 'Right'
            else:
                self.beam = beam1
                self.x_min = closest_x1
                self.y_mid = closest_y1
                self.x_min = closest_x
                self.x_max = self.x_min + self.beam.length * 0.2
                self.closest_point = (closest_x1, closest_y1)
            self.y_max, self.y_min = self.y_mid, self.y_mid
    
                self.point_index = self.beam.points['Left'].index(self.closest_point)
                self.side = 'Left'
    # Drawing the arrow and appending it to the list of objects acting on the corresponding beam
    def draw(self):
        if self.direction == "Up":
            m_cnv.create_line(self.x_mid, self.y_min, self.x_mid, self.y_max, arrow="first")
        elif self.direction == "Down":
            m_cnv.create_line(self.x_mid, self.y_min, self.x_mid, self.y_max, arrow="last")
        elif self.direction == "Left":
            m_cnv.create_line(self.x_min, self.y_mid, self.x_max, self.y_mid, arrow="first")
        elif self.direction == "Right":
            m_cnv.create_line(self.x_min, self.y_mid, self.x_max, self.y_mid, arrow="last")
        create_label(self)
        self.beam.objects["Forces"].append(self)


# Defining a pin support as a triangle with sidelength 15% of corresponding beams length
class PinSupport:
    def __init__(self, x_min, y_min, x_max, y_max, size=0.15):
        x_mid = (x_max + x_min)/2
        y_mid = (y_max + y_min)/2
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
            self.orientation = "Bottom"
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
            self.orientation = "Top"
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
            self.orientation = "Left"
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
            self.orientation = "Right"
            self.corner1 = (self.x_min, self.y_mid)
            self.corner2 = (self.x_max, self.y_min)
            self.corner3 = (self.x_max, self.y_max)
            surface_points["Right"].append((self, (x_max, y_mid), (self.x_max, self.y_mid)))
        self.point_index = self.beam.points[self.orientation].index(self.closest_point)

    def draw(self):
        m_cnv.create_polygon(self.corner1, self.corner2, self.corner3, fill="", outline="Black")
        self.beam.objects["Pins"].append(self)


# Defining a roller support as a pin support with sidelength 9.51% of corresponding beams length
# plus two extra circles with half that length as diameter
class RollerSupport:
    def __init__(self, x_min, y_min, x_max, y_max):
        x_mid = (x_min + x_max)/2
        y_mid = (y_min + y_max)/2
        pin_size = 0.0951
        ps = PinSupport(x_min, y_min, x_max, y_max, pin_size)
        self.ps = ps
        surface_points[self.ps.orientation].pop() # Removing the surface point that was added when the pin support was created
        self.surface_width = 1.2 * self.ps.beam.length * pin_size
        self.surface_height = self.surface_width
        if self.ps.orientation == "Bottom":
            self.circle_box1 = (ps.x_min, ps.y_max + ps.beam.length * pin_size/2, ps.x_mid, ps.y_max)
            self.circle_box2 = (ps.x_mid, ps.y_max + ps.beam.length * pin_size/2, ps.x_max, ps.y_max)
            self.orientation = "Bottom"
            surface_points["Bottom"].append((self, (x_mid, y_max), (ps.x_mid, ps.y_max + ps.beam.length * pin_size/2)))

        elif self.ps.orientation == "Top":
            self.circle_box1 = (ps.x_min, ps.y_min - ps.beam.length * pin_size/2, ps.x_mid, ps.y_min)
            self.circle_box2 = (ps.x_mid, ps.y_min - ps.beam.length * pin_size/2, ps.x_max, ps.y_min)
            self.orientation = "Top"
            surface_points["Top"].append((self, (x_mid, y_min), (ps.x_mid, ps.y_min - ps.beam.length * pin_size/2)))
        elif self.ps.orientation == "Left":
            self.circle_box1 = (ps.x_min - ps.beam.length * pin_size/2, ps.y_min, ps.x_min, ps.y_mid)
            self.circle_box2 = (ps.x_min - ps.beam.length * pin_size/2, ps.y_mid, ps.x_min, ps.y_max)
            self.orientation = "Left"
            surface_points["Left"].append((self, (x_min, y_mid), (ps.x_min - ps.beam.length * pin_size/2, ps.y_mid)))
        elif self.ps.orientation == "Right":
            self.circle_box1 = (ps.x_max, ps.y_min, ps.x_max + ps.beam.length * pin_size/2, ps.y_mid)
            self.circle_box2 = (ps.x_max, ps.y_mid, ps.x_max + ps.beam.length * pin_size/2, ps.y_max)
            self.orientation = "Right"
            surface_points["Right"].append((self, (x_max, y_mid), (ps.x_max + ps.beam.length * pin_size/2, ps.y_mid)))

    def draw(self):
        self.ps.draw()
        self.ps.beam.objects["Pins"].pop() # Elegant way of removing the extra pin support added to the objects dictionary
        m_cnv.create_oval(self.circle_box1)
        m_cnv.create_oval(self.circle_box2)
        self.ps.beam.objects["Rollers"].append(self)


class Moment:
    def __init__(self, x_min, y_min, x_max, y_max, rotation, rel_pos): # rel_pos samma som orientation, lite inkonsekvent
        x_mid, y_mid = (x_min + x_max)/2, (y_min + y_max)/2
        self.rel_pos = rel_pos
        self.rotation = rotation
        self.closest_point, self.beam = find_closest_point((x_mid, y_mid), [rel_pos])
        self.radius = self.beam.length * 0.075
        self.point_index = self.beam.points[rel_pos].index(self.closest_point)
        if rotation == "Clockwise":
            self.magnitude = -1
        elif rotation == "Counterwise":
        elif rotation == "Counterclockwise":
            self.magnitude = 1
        if rel_pos == "Bottom":
            self.x_mid = self.closest_point[0]
            self.x_min = self.x_mid - self.radius
            self.x_max = self.x_mid + self.radius
            self.y_min = self.closest_point[1] + self.radius/2
            self.y_max = self.y_min + self.radius
        elif rel_pos == "Top":
            self.x_mid = self.closest_point[0]
            self.x_min = self.x_mid - self.radius
            self.x_max = self.x_mid + self.radius
            self.y_max = self.closest_point[1] - self.radius/2
            self.y_min = self.y_max - self.radius
        elif rel_pos == "Left":
            self.x_max = self.closest_point[0] - self.radius/2
            self.x_min = self.x_max - self.radius
            self.y_mid = self.closest_point[1]
            self.y_min = self.y_mid - self.radius
            self.y_max = self.y_mid + self.radius
        elif rel_pos == "Right":
            self.x_min = self.closest_point[0] + self.radius/2
            self.x_max = self.x_min - self.radius
            self.y_mid = self.closest_point[1]
            self.y_min = self.y_mid - self.radius
            self.y_max = self.y_mid + self.radius

    def draw(self):
        if self.rel_pos == "Bottom":
            p1x = self.x_mid + self.radius * m.cos(m.radians(-15))
            p1y = self.y_min - self.radius * m.sin(m.radians(-15))
            p2y = self.y_min
            if self.rotation == "Counterwise":
            if self.rotation == "Counterclockwise":
                p2x = p1x + (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                m_cnv.create_line(p1x, p1y, p2x, p2y, arrow="last", width=2, arrowshape="16 20 6")

            for t in range(1, 1509):
                theta = -15 - t / 10
                p2x = self.x_mid + self.radius * m.cos(m.radians(theta))
                p2y = self.y_min - self.radius * m.sin(m.radians(theta))
                m_cnv.create_line(p1x, p1y, p2x, p2y, width=2)
                p1x = p2x
                p1y = p2y

            if self.rotation == "Clockwise":
                p2x = p1x - (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                m_cnv.create_line(p1x, p1y, p2x, self.y_min, arrow="last", width=2, arrowshape="16 20 6")

        elif self.rel_pos == "Top":
            p1x = self.x_mid + self.radius * m.cos(m.radians(15))
            p1y = self.y_max - self.radius * m.sin(m.radians(15))
            p2y = self.y_max
            if self.rotation == "Clockwise":
                p2x = p1x + (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                m_cnv.create_line(p1x, p1y, p2x, p2y, arrow="last", width=2, arrowshape="16 20 6")
            for t in range(1, 1509):
                theta = -15 - t / 10
                p2x = self.x_mid + self.radius * m.cos(m.radians(theta))
                p2y = self.y_max - self.radius * m.sin(m.radians(theta))
                m_cnv.create_line(p1x, p1y, p2x, p2y, width=2)
                p1x = p2x
                p1y = p2y
            if self.rotation == "Counterwise":
            if self.rotation == "Counterclockwise":
                p2x = p1x - (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                m_cnv.create_line(p1x, p1y, p2x, self.y_max, arrow="last", width=2, arrowshape="16 20 6")

        elif self.rel_pos == "Left":
            p1x = self.x_max + self.radius * m.cos(m.radians(255))
            p1y = self.y_mid - self.radius * m.sin(m.radians(255))
            p2x = self.x_max
            if self.rotation == "Counterwise":
            if self.rotation == "Counterclockwise":
                p2y = p1y + (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                m_cnv.create_line(p1x, p1y, p2x, p2y, arrow="last", width=2, arrowshape="16 20 6")
            for t in range(1, 1509):
                theta = 255 - t / 10
                p2x = self.x_max + self.radius * m.cos(m.radians(theta))
                p2y = self.y_mid - self.radius * m.sin(m.radians(theta))
                m_cnv.create_line(p1x, p1y, p2x, p2y, width=2)
                p1x = p2x
                p1y = p2y
            if self.rotation == "Clockwise":
                p2y = p1y - (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                m_cnv.create_line(p1x, p1y, self.x_max, p2y, arrow="last", width=2, arrowshape="16 20 6")

        elif self.rel_pos == "Right":
            p1x = self.x_min + self.radius * m.cos(m.radians(-75))
            p1y = self.y_mid - self.radius * m.sin(m.radians(-75))
            p2x = self.x_min
            # Draw the arrow part of the moment
            if self.rotation == "Clockwise":
                p2y = p1y + (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                m_cnv.create_line(p1x, p1y, p2x, p2y, arrow="last", width=2, arrowshape="16 20 6")

            # Draws the rest of the moment
            for t in range(1, 1509):
                theta = -75 + t / 10
                p2x = self.x_min + self.radius * m.cos(m.radians(theta))
                p2y = self.y_mid - self.radius * m.sin(m.radians(theta))
                m_cnv.create_line(p1x, p1y, p2x, p2y, width=2)
                p1x = p2x
                p1y = p2y
            if self.rotation == "Counterwise":
            if self.rotation == "Counterclockwise":
                p2y = p1y - (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                m_cnv.create_line(p1x, p1y, self.x_min, p2y, arrow="last", width=2, arrowshape="16 20 6")
        create_label(self)
        self.beam.objects["Moments"].append(self)


class Load:
    def __init__(self, x_min, y_min, x_max, y_max, direction):
        y_mid = (y_min + y_max)/2
        self.direction = direction
        self.leftmost_point, self.beam = find_closest_point((x_min, y_mid), ["Bottom", "Top"])
        self.rightmost_point, self.beam = find_closest_point((x_max, y_mid), ["Bottom", "Top"])
        self.closest_point = self.rightmost_point
        self.x_min = self.leftmost_point[0]
        self.x_max = self.rightmost_point[0]
        self.length = self.x_max - self.x_min
        self.height = self.beam.length/6
        if direction == "Up":
            self.magnitude = 1
        elif direction == "Down":
            self.magnitude = -1
        if self.closest_point in self.beam.points["Bottom"]:
            self.y_min = self.closest_point[1]
            self.y_max = self.y_min + self.height
            self.side = 'Bottom'
        elif self.closest_point in self.beam.points["Top"]:
            self.y_max = self.closest_point[1]
            self.y_min = self.y_max - self.height
            self.side = 'Top'
        self.no_arrows = int(self.length/50)
        self.sep = self.length / self.no_arrows
        self.point_indices = (self.beam.points[self.side].index(self.leftmost_point), self.beam.points[self.side].index(self.rightmost_point))


    def draw(self):
        py1 = self.leftmost_point[1]
        py2 = py1 - self.height
        if self.direction == "Down":
            for i in range(self.no_arrows + 1):
                px = self.leftmost_point[0] + i * self.sep
                m_cnv.create_line(px, py1, px, py2, arrow="first") # Kan krympa med first/last som variabel
        elif self.direction == "Up":
            for i in range(self.no_arrows + 1):
                px = self.leftmost_point[0] + i * self.sep
                m_cnv.create_line(px, py1, px, py2, arrow="last")

        m_cnv.create_line(self.leftmost_point[0], self.leftmost_point[1], self.rightmost_point[0],
                          self.rightmost_point[1])
        m_cnv.create_line(self.leftmost_point[0], py2, self.rightmost_point[0], py2)
        create_label(self)
        self.beam.objects["Loads"].append(self)


class Surface:
    def __init__(self, x_min, y_min, x_max, y_max):
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
            self.no_lines = int(self.height/8)
            if isinstance(self.closest_item, Beam): # sammanfoga längst ner i draw?
                self.point_index = self.closest_item.points[self.side].index(self.closest_point)


    def draw(self):
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

        if type(self.closest_item) == Beam: # Rätt?
        if isinstance(self.closest_item, Beam):
            self.closest_item.objects["Surfaces"].append(self) 


def find_closest_node(coord):
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
    try:
        df = pd.read_csv(r'C:\Users\admin\Desktop\Detection_Results_test.csv')
    except:
        df = pd.read_csv(r'C:\Users\tobia\Desktop\Detection_Results_test.csv')
        #df = pd.read_csv(r'C:\Users\tobia\Desktop\Kandidat\mlHollf\TrainYourOwnYOLO\Data\Source_Images\Test_Image_Detection_Results\Detection_Results.csv')
    df1 = df[["xmin", "ymin", "xmax", "ymax", "label"]]
        df = pd.read_csv(r'C:\Users\tobia\Desktop\resultatHebbeBatch16\Detection_Results.csv')
        # df = pd.read_csv(r'C:\Users\tobia\Desktop\Detection_Results_test.csv')
        # df = pd.read_csv(r'C:\Users\tobia\Desktop\Kandidat\mlHollf\TrainYourOwnYOLO\Data\Source_Images\Test_Image_Detection_Results\Detection_Results.csv')
    df1 = df[["xmin", "ymin", "xmax", "ymax", "label", "confidence", "x_size", "y_size"]]
    df1 = delete_overlapping_objects(df1)
    return (df1)


def delete_overlapping_objects(objects): # Sannolikheter, Momentpilar åt olika håll -> välj den som har rätt typ av balkpunkt närmast, grej för att ändra position om krock efter ändringar
    for index1, obj1 in objects.iterrows():
        for index2, obj2 in objects.iterrows():
            if index1 == index2:
                continue
            type1 = labels[obj1[4]]
            type2 = labels[obj2[4]]
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
    #labels = ["LoadDown", "LoadUp", "Beam0", "Counterclockwise", "CounterclockwiseRight", "ArrowRight", 
    #      "CounterclockwiseTop", "ArrowDown", "Clockwise", "ClockwiseRight", "ArrowLeft", 
    #      "CounterclockwiseBottom", "ArrowUp", "ClockwiseLeft", "Support", "ClockwiseTop", 
    #      "ClockwiseBottom", "CounterclockwiseLeft", "RollerSupport", "Beam90"]


def draw_all_objects():
    objects = get_objects()
    m_x = interp1d([0, img_width], [0, 800])
    m_y = interp1d([0, img_height], [800, 0])
    for index, row in objects.iterrows():
        obj_type = labels[row[4]]
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
        print(row[7])
        m_x = interp1d([0, min(row[6], row[7])], [0, 800])
        m_y = interp1d([0, min(row[6], row[7])], [0, 800])
        obj_type = labels[int(row[4])]
        x_min, y_min, x_max, y_max = float(m_x(row[0])), float(m_y(row[1])), float(m_x(row[2])), float(m_y(row[3]))
        if obj_type == "beam":
            beam = Beam(x_min, y_min, x_max, y_max, "0")
            beam.draw()
        elif obj_type == "beam_90":
            beam = Beam(x_min, y_min, x_max, y_max, "90")
            beam.draw()

    for index, row in objects.iterrows():
<<<<<<< HEAD
        obj_type = labels[row[4]]
        m_x = interp1d([0, row[6]], [0, 800])
        m_y = interp1d([0, row[6]], [800, 0])
=======
        m_x = interp1d([0, min(row[6], row[7])], [0, 800])
        m_y = interp1d([0, min(row[6], row[7])], [0, 800])
>>>>>>> adca8deb3bf77232d111f85583d3f9997c3be6b8
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
            load = Load(x_min, y_min, x_max, y_max, "Up")
            load.draw()

        elif obj_type == "load_down":
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

<<<<<<< HEAD
        elif obj_type == "CounterclockwiseBottom":
           moment = Moment(x_min, y_min, x_max, y_max, "Counterwise", "Bottom")
           moment = Moment(x_min, y_min, x_max, y_max, "Counterclockwise", "Bottom")
           moment.draw()

        elif obj_type == "CounterclockwiseTop":
           moment = Moment(x_min, y_min, x_max, y_max, "Counterwise", "Top")
           moment = Moment(x_min, y_min, x_max, y_max, "Counterclockwise", "Top")
           moment.draw()

        elif obj_type == "CounterclockwiseLeft":
           moment = Moment(x_min, y_min, x_max, y_max, "Counterwise", "Left")
           moment = Moment(x_min, y_min, x_max, y_max, "Counterclockwise", "Left")
           moment.draw()

        elif obj_type == "CounterclockwiseRight":
           moment = Moment(x_min, y_min, x_max, y_max, "Counterwise", "Right")
           moment = Moment(x_min, y_min, x_max, y_max, "Counterclockwise", "Right")
           moment.draw()
    for index, row in objects.iterrows():
        obj_type = labels[row[4]]
        m_x = interp1d([0, row[6]], [0, 800])
        m_y = interp1d([0, row[6]], [800, 0])
=======
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
        m_x = interp1d([0, min(row[6], row[7])], [0, 800])
        m_y = interp1d([0, min(row[6], row[7])], [0, 800]) # Om vanligt koordinatsystem, byt 3 och 1 nedan och 800, 0 t.v.
>>>>>>> adca8deb3bf77232d111f85583d3f9997c3be6b8
        obj_type = labels[int(row[4])]
        x_min, y_min, x_max, y_max = float(m_x(row[0])), float(m_y(row[1])), float(m_x(row[2])), float(m_y(row[3]))
        
        if obj_type == "ground":
            surface = Surface(x_min, y_min, x_max, y_max)
            surface.draw()
#["PinSupport", "RollerSupport", "BeamLine0", "Surface", "Node", "ArrowUp", "ArrowDown", 
#          "ArrowLeft", "ArrowRight", "ClockwiseRight", "ClockwiseTop", "ClockwiseLeft", "ClockwiseBottom", 
#          "CounterclockwiseRight", "CounterclockwiseTop", "CounterclockwiseLeft", "CounterclockwiseBottom", 
#          "Beam0", "BeamLine45", "BeamLine90", "Beam90", "BeamLine135", "Beam135", "LoadDown", "LoadUp"]

<<<<<<< HEAD
def fe_input(type):
=======

>>>>>>> adca8deb3bf77232d111f85583d3f9997c3be6b8
def fe_input():
    output = {}
    for beam in beam_list:
        index = beam_list.index(beam)
        beam_objects = []
        for obj_type in beam.objects:
            for obj in beam.objects[obj_type]:
                if isinstance(obj, Force):
                    beam_objects.append(('Force', obj.point_index, obj.side, obj.magnitude)) #index+1?
                elif isinstance(obj, Moment):
                    beam_objects.append(('Moment', obj.point_index, obj.rel_pos, obj.magnitude))
                elif isinstance(obj, Load):
                    beam_objects.append(('Load', obj.point_indices, obj.side, obj.magnitude))
                elif isinstance(obj, PinSupport):
                    beam_objects.append(('PinSupport', obj.point_index, obj.orientation))
                elif isinstance(obj, RollerSupport):
                    beam_objects.append(('RollerSupport', obj.ps.point_index, obj.orientation))
                elif isinstance(obj, Surface):
                    beam_objects.append(('Surface', obj.point_index, obj.side))




    output['Beam' + str(index)] = beam_objects
    print(output)
    return output


    '''
    if type == "beam":
        output = {"beam" : []}
        for beam in beam_list:
            coordinates = (beam.x_min, beam.y_min, beam.x_max, beam.y_max)
            output["beam"].append(coordinates)
            objects = beam.objects
            for type, obj in objects.items():
                if len(obj) > 0:
                    output[type] = []
                for o in obj:
                    coordinates = (o.x_min, o.y_min, o.x_max, o.y_max)
                    output[type].append(coordinates)
        return output
    elif type == "truss":
        print("Skjut mig nu")
        output = {"truss" : []}
        return output
        # En lista över elementen och vilka noder de går mellan
        '''


def create_entries():
    force_entries = []
    moment_entries = []
    load_entries = []
    objects = beam_list[0].objects
    # len item in Loads = 4
    # len item in Forces = 3
    # len item in Moment = 3

    def calculate():
        fe_input = fe_input()
        for e in force_entries:
            magnitude = e[0].get()
            obj = e[1].cget("text")
            # set force[i] magnitude to 'magnitude'

        for e in moment_entries:
            magnitude = e[0].get()
            obj = e[1].cget("text")
            # set moment[i] magnitude to 'magnitude'

        for e in load_entries:
            magnitude = e[0].get()
            obj = e[1].cget("text")
            # set load[i] magnitude to 'magnitude'
        
        print("Output to the FE-calculation script")

    calc_button = Button(e_cnv, text="Calculate", command=lambda: calculate())
    calc_button.pack(side=BOTTOM)

    for load in objects["Loads"]:
        entry_field = Canvas(e_cnv, bg="red")
        entry_field.pack()

        entry = Entry(entry_field)
        entry.pack(side=RIGHT)
        entry.insert(0, 1)

        label = Label(entry_field, text=load.label)
        label.pack(side=LEFT)

        load_entries.append((entry, label))

    for force in objects["Forces"]:
        entry_field = Canvas(e_cnv, bg="red")
        entry_field.pack()

        entry = Entry(entry_field)
        entry.pack(side=RIGHT)
        entry.insert(0, 1)

        label = Label(entry_field, text=force.label)
        label.pack(side=LEFT)

        force_entries.append((entry, label))

    for moment in objects["Moments"]:
        entry_field = Canvas(e_cnv, bg="red")
        entry_field.pack()

        entry = Entry(entry_field)
        entry.pack(side=RIGHT)
        entry.insert(0, 1)
        
        label = Label(entry_field, text=moment.label)
        label.pack(side=LEFT)

        moment_entries.append((entry, label))


draw_all_objects()

create_entries()
m_cnv.update()
m_cnv.postscript(file="bild.png", colormode='color')
#
# im1 = Image.open(r'C:\Users\tobia\Desktop\Kandidat\mlHollf\imageGenerator\bild.png')
# im1.save(r'C:\Users\tobia\Desktop\Kandidat\mlHollf\imageGenerator\bild.jpg')

im1 = Image.open(r'C:\Users\tobia\Desktop\Kandidat\mlHollf\imageGenerator\bild.png')
im1.save(r'C:\Users\tobia\Desktop\Kandidat\mlHollf\imageGenerator\bild.jpg')


mainloop()
