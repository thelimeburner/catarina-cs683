from ..model.shape import Shape


class Edge(Shape):
    def __init__(self):
        super(Edge, self).__init__()

    def set_shape(self, shape):
        self._shape = shape
