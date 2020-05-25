from tkinter import *
from tkinter import filedialog as fd
import math as m
import numpy as np
import random as r
import pandas as pd
from scipy.interpolate import interp1d
from PIL import Image#, ImageGrab # pyscreenshot för linux?
import time
import sys
import os
import platform
import FEM
#imports depending on OS
if(platform.system() == "Linux"):
    import pyscreenshot as ImageGrab
elif (platform.system() == "Windows" or platform.system() == "Darwin"):
    from PIL import ImageGrab
else:
    raise Exception("we could not find what OS you are running")

root = Tk()
# The main canvas houses the image
root.attributes('-fullscreen', True)  # Tror det är ett annat för python här
m_cnv = Canvas(root, width=800, height=800)
m_cnv.pack(side=LEFT)
# The entry canvas houses the entries to change magnitudes
e_cnv = Canvas(root)
e_cnv.pack(side=RIGHT)
# A frame that houses the attributes for loads, moments and forces
object_frame = Frame(e_cnv, bd=2, padx=2, pady=2, relief=RAISED)
object_frame.grid(row=0, column=0)

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
number_of_beams = 0

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
    """
    :return: labels, a list of classes detected by detector.py
    """
    labels = []
    try:
        # file = open(r'C:\Users\tobia\Desktop\Kandidat\data_classes.txt')
        data_classes = os.path.join(os.getcwd(),"TrainYourOwnYOLO/Data/Model_Weights/data_classes.txt")
        file = open(data_classes)
    except:
        file = open(r'C:\Users\admin\Desktop\data_classes.txt')
    
    for line in file:
        labels.append(line.rstrip("\n"))
    return labels


labels = get_classes()


def find_closest_point(coord, sides=["Bottom", "Top", "Left", "Right"]):
    """

    :param coord: a tuple containing x and y coordinates for the object.
    :param sides: specifies which side of the beam you want to find the closest point in
    :return shortest_distance_coordinates: the coordinates of the closest point on the beam as a x-y tuple
    :return closest_beam: the closest beam to coord (only relevant if you have two or more beams in a image)
    """
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


# TODO kolla om det här är rätt kommenterat
def find_closest_object(coord, sides=["Bottom", "Top", "Left", "Right"]):
    """
    Method for finding the closest possbile object for a surface to be put on (a beam or a support of some kind).
    :param coord: a tuple of the x and y coordinates of the middlepoint of the surface.
    :param sides: specifies which sides of an object that should be searched.
    :return closest item: the item on which to put a surface.
    :return closest side: the side of the item on which to put the surface on.
    :return shortest_distance_coordinates: the coordinates the surface should be drawn on.
    """
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


def compute_distance(point1, point2):
    """
    Computes the distance between two points
    :param point1: a x-y tuple representing a point
    :param point2: a x-y tuple representing a point
    :return: the minimum distance between them (Pythagorean theorem)
    """
    x1, y1 = point1
    x2, y2 = point2
    return m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def create_label(obj, old_object=None):
    """
    Used to write out the labels of the different forces, moments and loads.
    :param obj: TODO
    :param old_object: TODO
    :return: TODO
    """
    if old_object == None:
        if isinstance(obj, Force):
            global force_number
            force_number += 1
            if number_of_forces == 1:
                text = 'P'
            else: 
                text = 'P' + str(force_number)
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
                text = 'Q'
            else:
                text = 'Q' + str(load_number)
        elif isinstance(obj, Beam):
            if number_of_beams > 1:
                text = 'B' + str(beam_list.index(obj)+1)
            else:
                obj.label = "Beam length"
                return

    else:
        text = old_object.label
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    text = text.translate(SUB)
    obj.label = text

    while True:
        x = obj.x_max + 9
        y = obj.y_max + 9 
        if not m_cnv.find_overlapping(x-8, y-8, x+8, y+8): # no items there
            break
        x = obj.x_max + 9
        y = obj.y_min - 9
        if not m_cnv.find_overlapping(x-8, y-8, x+8, y+8): # no items there
            break
        x = obj.x_min - 9
        y = obj.y_max + 9
        if not m_cnv.find_overlapping(x-8, y-8, x+8, y+8): # no items there
            break
        x = obj.x_min - 9
        y = obj.y_min - 9
        if not m_cnv.find_overlapping(x-8, y-8, x+8, y+8): # no items there
            break

        found_position = False
        for i in range(10):
            x = obj.x_max + 9
            y = obj.y_max - i*(obj.y_max-obj.y_min)/10 
            if not m_cnv.find_overlapping(x-8, y-8, x+8, y+8): # no items there
                found_position = True
                break
            x = obj.x_max - i*(obj.x_max-obj.x_min)/10
            y = obj.y_min - 9
            if not m_cnv.find_overlapping(x-8, y-8, x+8, y+8): # no items there
                found_position = True
                break
            x = obj.x_min - 9
            y = obj.y_max - i*(obj.y_max-obj.y_min)/10
            if not m_cnv.find_overlapping(x-8, y-8, x+8, y+8): # no items there
                found_position = True
                break
            x = obj.x_max - i*(obj.x_max-obj.x_min)/10
            y = obj.y_max + 9
            if not m_cnv.find_overlapping(x-8, y-8, x+8, y+8): # no items there
                found_position = True
                break
        if found_position:
            break

        return # Nowhere to put the label, what do?

    
    m_cnv.create_text(x, y, font = ('Times', '-15'), text=text)
    return text
        

class Beam:
    """
    Defining the beam object
    """
    def __init__(self, x_min, y_min, x_max, y_max, orientation):
        y_mid = (y_max + y_min)/2
        x_mid = (x_max + x_min)/2
        self.height = 4
        self.inertia = 1  # TODO good standard value
        self.youngs_modulus = 1  # TODO good standard value
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
            point_distance = self.length/12
            # Creating twelve points on the top and bottom side of the beam and 
            # one on the middle of the left and right side.
            for i in range(13):
                self.points["Bottom"].append((self.x_min + i * point_distance, self.y_max))
                self.points["Top"].append((self.x_min + i * point_distance, self.y_min))
            self.points["Left"].append((self.x_min, y_mid))
            self.points["Right"].append((self.x_max, y_mid))
            # A suface could only be placed at any of the short ends of the beam.
            surface_points["Left"].append((self, (self.x_min, y_mid), (self.x_min, y_mid)))   # If the surface is connected to a beam the
            surface_points["Right"].append((self, (self.x_max, y_mid), (self.x_max, y_mid)))  # middle point were they connect won´t be changed
            self.surface_height = self.height*10

        elif orientation == "90":
            self.length = y_max - y_min
            self.x_max = x_mid + self.height/2
            self.x_min = x_mid - self.height/2
            self.y_min = y_min
            self.y_max = y_max
            point_distance = self.length/12
            # Creating twelve points on the top and bottom side of the beam and 
            # one on the middle of the left and right side.
            for i in range(13):
                self.points["Left"].append((self.x_min, self.y_max - i * point_distance))
                self.points["Right"].append((self.x_max, self.y_max - i * point_distance))
            self.points["Bottom"].append((x_mid, self.y_max))
            self.points["Top"].append((x_mid, self.y_min))
            # A suface could only be placed at any of the short ends of the beam.
            surface_points["Bottom"].append((self, (x_mid, self.y_max), (x_mid, self.y_max))) # If the surface is connected to a beam the
            surface_points["Top"].append((self, (x_mid, self.y_min), (x_mid, self.y_min)))    # middle point were they connect won´t be changed
            self.surface_width = self.height*10

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
        self.shapes = []
        x_mid = (x_max + x_min)/2
        y_mid = (y_max + y_min)/2
        if direction in ["Up", "Down"]: # direction i raden under
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
        elif direction in ["Left", "Right", "Horizontal"] :
            (closest_x, closest_y), self.beam = find_closest_point((x_min, y_mid), ["Left", "Right"])
            self.closest_point = (closest_x, closest_y)
            self.y_mid = self.y_max = self.y_min = closest_y
            if self.closest_point in self.beam.points["Right"]:
                self.x_min = closest_x
                self.x_max = self.x_min + self.beam.length * 0.2
                self.point_index = self.beam.points['Right'].index(self.closest_point)
                self.side = 'Right'
                if direction == "Horizontal":
                    self.direction = "Left"
            else:
                self.x_max = closest_x
                self.x_min = self.x_max - self.beam.length * 0.2
                self.point_index = self.beam.points['Left'].index(self.closest_point)
                self.side = 'Left'
                if direction == "Horizontal":
                    self.direction = "Right"

    def __str__(self):
        return "Force"

    # Drawing the arrow and appending it to the list of objects acting on the corresponding beam
    def draw(self):
        if self.direction == "Up":
            self.shapes.append(m_cnv.create_line(self.x_mid, self.y_min, self.x_mid, self.y_max, arrow="first"))
        elif self.direction == "Down":
            self.shapes.append(m_cnv.create_line(self.x_mid, self.y_min, self.x_mid, self.y_max, arrow="last"))
        elif self.direction == "Left":
            self.shapes.append(m_cnv.create_line(self.x_min, self.y_mid, self.x_max, self.y_mid, arrow="first"))
        elif self.direction == "Right":
            self.shapes.append(m_cnv.create_line(self.x_min, self.y_mid, self.x_max, self.y_mid, arrow="last"))
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
        self.point_index = ps.point_index
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
        self.ps.beam.objects["Pins"].pop()  # Removes the pin support
        m_cnv.create_oval(self.circle_box1)
        m_cnv.create_oval(self.circle_box2)
        self.ps.beam.objects["Rollers"].append(self)


class Moment:
    def __init__(self, x_min, y_min, x_max, y_max, rotation=None, side=["Top", "Bottom", "Left", "Right"], old_object=None):
        self.old_object = old_object
        self.shapes = []
        x_mid, y_mid = (x_min + x_max)/2, (y_min + y_max)/2
        self.side = side
        self.rotation = rotation
        print(side)
        self.closest_point, self.beam = find_closest_point((x_mid, y_mid), side)
        if self.closest_point in self.beam.points["Bottom"]:
            self.side = "Bottom"
            if rotation == None:
                self.rotation = "Clockwise"
        if self.closest_point in self.beam.points["Top"]:
            self.side = "Top"
            if rotation == None:
                self.rotation = "Counterclockwise"
        if self.closest_point in self.beam.points["Left"]:
            self.side = "Left"
            if rotation == None:
                self.rotation = "Counterclockwise"
        if self.closest_point in self.beam.points["Right"]:
            self.side = "Right"
            if rotation == None:
                self.rotation = "Clockwise" 
        self.radius = self.beam.length * 0.075
        self.point_index = self.beam.points[self.side].index(self.closest_point)
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
            print(self.rotation)

    def __str__(self):
        return "Moment"

    def draw(self):
        """
        :return: Draws a moment arrow
        """
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
                theta = 15 + t / 10
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
        self.beam.objects["Moments"].append(self)


class Load:
    def __init__(self, x_min, y_min, x_max, y_max, direction, old_object=None):
        self.old_object = old_object
        self.shapes = []
        y_mid = (y_min + y_max)/2
        self.direction = direction
        self.leftmost_point, self.beam = find_closest_point((x_min, y_mid), ["Bottom", "Top"])
        self.rightmost_point, self.beam = find_closest_point((x_max, y_mid), ["Bottom", "Top"])
        self.closest_point = self.rightmost_point
        self.x_min = self.leftmost_point[0]
        self.x_max = self.rightmost_point[0]
        self.length = self.x_max - self.x_min
        self.height = self.beam.length/6
        if self.closest_point in self.beam.points["Bottom"]:
            self.y_min = self.closest_point[1]
            self.y_max = self.y_min + self.height
            self.side = 'Bottom'
        elif self.closest_point in self.beam.points["Top"]:
            self.y_max = self.closest_point[1]
            self.y_min = self.y_max - self.height
            self.side = 'Top'
        self.no_arrows = self.beam.points[self.side].index(self.rightmost_point) - self.beam.points[self.side].index(self.leftmost_point) + 1
        self.sep = self.length / (self.no_arrows - 1)
        self.point_index = (self.beam.points[self.side].index(self.leftmost_point), self.beam.points[self.side].index(self.rightmost_point))

    def __str__(self):
        return "Load"

    def draw(self):
        """
        :return: Draws the Load
        """
        if self.side == "Top":
            py1 = self.leftmost_point[1]
            py2 = py1 - self.height
        elif self.side == "Bottom":
            py1 = self.leftmost_point[1]
            py2 = py1 + self.height
        if self.direction == "Down":
            for i in range(self.no_arrows):
                px = self.leftmost_point[0] + i * self.sep
                self.shapes.append(m_cnv.create_line(px, py1, px, py2, arrow="first")) # Kan krympa med first/last som variabel
        elif self.direction == "Up":
            for i in range(self.no_arrows):
                px = self.leftmost_point[0] + i * self.sep
                self.shapes.append(m_cnv.create_line(px, py2, px, py1, arrow="last"))

        self.shapes.append(m_cnv.create_line(self.leftmost_point[0], self.leftmost_point[1], 
                                            self.rightmost_point[0], self.rightmost_point[1]))
        self.shapes.append(m_cnv.create_line(self.leftmost_point[0], py2, self.rightmost_point[0], py2))
        self.beam.objects["Loads"].append(self)


class Surface:
    """
    Representation of a surface
    """
    def __init__(self, x_min, y_min, x_max, y_max):
        self.magnitude = None
        self.x_min = x_min
        self.y_min = y_min
        self.x_mid = (x_min + x_max)/2
        self.y_mid = (y_min + y_max)/2
        self.x_max = x_max
        self.y_max = y_max
        self.closest_item, self.side, self.closest_point = find_closest_object((self.x_mid, self.y_mid))
        if self.side in ["Bottom", "Top"]:
            self.x_mid = self.closest_point[0]
            self.width = self.closest_item.surface_width
            self.height = 6
            if self.side == "Bottom":
                self.y_min = self.closest_point[1]
                self.y_max = self.y_min + self.height
            elif self.side == "Top":
                self.y_max = self.closest_point[1]
                self.y_min = self.y_max - self.height
            self.no_lines = int(self.width/5) 
        elif self.side in ["Left", "Right"]:
            self.y_mid = self.closest_point[1]
            self.height = self.closest_item.surface_height 
            self.width = 6
            if self.side == "Left":
                self.x_max = self.closest_point[0]
                self.x_min = self.x_max - self.width
            elif self.side == "Right":
                self.x_min = self.closest_point[0]
                self.x_max = self.x_min + self.width
            self.no_lines = int(self.height/5)
            if isinstance(self.closest_item, Beam):
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


"""
The classes Rectangle, Box, Circle, Pipe, H-shape and T-shape are used for calculating the moment of inertia for the 
respective cross section. In all cases the x-axis points to the right (while looking straight at the cross section) 
and the y-axis points upwards.
"""
class Rectangle:
    def __init__(self, width, height):
        self.inertia_x = width * (height**3)/12
        self.inertia_y = height * (width**3)/12


class Box:
    def __init__(self, length):
        self.length = length
        self.inertia = (length**4)/12


class Circle:
    def __init__(self, diameter):
        self.inertia = m.pi*(diameter**4)/64


class Pipe:
    def __init__(self, diameter, thickness):
        d_i = diameter - 2*thickness
        self.inertia = m.pi*(diameter**4 - d_i**4)/64


class Hshape:  # Symmetrical
    def __init__(self, width, height, i_height, thickness):
        self.inertia_x = (thickness*i_height**3)/12 + (height**3 - i_height**3)*width/12
        self.inertia_y = (i_height * thickness**3)/12 + (width**3)*(height - i_height)/12


class Tshape:
    def __init__(self, width, height, thickness_1, thickness_2):
        area = width * thickness_1 + height * thickness_2
        y_c = ((height + thickness_1/2)*thickness_1*width + width*(height**2)/2)/area
        x_c = width/2
        self.inertia_y = height*(thickness_2**3)/12 + thickness_1*(width**3)/12
        self.inertia_x = thickness_2*height*(y_c - height/2)**2 + thickness_2*(height**3)/12 + \
                         thickness_1*width*(height + thickness_1/2 - y_c)**2 + width*(thickness_1**3)/12


# Code for trusses
"""
def find_closest_node(coord):
    ""
    Finds the closest node to the input coordinates
    :param coord: coordinates for the endpoint of a truss_beam
    :return: the closest node to the endpoint
    ""
    shortest_distance = m.inf
    shortest_distance_coordinates = (m.inf, m.inf)
    for node in node_list:
        distance = compute_distance(coord, node.center)
        if distance < shortest_distance:
            shortest_distance = distance
            shortest_distance_coordinates = node.center
            closest_node = node

    return shortest_distance_coordinates, closest_node


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
    :return objects: a pandas dataframe representation of the .csv file from Detector.py
    """
    #try:
    #    df = pd.read_csv(r'C:\Users\admin\Desktop\Detection_Results.csv')
    #except:
    #    df = pd.read_csv(r'C:\Users\tobia\Desktop\resultatHebbeBatch16\Detection_Results.csv')
        # df = pd.read_csv(r'C:\Users\tobia\Desktop\Detection_Results_test.csv')
    df = pd.read_csv(os.path.join(os.getcwd(), "TrainYourOwnYOLO/Data/Source_Images/Test_Image_Detection_Results/Detection_Results.csv"))
    
    df1 = df[["xmin", "ymin", "xmax", "ymax", "label", "confidence", "x_size", "y_size"]]
    df1 = delete_overlapping_objects(df1)
    return (df1)


def delete_overlapping_objects(objects): # Sannolikheter, Momentpilar åt olika håll -> välj den som har rätt typ av balkpunkt närmast, grej för att ändra position om krock efter ändringar
    """
    Function for deleting overlapping objects, if Detector.py detects two items whose bounding boxes overlap "too much" one of the objects is deleted
    :param objects: Pandas dataframe representation of the .csv file from Detector.py
    :return: Removes overlapping objects
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
                # If two objects of the same type are detected and overlap in bothe x and y direction, the one with the highest probability is kept
                if type1 == type2:
                    if obj1[5] < obj2[5]:
                        objects = objects.drop(index1, axis=0)
                        break
                # Code below is for the beams in a truss
                # elif type1 == "BeamLine":
                #    objects = objects.drop(index1, axis=0)
                # If a force is detected inside the boundaries of a load, the force is removed.
                elif type1 in ["force_up", "force_down", "force_left", "force_right"] and type2 in ["load_up", "load_down"]:
                    objects = objects.drop(index1, axis=0)
                    break
                # If a arrow down and a arrow up overlaps the one with the highest confidence is kept
                elif type1 in ["force_up", "force_down"] and type2 in ["force_up", "force_down"]:
                    if obj1[5] < obj2[5]:
                        objects = objects.drop(index1, axis=0)
                        break
                # If a arrow left and a arrow right overlaps the one with the highest confidence is kept
                elif type1 in ["force_left", "force_right"] and type2 in ["force_left", "force_right"]:
                    if obj1[5] < obj2[5]:
                        objects = objects.drop(index1, axis=0)
                        break
                # Code for removing nodes if they are overlapping with a roller support (if a wheel is detected as a node)
                # elif type1 == "Node" and type2 == "roller_support":
                    # objects = objects.drop(index1, axis=0)
                # If a support or roller support overlaps the one with the highest confidence is kept
                elif type1 in ["support", "roller_support"] and type2 in ["support", "roller_support"]:
                    if obj1[5] < obj2[5]:
                        objects = objects.drop(index1, axis=0)
                        break
                # If moments overlap the one with the highest confidence is kept
                elif type1 in ["counterclockwise_right", "counterclockwise_top", "counterclockwise_bottom", "counterclockwise_left", 
                                "clockwise_right", "clockwise_left", "clockwise_top", "clockwise_bottom", "clockwise", "counterclockwise", 
                                "arrow_torque"] and type2 in ["counterclockwise_right", "counterclockwise_top", "counterclockwise_bottom", 
                                "counterclockwise_left", "clockwise_right", "clockwise_left", "clockwise_top", "clockwise_bottom", 
                                "clockwise", "counterclockwise", "arrow_torque"]:
                    if obj1[5] < obj2[5]:
                        objects = objects.drop(index1, axis=0)
                        break
                # If a beam is detected in in a load, the beam is removed
                elif type1 == "beam_90" and type2 in ["load_up", "load_down"]:
                    objects = objects.drop(index1, axis=0)
                    break
                # If a load up and load down overlap the one with the highest confidence is kept
                elif type1 in ["load_up", "load_down"] and type2 in ["load_up", "load_down"]:
                    if obj1[5] < obj2[5]:
                        objects = objects.drop(index1, axis=0)
                        break
    return objects


def draw_all_objects(): #lägg in vanliga clockwise/counterwise
    """
    Draws all the detected objects by detector.py
    :return:
    """
    objects = get_objects()
    for index, row in objects.iterrows():
        # Row 4 in objects is the numerical version of the label
        obj_type = labels[int(row[4])]
        if obj_type in ['force_up', 'force_down', 'force_left', 'force_right', 'arrow_horizontal']: # ändra alla ' till " eller tvärt om?
            global number_of_forces
            number_of_forces += 1
        elif obj_type in ["clockwise_right", "clockwise_top", "clockwise_left", "clockwise_bottom", 
                          "counterclockwise_right", "counterclockwise_top", "counterclockwise_left",
                          "counterclockwise_bottom", "clockwise", "counterclockwise", "arrow_torque",
                          "torque_left_right", "torque_top_bottom"]:
            global number_of_moments
            number_of_moments += 1
        elif obj_type in ["load_up", "load_down"]:
            global number_of_loads
            number_of_loads += 1
        elif obj_type in ["beam", "beam_90"]:
            global number_of_beams
            number_of_beams += 1
    """
    Loop for scaling the beams to fit in a imgage of size 800x800 and drawing them. The beams are handled in their own loop since 
    the other objects draw() functions require that at least one beam exists.
    """
    for index, row in objects.iterrows():
        m_x = interp1d([0, max(row[6], row[7])], [0, 800])
        m_y = interp1d([0, max(row[6], row[7])], [0, 800])
        obj_type = labels[int(row[4])]
        x_min, y_min, x_max, y_max = float(m_x(row[0])), float(m_y(row[1])), float(m_x(row[2])), float(m_y(row[3]))
        if obj_type == "beam":
            beam = Beam(x_min, y_min, x_max, y_max, "0")
            beam.draw()
        elif obj_type == "beam_90":
            beam = Beam(x_min, y_min, x_max, y_max, "90")
            beam.draw()
    # Checking if any beam was identified. If not, the program can't run.
    if not beam_list:
        sys.exit("Error: No beam identified")
    # Loop for scaling all objects fit in a 800x800 image and drawing them
    for index, row in objects.iterrows():
        m_x = interp1d([0, max(row[6], row[7])], [0, 800])
        m_y = interp1d([0, max(row[6], row[7])], [0, 800])
        obj_type = labels[int(row[4])]
        x_min, y_min, x_max, y_max = float(m_x(row[0])), float(m_y(row[1])), float(m_x(row[2])), float(m_y(row[3]))
        if obj_type == "force_down":
            force = Force(x_min, y_min, x_max, y_max, "Down")
            force.draw()

        elif obj_type == "force_up":
            force = Force(x_min, y_min, x_max, y_max, "Up")
            force.draw()

        elif obj_type == "force_left":
            force = Force(x_min, y_min, x_max, y_max, "Left")
            force.draw()

        elif obj_type == "force_right":
            force = Force(x_min, y_min, x_max, y_max, "Right")
            force.draw()

        elif obj_type == "arrow_horizontal":
            force = Force(x_min, y_min, x_max, y_max, "Horizontal")
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

        elif obj_type == "torque_top_bottom":
            moment = Moment(x_min, y_min, x_max, y_max, side=["Top", "Bottom"])
            moment.draw()

        elif obj_type == "torque_left_right":
            moment = Moment(x_min, y_min, x_max, y_max, side=["Left", "Right"])
            moment.draw()

        elif obj_type == "arrow_torque":
            moment = Moment(x_min, y_min, x_max, y_max)
            moment.draw()

        elif obj_type == "clockwise":
            moment = Moment(x_min, y_min, x_max, y_max, "Clockwise")
            moment.draw()

        elif obj_type == "counterclockwise":
            moment = Moment(x_min, y_min, x_max, y_max, "Counterclockwise")
            moment.draw()

        elif obj_type == "clockwise_bottom":
            moment = Moment(x_min, y_min, x_max, y_max, "Clockwise", ["Bottom"])
            moment.draw()
        
        elif obj_type == "clockwise_top":
            moment = Moment(x_min, y_min, x_max, y_max, "Clockwise", ["Top"])
            moment.draw()

        elif obj_type == "clockwise_left":
            moment = Moment(x_min, y_min, x_max, y_max, "Clockwise", ["Left"])
            moment.draw()

        elif obj_type == "clockwise_right":
            moment = Moment(x_min, y_min, x_max, y_max, "Clockwise", ["Right"])
            moment.draw()

        elif obj_type == "counterclockwise_bottom":
            moment = Moment(x_min, y_min, x_max, y_max, "Counterclockwise", ["Bottom"])
            moment.draw()

        elif obj_type == "counterclockwise_top":
            moment = Moment(x_min, y_min, x_max, y_max, "Counterclockwise", ["Top"])
            moment.draw()

        elif obj_type == "counterclockwise_left":
            moment = Moment(x_min, y_min, x_max, y_max, "Counterclockwise", ["Left"])
            moment.draw()

        elif obj_type == "counterclockwise_right":
            moment = Moment(x_min, y_min, x_max, y_max, "Counterclockwise", ["Right"])
            moment.draw()
    """
    Loop for scaling grounds/surfaces to fit in a 800x800 image and drawing them,
    also labels the beams, forces, moments and loads.
    """
    for index, row in objects.iterrows():
        m_x = interp1d([0, max(row[6], row[7])], [0, 800])
        m_y = interp1d([0, max(row[6], row[7])], [0, 800]) # Om vanligt koordinatsystem, byt 3 och 1 nedan och 800, 0 t.v.
        obj_type = labels[int(row[4])]
        x_min, y_min, x_max, y_max = float(m_x(row[0])), float(m_y(row[1])), float(m_x(row[2])), float(m_y(row[3]))
        
        if obj_type == "ground":
            surface = Surface(x_min, y_min, x_max, y_max)
            surface.draw()
    for beam in beam_list:
        create_label(beam)
        for obj_type in ["Forces", "Moments", "Loads"]:
            for obj in beam.objects[obj_type]:
                create_label(obj, obj.old_object)


def fe_input():
    """
    Function for converting the mathematical model to a Python dictionary and delivering it to the calculation script
    :return output: The dictionary containing the necessary information for the calculations
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
                        beam_objects.append((str(obj), 12, obj.magnitude)) 
                elif beam.orientation == "90":
                    if obj.side in ["Left", "Right"]:
                        beam_objects.append((str(obj), obj.point_index, obj.magnitude)) 
                    elif obj.side == "Top":
                        beam_objects.append((str(obj), 0, obj.magnitude))
                    elif obj.side == "Bottom":
                        beam_objects.append((str(obj), 12, obj.magnitude))
        output['Beam' + str(index)] = (beam.fe_length, beam.orientation, beam.inertia*beam.youngs_modulus, beam_objects)
    print(output)
    return output


def delete_object(obj):
    """
    Deletes an object
    :param obj: The object to be deleted
    :return:
    """
    obj.beam.objects[str(obj) + "s"].remove(obj)
    for shape in obj.shapes:
        m_cnv.delete(shape)


def set_magnitude(obj, entry):
    """
    Function for changing direction and magnitude of an object. If a negative value is given, a new object with the
    opposite direction is drawn.
    :param obj: A object to change the magnitude of, obj must be an instance of Moment, Force or Load
    :param entry: The value to change the magnitude to, if entry.
    :return obj: A new object of the same type as the parameter obj but with the new magnitude. If the direction is
                 changed, obj is redrawn with the new direction
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
                new_obj = Moment(obj.x_min, obj.y_min, obj.x_max, obj.y_max, 'Counterclockwise', [obj.side], obj)
                new_obj.magnitude = entry*(-1)
            elif obj.rotation == 'Counterclockwise':
                new_obj = Moment(obj.x_min, obj.y_min, obj.x_max, obj.y_max, 'Clockwise', [obj.side], obj)
                new_obj.magnitude = entry
        elif isinstance(obj, Load):
            if obj.direction == 'Up':
                new_obj = Load(obj.x_min, obj.y_min, obj.x_max, obj.y_max, 'Down', obj)
                new_obj.magnitude = entry
            if obj.direction == 'Down':
                new_obj = Load(obj.x_min, obj.y_min, obj.x_max, obj.y_max, 'Up', obj)
                new_obj.magnitude = entry*(-1)
        new_obj.draw()
        new_obj.label = obj.label
        delete_object(obj)
        obj = new_obj
    return obj


def set_length(beam, length):
    """
    Helper function for changing the .length of beam
    :param beam: the beam to change the length of
    :param length: the new length
    :return: changes the fe_length to length
    """
    if length <= 0:
        print("Beam length must be positive")
    else:
        beam.fe_length = length


def create_entries():
    """
    Adds entries for changing the magnitude and direction of moments, loads, forces, cross-sections and Young's modulus
    :return: entries, labels, and spinboxes for units.
    """
    force_entries = []
    moment_entries = []
    load_entries = []
    beam_entries = []
    objects = beam_list[0].objects

    def update_image():
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
            Converts the prefixes (km, kN, MNm and N/m) to powers of ten (1000, 1000000, 1).
            :param unit: A prefix followed by the unit corresponding to loads, moments and forces (N, Nm, N/m)
            :return:
            """
            split = unit.split("N")[0]
            output = 1
            if split == "km":
                output = 1000
            elif split == "k":
                output = 1000
            elif split == "M":
                output = 1000000
            elif split == "G":
                output = 1000000000
            return output

        for e in force_entries:
            try:
                magnitude = float(e[0].get())
            except:
                print("Input must be a number")
                magnitude = 1.0
            scale_factor = convert_unit(str(e[2].get()))
            scaled_magnitude = magnitude * scale_factor
            force_label = e[1].cget("text")
            for beam in beam_list:
                for force in beam.objects["Forces"]:
                    if force.label == force_label:
                        scaled_force = force
            set_magnitude(scaled_force, scaled_magnitude)
            e[0].delete(0, END)
            e[0].insert(0, str(abs(magnitude)))

        for e in moment_entries:
            try:
                magnitude = float(e[0].get())
            except:
                print("Input must be a number")
                magnitude = 1.0
            scale_factor = convert_unit(str(e[2].get()))
            scaled_magnitude = magnitude * scale_factor

            moment_label = e[1].cget("text")
            for beam in beam_list:
                for moment in beam.objects["Moments"]:
                    if moment.label == moment_label:
                        scaled_moment = moment
            set_magnitude(scaled_moment, scaled_magnitude)
            e[0].delete(0, END)
            e[0].insert(0, str(abs(magnitude)))

        for e in load_entries:
            try:
                magnitude = float(e[0].get())
            except:
                print("Input must be a number")
                magnitude = 1.0
            scale_factor = convert_unit(str(e[2].get()))
            scaled_magnitude = magnitude * scale_factor

            load_label = e[1].cget("text")
            for beam in beam_list:
                for load in beam.objects["Loads"]:
                    if load.label == load_label:
                        scaled_load = load
            set_magnitude(scaled_load, scaled_magnitude)
            e[0].delete(0, END)
            e[0].insert(0, str(abs(magnitude)))

        for e in beam_entries:
            try:
                length = float(e[0].get())
            except:
                print("Input must be a number")
                length = 1.0
            scale_factor = convert_unit(str(e[2].get()))
            scaled_length = length * scale_factor

            beam_label = e[1].cget("text").split("\n")
            beam_label = beam_label[0] + " " + beam_label[1]
            for beam in beam_list:
                print(beam.label)
                if beam.label == beam_label:
                    scaled_beam = beam
            set_length(scaled_beam, scaled_length)
            e[0].delete(0, END)
            e[0].insert(0, str(length))

    def shear_force_diagram():
        update_image()
        FEM.FEM_main(fe_input(), 0)
    
    def normal_force_diagram():
        update_image()
        FEM.FEM_main(fe_input(), 1)

    def moment_diagram():
        update_image()
        FEM.FEM_main(fe_input(), 2)
    
    def deflection():
        update_image()
        FEM.FEM_main(fe_input(), 3)

    # Frame to hold the entries for loads
    load_frame = Frame(object_frame, bd=2, padx=2, pady=2, relief=RAISED)
    load_frame.grid(row=0)
    # loop for creating the entries for all the loads
    for load in objects["Loads"]:
        row = objects["Loads"].index(load)

        label = Label(load_frame, text=load.label, width=5)
        label.grid(row=row, column=0)

        entry = Entry(load_frame, width=10)
        entry.grid(row=row, column=1)
        entry.insert(0, "1.0")

        unit = Spinbox(load_frame, values=("N/m", "kN/m", "MN/m", "GN/m"), width=5)
        unit.grid(row=row, column=2)

        load_entries.append((entry, label, unit))
    # Frame to hold the entries for forces
    force_frame = Frame(object_frame, bd=2, padx=2, pady=2, relief=RAISED)
    force_frame.grid(row=1)
    # loop for creating the entries for all the forces
    for force in objects["Forces"]:
        row = objects["Forces"].index(force)

        label = Label(force_frame, text=force.label, width=5)
        label.grid(row=row, column=0)

        entry = Entry(force_frame, width=10)
        entry.grid(row=row, column=1)
        entry.insert(0, "1.0")

        unit = Spinbox(force_frame, values=("N", "kN", "MN", "GN"), width=5)
        unit.grid(row=row, column=2)

        force_entries.append((entry, label, unit))
    # Frame to hold the entries for moments
    moment_frame = Frame(object_frame, bd=2, padx=2, pady=2, relief=RAISED)
    moment_frame.grid(row=2)
    # loop for creating the entries for all the moments
    for moment in objects["Moments"]:
        row = objects["Moments"].index(moment)

        label = Label(moment_frame, text=moment.label, width=5)
        label.grid(row=row, column=0)

        entry = Entry(moment_frame, width=10)
        entry.grid(row=row, column=1)
        entry.insert(0, "1.0")

        unit = Spinbox(moment_frame, values=("Nm", "kNm", "MNm", "GNm"), width=5)
        unit.grid(row=row, column=2)

        moment_entries.append((entry, label, unit))

    # Frame to hold the entries for beams
    beam_frame = Frame(object_frame, bd=2, padx=2, pady=2, relief=RAISED)
    beam_frame.grid(row=3)
    # loop for creating the entries for all the beams, currently only one beam per image is implemented 100%
    for beam in beam_list:
        row = beam_list.index(beam)
        label_list = beam.label.split(" ")
        print(label_list)
        text = label_list[0] + "\n" + label_list[1]
        label = Label(beam_frame, text=text, width=5)
        label.grid(row=row, column=0)

        entry = Entry(beam_frame, width=10)
        entry.grid(row=row, column=1)
        entry.insert(0, "1.0")

        unit = Spinbox(beam_frame, values=("m", "km"), width=5)
        unit.grid(row=row, column=2)

        beam_entries.append((entry, label, unit))

    # Create a new frame to hold the options for the cross section
    cross_section_frame = Frame(object_frame, bd=2, padx=2, pady=2, relief=RAISED)
    cross_section_frame.grid(row=4)
    # Cross section label
    cross_section_label = Label(cross_section_frame, text="Cross section")
    cross_section_label.grid(row=0, column=0)
    # The spinbox for selecting different types of cross section, selecting value lets you simply enter a value for I
    cross_section = Spinbox(cross_section_frame,
                            values=("Rectangle", "Box", "Circle", "Pipe", "H-shape", "T-shape", "Value"), width=10)
    cross_section.grid(row=0, column=1)

    cross_section_button = Button(cross_section_frame, text="Customize",
                                  command=lambda: change_parameters())
    cross_section_button.grid(row=0, column=2)

    def change_parameters():
        """
        Function used to choose what moment of inertia and Young's modulus to be used for the FE-calculations
        :return inertia, youngs_modulus:
        """
        # Removes the change parameters field from the menu if there already is one.
        if len(e_cnv.grid_slaves()) > 2:
            field_to_delete = e_cnv.grid_slaves()[0]
            field_to_delete.grid_remove()
        # The frame that holds all the different fields
        change_parameters_frame = Frame(e_cnv, bd=2, padx=2, pady=2, relief=RAISED)
        change_parameters_frame.grid(row=3, column=0)
        # Gets the text in the cross-section spinbox
        cross_section_type = cross_section.get()
        # Used to keep track of indexing for the different fields in the menu
        parameters = ()
        # Entry and Spinbox width
        widget_width = 5
        if cross_section_type == "Rectangle":
            height, width = 1, 1  # in dm
            parameters = ("Rectangle", width, height)
            # 1409-1424 creates the menu fields for a rectangular cross section
            height_label = Label(change_parameters_frame, text="Height")
            width_label = Label(change_parameters_frame, text="Width")
            height_label.grid(row=1, column=0)
            width_label.grid(row=0, column=0)

            height_entry = Entry(change_parameters_frame, width=2*widget_width)
            width_entry = Entry(change_parameters_frame, width=2*widget_width)
            height_entry.grid(row=1, column=1)
            width_entry.grid(row=0, column=1)
            height_entry.insert(END, height)
            width_entry.insert(END, width)

            height_unit = Spinbox(change_parameters_frame, values=("mm", "cm", "dm", "m"), width=widget_width)
            width_unit = Spinbox(change_parameters_frame, values=("mm", "cm", "dm", "m"), width=widget_width)
            height_unit.grid(row=1, column=2)
            width_unit.grid(row=0, column=2)
        elif cross_section_type == "Box":
            side = 1
            parameters = ("Box", side)
            # 1429-1437 creates the menu fields for a quadratic cross section
            side_label = Label(change_parameters_frame, text="Side")
            side_label.grid(row=0, column=0)

            side_entry = Entry(change_parameters_frame, width=2*widget_width)
            side_entry.grid(row=0, column=1)
            side_entry.insert(END, side)

            side_unit = Spinbox(change_parameters_frame, values=("mm", "cm", "dm", "m"), width=widget_width)
            side_unit.grid(row=0, column=2)
        elif cross_section_type == "Circle":
            diameter = 1
            parameters = ("Circle", diameter)

            diameter_label = Label(change_parameters_frame, text="Diameter")
            diameter_label.grid(row=0, column=0)

            diameter_entry = Entry(change_parameters_frame, width=2*widget_width)
            diameter_entry.grid(row=0, column=1)
            diameter_entry.insert(END, diameter)

            diameter_unit = Spinbox(change_parameters_frame, values=("mm", "cm", "dm", "m"), width=widget_width)
            diameter_unit.grid(row=0, column=2)
        elif cross_section_type == "Pipe":
            diameter = 1
            thickness = 1
            parameters = ("Pipe", diameter, thickness)

            diameter_label = Label(change_parameters_frame, text="Diameter")
            diameter_label.grid(row=0, column=0)

            diameter_entry = Entry(change_parameters_frame, width=2*widget_width)
            diameter_entry.grid(row=0, column=1)
            diameter_entry.insert(END, diameter)

            diameter_unit = Spinbox(change_parameters_frame, values=("mm", "cm", "dm", "m"), width=widget_width)
            diameter_unit.grid(row=0, column=2)

            thickness_label = Label(change_parameters_frame, text="Thickness")
            thickness_label.grid(row=1, column=0)

            thickness_entry = Entry(change_parameters_frame, width=2*widget_width)
            thickness_entry.grid(row=1, column=1)
            thickness_entry.insert(END, thickness)

            thickness_unit = Spinbox(change_parameters_frame, values=("mm", "cm", "dm", "m"), width=widget_width)
            thickness_unit.grid(row=1, column=2)
        elif cross_section_type == "H-shape":
            # Need to inform them what i_height is
            # Parameters are width, height, i_height and thickness
            width, height, i_height, thickness = 1, 1, 1, 1
            parameters = ("H-shape", width, height, i_height, thickness)

            width_label = Label(change_parameters_frame, text="Width")
            width_label.grid(row=0, column=0)

            width_entry = Entry(change_parameters_frame, width=2*widget_width)
            width_entry.grid(row=0, column=1)
            width_entry.insert(END, width)

            width_unit = Spinbox(change_parameters_frame, values=("mm", "cm", "dm", "m"), width=widget_width)
            width_unit.grid(row=0, column=2)

            height_label = Label(change_parameters_frame, text="Height")
            height_label.grid(row=1, column=0)

            height_entry = Entry(change_parameters_frame, width=2*widget_width)
            height_entry.grid(row=1, column=1)
            height_entry.insert(END, height)

            height_unit = Spinbox(change_parameters_frame, values=("mm", "cm", "dm", "m"), width=widget_width)
            height_unit.grid(row=1, column=2)

            i_height_label = Label(change_parameters_frame, text="Middle height")
            i_height_label.grid(row=2, column=0)

            i_height_entry = Entry(change_parameters_frame, width=2*widget_width)
            i_height_entry.grid(row=2, column=1)
            i_height_entry.insert(END, i_height)

            i_height_unit = Spinbox(change_parameters_frame, values=("mm", "cm", "dm", "m"), width=widget_width)
            i_height_unit.grid(row=2, column=2)

            thickness_label = Label(change_parameters_frame, text="Thickness")
            thickness_label.grid(row=3, column=0)

            thickness_entry = Entry(change_parameters_frame, width=2*widget_width)
            thickness_entry.grid(row=3, column=1)
            thickness_entry.insert(END, thickness)

            thickness_unit = Spinbox(change_parameters_frame, values=("mm", "cm", "dm", "m"), width=widget_width)
            thickness_unit.grid(row=3, column=2)
        elif cross_section_type == "T-shape":
            width, height, top_thickness, vertical_thickness = 1, 1, 1, 1
            parameters = ("T-shape", width, height, top_thickness, vertical_thickness)

            width_label = Label(change_parameters_frame, text="Width")
            width_label.grid(row=0, column=0)

            width_entry = Entry(change_parameters_frame, width=2*widget_width)
            width_entry.grid(row=0, column=1)
            width_entry.insert(END, width)

            width_unit = Spinbox(change_parameters_frame, values=("mm", "cm", "dm", "m"), width=widget_width)
            width_unit.grid(row=0, column=2)

            height_label = Label(change_parameters_frame, text="Height")
            height_label.grid(row=1, column=0)

            height_entry = Entry(change_parameters_frame, width=2*widget_width)
            height_entry.grid(row=1, column=1)
            height_entry.insert(END, height)

            height_unit = Spinbox(change_parameters_frame, values=("mm", "cm", "dm", "m"), width=widget_width)
            height_unit.grid(row=1, column=2)

            top_thickness_label = Label(change_parameters_frame, text="Top thickness")
            top_thickness_label.grid(row=2, column=0)

            top_thickness_entry = Entry(change_parameters_frame, width=2*widget_width)
            top_thickness_entry.grid(row=2, column=1)
            top_thickness_entry.insert(END, top_thickness)

            top_thickness_unit = Spinbox(change_parameters_frame, values=("mm", "cm", "dm", "m"), width=widget_width)
            top_thickness_unit.grid(row=2, column=2)

            vertical_thickness_label = Label(change_parameters_frame, text="Foot thickness")
            vertical_thickness_label.grid(row=3, column=0)

            vertical_thickness_entry = Entry(change_parameters_frame, width=2*widget_width)
            vertical_thickness_entry.grid(row=3, column=1)
            vertical_thickness_entry.insert(END, vertical_thickness)

            vertical_thickness_unit = Spinbox(change_parameters_frame, values=("mm", "cm", "dm", "m"), width=widget_width)
            vertical_thickness_unit.grid(row=3, column=2)
        elif cross_section_type == "Value":
            value = 1
            parameters = ("Value", value, "")
            explanation_label = Label(change_parameters_frame, text="If your desired cross section isn't implemented yet,\nyou can enter a value for I in the field below")
            explanation_label.grid(row=0, column=0, columnspan=3)

            value_label = Label(change_parameters_frame, text="Value of I")
            value_label.grid(row=1, column=0)

            value_entry = Entry(change_parameters_frame, width=2*widget_width)
            value_entry.grid(row=1, column=1)
            value_entry.insert(END, value)

            value_unit = Label(change_parameters_frame, text="kgm^2", width=widget_width)
            value_unit.grid(row=1, column=2)

        def change_parameters_command(parameters):
            """
            The function that changes the inertia and Young's modulus of the depicted beam
            :param parameters: A tuple where p[0] = the type of cross section, the rest of the info isn't used TODO: Better workaround
            :return: Changes beam.inertia and beam.youngs_modulus to user's desired values
            """
            def scale(unit):
                """
                Helper function for converting prefixes to numerical values
                :param unit: a prefix (mm, cm, dm, m)
                :return factor: the numerical representation of unit (0.001, 0.01, 0.1, 1)
                """
                factor = 1
                unit_split = unit.split("m")
                unit = unit_split[0]
                if unit == "" and len(unit_split) == 3:
                    factor = 0.001
                elif unit == "c":
                    factor = 0.01
                elif unit == "d":
                    factor = 0.1
                return factor

            if parameters[0] == "Rectangle":
                width = float(width_entry.get()) * scale(width_unit.get())
                height = float(height_entry.get()) * scale(height_unit.get())
                rectangle = Rectangle(width, height)
                inertia = rectangle.inertia_y
            elif parameters[0] == "Box":
                side = float(side_entry.get()) * scale(side_unit.get())
                box = Box(side)
                inertia = box.inertia
            elif parameters[0] == "Circle":
                diameter = float(diameter_entry.get()) * scale(diameter_unit.get())
                circle = Circle(diameter)
                inertia = circle.inertia
            elif parameters[0] == "Pipe":
                diameter = float(diameter_entry.get()) * scale(diameter_unit.get())
                thickness = float(thickness_entry.get()) * scale(thickness_unit.get())
                pipe = Pipe(diameter, thickness)
                inertia = pipe.inertia
            elif parameters[0] == "H-shape":
                width = float(width_entry.get()) * scale(width_unit.get())
                height = float(height_entry.get()) * scale(height_unit.get())
                i_height = float(i_height_entry.get()) * scale(i_height_unit.get())
                thickness = float(thickness_entry.get()) * scale(thickness_unit.get())
                h_shape = Hshape(width, height, i_height, thickness)
                inertia = h_shape.inertia_x
            elif parameters[0] == "T-shape":
                width = float(width_entry.get()) * scale(width_unit.get())
                height = float(height_entry.get()) * scale(height_unit.get())
                top_thickness = float(top_thickness_entry.get()) * scale(top_thickness_unit.get())
                foot_thickness = float(vertical_thickness_entry.get()) * scale(vertical_thickness_unit.get())
                t_shape = Tshape(width, height, top_thickness, foot_thickness) # TODO check if correct
                inertia = t_shape.inertia_x
            elif parameters[0] == "Value":
                inertia = float(value_entry.get())

            beam_list[0].inertia = inertia
            beam_list[0].youngs_modulus = get_elasticity()
            change_parameters_frame.grid_remove()

        def get_elasticity():
            """
            Helper function for getting and scaling the Young's modulus
            :return scaled_E: The value of E in SI-units
            """
            scale_factor = 1
            unit = elasticity_unit.get().split("P")[0]
            if unit == "k":
                scale_factor = 10**3
            elif unit == "M":
                scale_factor = 10**6
            elif unit == "G":
                scale_factor = 10**9
            unscaled_E = float(elasticity_entry.get())
            scaled_E = unscaled_E * scale_factor

            return scaled_E
        # Button that changes .inertia and .youngs_modulus
        change_button = Button(change_parameters_frame, text="Done", command=lambda: change_parameters_command(parameters))
        change_button.grid(row=len(parameters), column=2, sticky=E)
        # Elasticity modulos
        elasticity_label = Label(change_parameters_frame, text="Young's\nmodulus")
        elasticity_label.grid(row=len(parameters) - 1, column=0)

        elasticity_entry = Entry(change_parameters_frame, width=2*widget_width)
        elasticity_entry.grid(row=len(parameters) - 1, column=1)
        elasticity_entry.insert(END, 1)

        elasticity_unit = Spinbox(change_parameters_frame, values=("Pa", "kPa", "MPa", "GPa"), width=widget_width)
        elasticity_unit.grid(row=len(parameters) - 1, column=2)
    # Frame to hold save, calculate and quit-buttons
    menu_frame = Frame(e_cnv, bd=2, padx=2, pady=2, relief=RAISED)
    menu_frame.grid(row=4, rowspan=2)

    utility_frame = Frame(menu_frame, bd=2, padx=2, pady=2)
    utility_frame.grid(row=1)

    calculate_frame = Frame(menu_frame, bd=2, padx=2, pady=2)
    calculate_frame.grid(row=0)

    diagram_button_1 = Button(calculate_frame, text="Normal force\ndiagram", command=lambda: normal_force_diagram())
    diagram_button_1.grid(row=0, column=0)

    diagram_button_2 = Button(calculate_frame, text="Shear force\ndiagram", command=lambda: shear_force_diagram())
    diagram_button_2.grid(row=0, column=1)

    diagram_button_3 = Button(calculate_frame, text="Bending moment\ndiagram", command=lambda: moment_diagram())
    diagram_button_3.grid(row=0, column=2)

    deflection_button = Button(calculate_frame, text="Deflection", command=lambda: deflection(), height=2)
    deflection_button.grid(row=0, column=3)
    print(diagram_button_3.cget("height"))

    def save_image():  # behöver kanske inte vara metod i metod... Se till så inte gammal bild skrivs över?
        """
        Helper function for saving the image
        :return: A .png of the drawn image
        """
        path = fd.askdirectory()
        im = ImageGrab.grab(bbox=(0, 0, 1200, 1000))
        im.save(os.path.join(path, "bild.png"))

    save_button = Button(utility_frame, text="Save image", command=lambda: save_image())
    save_button.grid(row=0, column=0)

    def quit():
        """
        Helper function for closing the window
        :return: Destroys root
        """
        root.destroy()

    quit_button = Button(utility_frame, text='Quit', command=lambda: quit())
    quit_button.grid(row=0, column=1)

    update_button = Button(utility_frame, text="Update image", command=lambda: update_image())
    update_button.grid(row=0, column=2)

# Draw the image
draw_all_objects()
# Create the menu
create_entries()
# Used to loop tkinter
mainloop()
