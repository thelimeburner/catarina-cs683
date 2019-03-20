from termcolor import colored, cprint


class Shape(object):
    def __init__(self, shape, x, y):
        self._shape = shape
        self._color = "black"
        self.highlights = None
        self.color_attr = None
        self._x = x
        self._y = y

    def set_shape(self, shape):
        self._shape = shape

    def set_color(self, color, highlights=None, color_attr=None):
        self._color = color
        self.highlights = highlights
        self.color_attr = color_attr

    def set_xy(self, x, y):
        self._x = x
        self._y = y

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def __repr__(self):
        if self._color == 'black':
            return self._shape
        if self.color_attr:
            return colored(self._shape, self._color, self.highlights, attrs=[self.color_attr])
        else:
            return colored(self._shape, self._color, self.highlights)
