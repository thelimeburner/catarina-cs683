from shape import Shape

HORIZONTAL = '-'
VERTICAL_RIGHT = '/'
VERTICAL_LEFT = '\\'


class Edge(Shape):
    def __init__(self): 
        super(Edge, self).__init__()
    
    def set_shape(self, shape):
        self._shape = shape
