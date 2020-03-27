from tkinter import *
import math as m
import numpy as np
import random as r
import pandas as pd
from scipy.interpolate import interp1d
from PIL import Image
import time
root = Tk()
m_cnv = Canvas(root, width=1000, height=1000)
m_cnv.pack()

beam_list = []
node_list = []
truss_beams = []
surface_points = {"Bottom": [], "Top": [], "Left": [], "Right": []} # To find the closest item for a surface. Each list: 
                                                                    # (the item, (starting coordinate), (ending coordinate)) 

labels = ["RollerSupport", "PinSupport", "Beam", "Node", "ArrowDown", "ArrowUp", "ArrowCounterClockwise",
                  "ArrowClockwise", "Beam45", "Beam135", "Surface", "LoadUp", "LoadRight", "LoadDown"]

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


def find_closest_object(coord, sides=["Bottom", "Top", "Left", "Right"]):
    shortest_distance = m.inf
    shortest_distance_coordinates = (m.inf, m.inf)
    print(surface_points)
    for side in sides:
        print(side)
        for item, point, corrected_point in surface_points[side]: # Point och changed_point rätt grejer?
            print(item)
            print(point)
            print(corrected_point)
            distance = compute_distance(coord, point)
            if distance < shortest_distance:
                shortest_distance = distance
                shortest_distance_coordinates = corrected_point
                closest_item = item
                closest_side = side
    print(closest_item)
    print(closest_side)
    print(shortest_distance_coordinates)
    return closest_item, closest_side, shortest_distance_coordinates # Returning wrong stuff?

# compute distance between two points
def compute_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


class Beam:
    def __init__(self, x_min, y_min, x_max, y_max):
        y_mid = (y_max + y_min)/2
        x_mid = (x_max + x_min)/2
        self.points = {"Bottom": [], "Top": [], "Left": [], "Right": []}
        self.objects = {"Forces": [], "Loads": [], "Pins": [], "Rollers": [], "Moments": [], "Fixed": []}
        if x_max - x_min > y_max - y_min:
            self.length = x_max - x_min
            self.height = 4
            self.y_max = y_mid + 2
            self.y_min = y_mid - 2
            self.x_max = x_max
            self.x_min = x_min
            self.y_mid = (self.y_max + self.y_min)/2
            point_distance = self.length/11
            for i in range(12):
                self.points["Bottom"].append((self.x_min + i * point_distance, self.y_max))
                self.points["Top"].append((self.x_min + i * point_distance, self.y_min))
            self.points["Left"].append((self.x_min, self.y_mid))
            self.points["Right"].append((self.x_max, self.y_mid))
            surface_points["Left"].append((self, (self.x_min, self.y_mid), (self.x_min, self.y_mid)))   # If the surface is connected to a beam the
            surface_points["Right"].append((self, (self.x_max, self.y_mid), (self.x_max, self.y_mid)))  # middle point were they connect won´t be changed
            self.surface_height = self.height*4

        else:
            self.length = y_max - y_min
            self.height = 4
            self.x_max = x_mid + 2
            self.x_min = x_mid - 2
            self.y_min = y_min
            self.y_max = y_max
            self.x_mid = (self.x_max + self.x_min)/2
            point_distance = self.length/11
            for i in range(12):
                self.points["Left"].append((self.x_min, self.y_min + i * point_distance))
                self.points["Right"].append((self.x_max, self.y_min + i * point_distance))
            self.points["Bottom"].append((self.x_mid, self.y_max))
            self.points["Top"].append((self.x_mid, self.y_min))
            surface_points["Bottom"].append((self, (self.x_mid, self.y_max), (self.x_mid, self.y_max))) # If the surface is connected to a beam the
            surface_points["Top"].append((self, (self.x_mid, self.y_min), (self.x_mid, self.y_min)))    # middle point were they connect won´t be changed
            self.surface_width = self.height*4

    def draw(self):
        m_cnv.create_rectangle(self.x_min, self.y_min, self.x_max, self.y_max, fill="")
        beam_list.append(self)


class Force:
    def __init__(self, x_min, y_min, x_max, y_max, direction):
        self.direction = direction
        x_mid = (x_max + x_min)/2
        y_mid = (y_max + y_min)/2
        if direction == "Up" or direction == "Down": # direction i raden under
            (closest_x1, closest_y1), beam1 = find_closest_point((x_mid, y_min), ["Bottom", "Top"])
            (closest_x2, closest_y2), beam2 = find_closest_point((x_mid, y_max), ["Bottom", "Top"])
            dist1 = compute_distance((closest_x1, closest_y1), (x_mid, y_min))
            dist2 = compute_distance((closest_x2, closest_y2), (x_mid, y_max))
            if dist1 > dist2:
                self.x_mid = closest_x2
                self.y_max = closest_y2
                self.beam = beam2
                self.y_min = self.y_max - self.beam.length * 0.2
                self.closest_point = (closest_x2, closest_y2)
            else:
                self.x_mid = closest_x1
                self.y_min = closest_y1
                self.beam = beam1
                self.y_max = self.y_min + self.beam.length * 0.2
                self.closest_point = (closest_x1, closest_y1)
        elif direction == "Left" or direction == "Right":
            (closest_x1, closest_y1), beam1 = find_closest_point((x_min, y_mid), ["Left", "Right"])
            (closest_x2, closest_y2), beam2 = find_closest_point((x_max, y_mid), ["Left", "Right"])
            dist1 = compute_distance((closest_x1, closest_y1), (x_min, y_mid))
            dist2 = compute_distance((closest_x2, closest_y2), (x_max, y_mid)) 
            if dist1 > dist2:
                self.x_max = closest_x2
                self.y_mid = closest_y2
                self.beam = beam2
                self.x_min = self.x_max - self.beam.length * 0.2
                self.closest_point = (closest_x2, closest_y2)
            else:
                self.x_min = closest_x1
                self.y_mid = closest_y1
                self.beam = beam1
                self.x_max = self.x_min + self.beam.length * 0.2
                self.closest_point = (closest_x1, closest_y1)
        
    def draw(self):
        if self.direction == "Up":
            m_cnv.create_line(self.x_mid, self.y_min, self.x_mid, self.y_max, arrow="first")
            self.beam.objects["Forces"].append((self.closest_point, "Up"))
        elif self.direction == "Down":
            m_cnv.create_line(self.x_mid, self.y_min, self.x_mid, self.y_max, arrow="last")
            self.beam.objects["Forces"].append((self.closest_point, "Down"))
        elif self.direction == "Left":
            m_cnv.create_line(self.x_min, self.y_mid, self.x_max, self.y_mid, arrow="first")
            self.beam.objects["Forces"].append((self.closest_point, "Left"))
        elif self.direction == "Right":
            m_cnv.create_line(self.x_min, self.y_mid, self.x_max, self.y_mid, arrow="last")
            self.beam.objects["Forces"].append((self.closest_point, "Right"))


class PinSupport:
    def __init__(self, x_min, y_min, x_max, y_max, size=0.15):
        x_mid = (x_max + x_min)/2
        y_mid = (y_max + y_min)/2
        self.points = {"Bottom": [(x_mid, y_max)], "Top": [x_mid, y_min], "Left": [x_min, y_mid], "Right": [x_max, y_mid]}
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
            self.corner1 = (self.x_mid, self.y_min)
            self.corner2 = (self.x_min, self.y_max)
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

    def draw(self):
        m_cnv.create_polygon(self.corner1, self.corner2, self.corner3, fill="", outline="Black")
        self.beam.objects["Pins"].append((self.corner1, self.orientation))


class RollerSupport:
    def __init__(self, x_min, y_min, x_max, y_max):
        x_mid = (x_min + x_max)/2
        y_mid = (y_min + y_max)/2
        pin_size = 0.0951
        self.ps = PinSupport(x_min, y_min, x_max, y_max, pin_size)
        surface_points[self.ps.orientation].pop()
        self.surface_width = 1.2 * self.ps.beam.length * pin_size
        self.surface_height = self.surface_width
        if self.ps.orientation == "Bottom":
            self.circle_box1 = (self.ps.x_min, self.ps.y_max + self.ps.beam.length * pin_size/2, self.ps.x_mid, self.ps.y_max)
            self.circle_box2 = (self.ps.x_mid, self.ps.y_max + self.ps.beam.length * pin_size/2, self.ps.x_max, self.ps.y_max)
            self.orientation = "Bottom"
            surface_points["Bottom"].append((self, (x_mid, y_max), (self.ps.x_mid, self.ps.y_max + self.ps.beam.length * pin_size/2)))

        elif self.ps.orientation == "Top":
            self.circle_box1 = (self.ps.x_min, self.ps.y_min - self.ps.beam.length * pin_size/2,
                                self.ps.x_mid, self.ps.y_min)
            self.circle_box2 = (self.ps.x_mid, self.ps.y_min - self.ps.beam.length * pin_size/2,
                                self.ps.x_max, self.ps.y_min)
            self.orientation = "Top"
            surface_points["Top"].append((self, (x_mid, y_min), (self.ps.x_mid, self.ps.y_min - self.ps.beam.length * pin_size/2)))
        elif self.ps.orientation == "Left":
            self.circle_box1 = (self.ps.x_min - self.ps.beam.length * pin_size/2, self.ps.y_min,
                                self.ps.x_min, self.ps.y_mid)
            self.circle_box2 = (self.ps.x_min - self.ps.beam.length * pin_size/2, self.ps.y_mid,
                                self.ps.x_min, self.ps.y_max)
            self.orientation = "Left"
            surface_points["Left"].append((self, (x_min, y_mid), (self.ps.x_min - self.ps.beam.length * pin_size/2, self.ps.y_mid)))
        elif self.ps.orientation == "Right":
            self.circle_box1 = (self.ps.x_max, self.ps.y_min,
                                self.ps.x_max + self.ps.beam.length * pin_size/2, self.ps.y_mid)
            self.circle_box2 = (self.ps.x_max, self.ps.y_mid,
                                self.ps.x_max + self.ps.beam.length * pin_size/2, self.ps.y_max)
            self.orientation = "Right"
            surface_points["Right"].append((self, (x_max, y_mid), (self.ps.x_max + self.ps.beam.length * pin_size/2, self.ps.y_mid)))

    def draw(self):
        self.ps.draw()
        self.ps.beam.objects["Pins"].pop() # Elegant way of removing the extra pin support added to the objects dictionary
        m_cnv.create_oval(self.circle_box1)
        m_cnv.create_oval(self.circle_box2)
        self.ps.beam.objects["Forces"].append((self.ps.closest_point, self.orientation))


class Moment:
    def __init__(self, x_min, y_min, x_max, y_max, rotation, rel_pos):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        x_mid, y_mid = (x_min + x_max)/2, (y_min + y_max)/2
        self.rel_pos = rel_pos
        self.rotation = rotation
        self.closest_point, self.beam = find_closest_point((x_mid, y_mid), [self.rel_pos])
        self.radius = self.beam.length * 0.075
        if self.rel_pos == "Bottom":
            self.x_mid = self.closest_point[0]
            self.y_min = self.closest_point[1] + self.radius/2
        elif self.rel_pos == "Top":
            self.x_mid = self.closest_point[0]
            self.y_max = self.closest_point[1] - self.radius/2
        elif self.rel_pos == "Left":
            self.x_max = self.closest_point[0] - self.radius/2
            self.y_mid = self.closest_point[1]
        elif self.rel_pos == "Right":
            self.x_min = self.closest_point[0] + self.radius/2
            self.y_mid = self.closest_point[1]
            print("Got to first elif loop")

    def draw(self):
        if self.rel_pos == "Bottom":
            p1x = self.x_mid + self.radius * m.cos(m.radians(-15))
            p1y = self.y_min - self.radius * m.sin(m.radians(-15))
            p2y = self.y_min
            if self.rotation == "Counterwise":
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
                p2x = p1x - (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                m_cnv.create_line(p1x, p1y, p2x, self.y_max, arrow="last", width=2, arrowshape="16 20 6")

        elif self.rel_pos == "Left":
            p1x = self.x_max + self.radius * m.cos(m.radians(255))
            p1y = self.y_mid - self.radius * m.sin(m.radians(255))
            p2x = self.x_max
            if self.rotation == "Counterwise":
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
                p2y = p1y - (self.radius * m.sin(m.radians(15)) * m.tan(m.radians(15)))
                m_cnv.create_line(p1x, p1y, self.x_min, p2y, arrow="last", width=2, arrowshape="16 20 6")

        self.beam.objects["Moments"].append((self.closest_point, self.rotation))


class Load:
    def __init__(self, x_min, y_min, x_max, y_max, direction):
        self.x_min = x_min
        self.y_min = y_min
        self.y_mid = (y_min + y_max)/2
        self.x_max = x_max
        self.y_max = y_max
        self.direction = direction
        self.leftmost_point, self.beam = find_closest_point((x_min, self.y_mid), ["Bottom", "Top"])
        self.rightmost_point, self.beam = find_closest_point((x_max, self.y_mid), ["Bottom", "Top"])
        self.length = self.rightmost_point[0] - self.leftmost_point[0]
        self.height = self.beam.length/6
        self.no_arrows = int(self.length/50)
        self.sep = self.length / self.no_arrows

    def draw(self):
        py1 = self.leftmost_point[1]
        py2 = py1 - self.height
        if self.direction == "Down":
            for i in range(self.no_arrows + 1):
                px = self.leftmost_point[0] + i * self.sep
                m_cnv.create_line(px, py1, px, py2, arrow="first")
        elif self.direction == "Up":
            for i in range(self.no_arrows + 1):
                px = self.leftmost_point[0] + i * self.sep
                m_cnv.create_line(px, py1, px, py2, arrow="last")

        m_cnv.create_line(self.leftmost_point[0], self.leftmost_point[1], self.rightmost_point[0],
                          self.rightmost_point[1])
        m_cnv.create_line(self.leftmost_point[0], py2, self.rightmost_point[0], py2)
        self.beam.objects["Loads"].append((self.leftmost_point, self.rightmost_point, self.direction))


class Surface:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_mid = (x_min + x_max)/2
        self.y_mid = (y_min + y_max)/2
        self.x_max = x_max
        self.y_max = y_max
        self.height = y_max - y_min
        self.width = x_max - x_min
        if self.width > self.height:
            self.closest_item, self.side, self.closest_point = find_closest_object((self.x_mid, self.y_mid), ["Bottom", "Top"])
            print(self.closest_item)
            print(self.side)
            print(self.closest_point)
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
        elif self.width < self.height:
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
            m_cnv.create_line(self.x_max, self.y_mid - self.width/2, self.x_max, self.y_mid + self.width/2)
            for i in range(self.no_lines):
                p1x = self.x_max
                p2x = self.x_min
                p1y = self.y_mid - self.height/2 + (i/(self.no_lines - 1))*self.height 
                p2y = p2y - self.height/(self.no_lines - 1)
                m_cnv.create_line(p1x, p1y, p2x, p2y)
        elif self.side == "Right":
            m_cnv.create_line(self.x_min, self.y_mid - self.width/2, self.x_min, self.y_mid + self.width/2)
            for i in range(self.no_lines):
                p1x = self.x_min
                p2x = self.x_max
                p1y = self.y_mid - self.height/2 + (i/(self.no_lines - 1))*self.height 
                p2y = p2y - self.height/(self.no_lines - 1)
                m_cnv.create_line(p1x, p1y, p2x, p2y)

        if type(self.closest_item) == Beam: # Rätt?
            self.closest_item.objects["Fixed"].append((self.closest_point)) 



        
            



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
        self.layer = (0, 0)
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

        def x_sort(node):
            return node.center[0]

        def y_sort(node):
            return node.center[1]

        x_list = sorted(self.nodes, key = x_sort)
        y_list = sorted(self.nodes, key = y_sort)

        width = x_list[-1] - x_list[0]
        height = y_list[-1] - y_list[0]

        steps = 10
        x_step, y_step = width/steps, height/steps

        while len(y_list) > 0:
            node_0 = y_list[0]
            node_1 = y_list[1]
            y_0 = node_0.center[1]
            y_1 = node_1.center[1]
            y_bar = y_node + y_step
            if y_0 <= y_1 <= y_bar:
                node_1.layer[1] = node_0.layer[1]
                del y_list[1]
            else:
                node_1.layer[1] = node_0.layer[1] + 1
                del y_list[0]

        while len(x_list) > 0:
            node_0 = x_list[0]
            node_1 = x_list[1]
            x_0 = node_0.center[0]
            x_1 = node_1.center[0]
            x_bar = x_node + x_step
            if x_0 <= x_1 <= x_bar:
                node_1.layer[0] = node_0.layer[0]
                del y_list[1]
            else:
                node_1.layer[0] = node_0.layer[0] + 1
                del y_list[0]

        """
        # Aligns the nodes horizontally
        layers = {0: {start_node}}
        start_node.layer = 0
        temp = [start_node]
        finished = []
        while len(temp) > 0:
            for node in temp:
                temp.append(node.connected_nodes)
                temp.remove(node)
                finished.append(node)
                for node_2 in temp:
                    beam = get_beam(node, node_2)
                    angle = beam.orientation
                    if angle == 0:
                        node_2.layer = node.layer
                        layers[node.layer].add(node_2)
                    elif angle == 45 or angle == 135: 
                        if node.center[1] < node_2.center[1]:
                            node_2.layer = node.layer - 1
                            layers[node.layer].add(node_2)
                        else:
                            node_2.layer = node.layer + 1
                            layers[node.layer].add(node_2)
                    elif angle == 90:
           """
def get_objects():
    try:
        df = pd.read_csv(r'C:\Users\admin\Documents\mlHollf\TrainYourOwnYOLO\Data\Source_Images\Test_Image_Detection_Results\Detection_Results.csv')
    except:
        df = pd.read_csv(r'C:\Users\tobia\Desktop\Detection_Results_test.csv')
        #df = pd.read_csv(r'C:\Users\tobia\Desktop\Kandidat\mlHollf\TrainYourOwnYOLO\Data\Source_Images\Test_Image_Detection_Results\Detection_Results.csv')
    df1 = df[["xmin", "ymin", "xmax", "ymax", "label"]]
    df1 = delete_overlapping_objects(df1)
    return (df1)


def delete_overlapping_objects(objects):
    for index1, obj1 in objects.iterrows():
        for index2, obj2 in objects.iterrows():
            if index1 == index2:
                continue
            type1 = labels[obj1[4]]
            type2 = labels[obj2[4]]
            x_min1, y_min1, x_max1, y_max1 = obj1[0], obj1[1], obj1[2], obj1[3],
            x_min2, y_min2, x_max2, y_max2 = obj2[0], obj2[1], obj2[2], obj2[3],
            x_mid1 = (x_max1 + x_min1)/2
            y_mid1 = (y_max1 + y_min1)/2
            # x_mid2 = (x_max2 + x_min2)/2
            # y_mid2 = (y_max2 + y_min2)/2
            # print(str(index1), str(index2), str(x_min2), str(y_min2), str(x_max2), str(y_max2), str(x_mid1), str(y_mid1))
            if x_min2 < x_mid1 < x_max2 and y_min2 < y_mid1 < y_max2:
                if type1 == type2:
                    objects = objects.drop(index1, axis=0)
                elif type1 == "BeamLine":
                    objects = objects.drop(index1, axis=0)
                elif type1 in ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"] and type2 in ["LoadUp", "LoadDown"]:
                    objects = objects.drop(index1, axis=0)
    return objects

<<<<<<< HEAD

=======
>>>>>>> 00e580b6ce2fd6f3fe94a101edfa8ebd523440c7
def draw_all_objects():
    objects = get_objects()
    m_x = interp1d([0, 4000], [0, 1000])
    m_y = interp1d([0, 4000], [800, 0])
    for index, row in objects.iterrows():
        type = labels[row[4]]
        x_min, y_min, x_max, y_max = float(m_x(row[0])), float(m_y(row[1])), float(m_x(row[2])), float(m_y(row[3]))
        if type == "Beam":
            beam = Beam(x_min, y_min, x_max, y_max)
            beam.draw()

    for index, row in objects.iterrows():
        # print(index)
        type = labels[row[4]]
        x_min, y_min, x_max, y_max = float(m_x(row[0])), float(m_y(row[1])), float(m_x(row[2])), float(m_y(row[3]))
        if type == "ArrowDown":
            force = Force(x_min, y_min, x_max, y_max, "Down")
            force.draw()

        elif type == "ArrowUp":
            force = Force(x_min, y_min, x_max, y_max, "Up")
            force.draw()

        elif type == "PinSupport":
            pin = PinSupport(x_min, y_min, x_max, y_max)
            pin.draw()

        elif type == "RollerSupport":
            roller = RollerSupport(x_min, y_min, x_max, y_max)
            roller.draw()

        elif type == "LoadUp":
            load = Load(x_min, y_min, x_max, y_max, "Up")
            load.draw()

        elif type == "LoadDown":
            load = Load(x_min, y_min, x_max, y_max, "Down")
            load.draw()

        #elif type == "ArrowClockwise":
        #   moment = Moment(x_min, y_min, x_max, y_max, "Clockwise", )
    for index, row in objects.iterrows():
        type = labels[row[4]]
        x_min, y_min, x_max, y_max = float(m_x(row[0])), float(m_y(row[1])), float(m_x(row[2])), float(m_y(row[3]))
        if type == "Surface":
            surface = Surface(x_min, y_min, x_max, y_max)
            surface.draw()



draw_all_objects()

# beam1 = Beam(100, 550, 600, 650)
# beam1.draw()
# arrow1 = Force(150, 100, 175, 150, "Left")
# arrow1.draw()
# pin1 = PinSupport(300, 700, 356, 750, 0.15)
# pin1.draw()
# roll = RollerSupport(300, 500, 350, 650)
# roll.draw()
# rolll = RollerSupport(10, 550, 100, 650)
# rolll.draw()
# moment = Moment(750, 550, 800, 650, "Clockwise", "Bottom")
# moment.draw()
# m_cnv.create_line(400, 550, 400, 650, fill="red")
# load = Load(100, 450, 400, 550, "Up")
# load.draw()

m_cnv.update()
m_cnv.postscript(file="bild.png", colormode='color')


im1 = Image.open(r'C:\Users\tobia\Desktop\Kandidat\mlHollf\imageGenerator\bild.png')
im1.save(r'C:\Users\tobia\Desktop\Kandidat\mlHollf\imageGenerator\bild.jpg')


mainloop()
