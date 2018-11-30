from termcolor import colored, cprint


class Shape(object):
    def __init__(self, shape, x, y):
        self._shape = shape
        self._color = "magenta"
        self._x = x
        self._y = y
    
    def set_color(self, color):
        self._color = color

    def set_xy(self, x, y):
        self._x = x
        self._y = y

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def __repr__(self):
        return colored(self._shape, self._color)
