"""Just a useful rectangle"""
import random


class Rectangle(object):
    def __init__(self, x_min, y_min, x_max, y_max):
        if x_min > x_max:
            raise ValueError("x_min cannot be greater than x_max")
        if y_min > y_max:
            raise ValueError("y_min cannot be greater than y_max")
        self.qt_data = None
        self.bounds = (x_min, y_min, x_max, y_max)

    def __repr__(self):
        return "{0}({1}, {2}, {3}, {4})".format(self.__class__.__name__,
                                                *self.bounds)

    def __eq__(self, other):
        return self.bounds == other.bounds and isinstance(other, Rectangle)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.bounds)


def random_bounds(within_bounds, max_size=0):
    if max_size > 0:
        x1 = random.uniform(within_bounds[0], within_bounds[2] - max_size)
        y1 = random.uniform(within_bounds[1], within_bounds[3] - max_size)
        x2 = x1 + random.uniform(0.001, max_size)
        y2 = y1 + random.uniform(0.001, max_size)
    else:
        x1 = random.uniform(within_bounds[0], within_bounds[2])
        x2 = random.uniform(within_bounds[0], within_bounds[2])
        y1 = random.uniform(within_bounds[1], within_bounds[3])
        y2 = random.uniform(within_bounds[1], within_bounds[3])
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
    return (x1, y1, x2, y2)


def random_rectangle(within_bounds, max_size=0):
    return Rectangle(*random_bounds(within_bounds, max_size))
