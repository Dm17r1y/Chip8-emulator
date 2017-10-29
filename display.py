#!/usr/bin/python3

class Point:

    def __init__(self, x, y):
        self._x = x
        self._y = y

    def __hash__(self):
        return self.x * 31 + self.y

    def __eq__(self, other):
        return type(other) is Point and self.x == other.x\
               and self.y == other.y

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

class Display:

    def __init__(self):
        self._pixels = {}

    WIDTH = 64
    HEIGHT = 32

    @staticmethod
    def get_correct_point(point):
        x, y = point.x, point.y
        x = x % Display.WIDTH
        y = y % Display.HEIGHT
        return Point(x, y)


    def set_pixel(self, point, value):
        point = Display.get_correct_point(point)
        self._pixels[point] = value

    def get_pixel(self, point):
        point = Display.get_correct_point(point)
        if point in self._pixels:
            return self._pixels[point]
        return 0

    def clear(self):
        self._pixels.clear()
