import pytest
from random import randint
from quadpy import Node
from quadpy.quadtree import fits, overlaps


class Rectangle(object):
    def __init__(self, x_min, y_min, x_max, y_max):
        if x_min > x_max:
            raise ValueError("x_min cannot be greater than x_max")
        if y_min > y_max:
            raise ValueError("y_min cannot be greater than y_max")
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.qt_parent = None
        self.bounds = (x_min, y_min, x_max, y_max)

    def __repr__(self):
        return "{0}({1}, {2}, {3}, {4})".format(self.__class__.__name__,
                                                *self.bounds)

    def __eq__(self, other):
        return self.bounds == other.bounds and isinstance(other, Rectangle)


def get_random_rect(within_bounds):
    x1 = randint(within_bounds[0], within_bounds[2])
    x2 = randint(within_bounds[0], within_bounds[2])
    y1 = randint(within_bounds[1], within_bounds[3])
    y2 = randint(within_bounds[1], within_bounds[3])
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    return Rectangle(x1, y1, x2, y2)


class Test_fits_and_overlaps_helper_functions:
    @pytest.mark.parametrize(
        ('bounds_A', 'bounds_B', 'should_fit', 'should_overlap'), [
            ((0, 0, 20, 20), (0, 0, 20, 20), True, True),   # exact
            ((5, 5, 10, 10), (0, 0, 20, 20), True, True),   # small inside
            ((0, 0, 21, 20), (0, 0, 20, 20), False, True),  # sligtly larger
            ((0, 0, 20, 21), (0, 0, 20, 20), False, True),
            ((-1, 0, 20, 20), (0, 0, 20, 20), False, True),
            ((0, -1, 20, 20), (0, 0, 20, 20), False, True),
            ((-10, -10, 30, -5), (0, 0, 20, 20), False, False),  # wide above
            ((-10, 30, 35, 40), (0, 0, 20, 20), False, False),   # wide below
            ((-10, -10, -5, 30), (0, 0, 20, 20), False, False),  # tall left
            ((30, -10, 35, 30), (0, 0, 20, 20), False, False),   # tall right
            ((10, 10, 30, 15), (0, 0, 20, 20), False, True),  # wide across
            ((10, 10, 15, 30), (0, 0, 20, 20), False, True),  # tall across
            ((-10, -10, 10, 10), (0, 0, 20, 20), False, True),  # corner only
            ((10, -10, 30, 10), (0, 0, 20, 20), False, True),
            ((10, 10, 30, 30), (0, 0, 20, 20), False, True),
            ((-10, 10, 10, 30), (0, 0, 20, 20), False, True),
            ((-10, 10, 10, 15), (0, 0, 20, 20), False, True),  # two corners
            ((10, 10, 30, 15), (0, 0, 20, 20), False, True),
            ((10, -10, 15, 15), (0, 0, 20, 20), False, True),
            ((10, 10, 15, 30), (0, 0, 20, 20), False, True),
        ])
    def test_fits(self, bounds_A, bounds_B, should_fit, should_overlap):
        assert fits(bounds_A, bounds_B) == should_fit
        assert overlaps(bounds_A, bounds_B) == should_overlap


class Test_subdivisions_working:
    @pytest.mark.parametrize('coords', [
        (0.1, 0.1, 0.2, 0.2),
        (1023.1, 0.1, 1023.2, 0.2),
        (1023.1, 1023.1, 1023.2, 1023.2),
        (0.1, 1023.1, 0.2, 1023.2),
    ])
    @pytest.mark.parametrize('max_depth', list(range(20)))
    def test_insert_small_rect_in_corner(self, max_depth, coords):
        # inserting small rectangle in top left corner should make the
        # quadtree perform maximum number of subdivisions
        qt = Node(0, 0, 1024, 1024, max_depth)
        assert qt._get_depth() == 0
        assert qt._get_number_of_nodes() == 1
        rect = Rectangle(*coords)
        qt.insert(rect)
        assert qt._get_depth() == max_depth
        assert qt._get_number_of_nodes() == 1 + max_depth * 4
        qt.remove(rect)
        assert qt._get_depth() == 0
        assert qt._get_number_of_nodes() == 1


    @pytest.mark.parametrize('coords', [
        (511, 511, 513, 513),
        (20, 511, 22, 513),
        (720, 511, 722, 513),
        (511, 20, 513, 22),
        (511, 720, 513, 722),
    ])
    @pytest.mark.parametrize('max_depth', list(range(1, 20)))
    def test_item_crossing_border(self, max_depth, coords):
        # adding item that cross borders shouldn't trigger nested subdivisions
        qt = Node(0, 0, 1024, 1024, max_depth)
        assert qt._get_depth() == 0
        assert qt._get_number_of_nodes() == 1
        rect = Rectangle(*coords)
        qt.insert(rect)
        assert qt.get_children() == [rect]
        assert qt._get_depth() == 1
        assert qt._get_number_of_nodes() == 5



class Test_insert_and_remove_single_item_once:
    def setup_class(self):
        self.qt = Node(0, 0, 1000, 1000)
        self.rect = Rectangle(20, 20, 40, 40)

    def test_is_empty_after_initialization(self):
        assert self.qt.direct_children == []
        assert self.qt.get_children() == []

    def test_contains_rect_after_insert(self):
        self.qt.insert(self.rect)
        assert self.qt.get_children() == [self.rect]

    def test_is_empty_after_removing(self):
        self.qt.remove(self.rect)
        assert self.qt.direct_children == []
        assert self.qt.get_children() == []


class Test_insert_and_remove_multiple_items:
    def test_insert_two_at_different_locations(self):
        qt = Node(0, 0, 1000, 1000)
        rect1 = Rectangle(10, 10, 20, 20)
        rect2 = Rectangle(800, 800, 900, 900)

        qt.insert(rect1)
        qt.insert(rect2)
        assert sorted(qt.get_children()) == sorted([rect1, rect2])

        qt.remove(rect1)
        assert qt.get_children() == [rect2]

        qt.insert(rect1)
        assert sorted(qt.get_children()) == sorted([rect1, rect2])

        qt.remove(rect2)
        assert qt.get_children() == [rect1]

        qt.remove(rect1)
        assert qt.get_children() == []
        assert qt.direct_children == []

    def test_insert_two_at_same_location(self):
        qt = Node(0, 0, 1000, 1000)
        rect1 = Rectangle(10, 10, 20, 20)
        rect2 = Rectangle(10, 10, 20, 20)

        qt.insert(rect1)
        qt.insert(rect2)
        assert sorted(qt.get_children()) == sorted([rect1, rect2])

        qt.remove(rect1)
        assert qt.get_children() == [rect2]

        qt.insert(rect1)
        assert sorted(qt.get_children()) == sorted([rect1, rect2])

        qt.remove(rect2)
        assert qt.get_children() == [rect1]

        qt.remove(rect1)
        assert qt.get_children() == []
        assert qt.direct_children == []

    def test_clear(self):
        qt = Node(0, 0, 1000, 1000)
        [qt.insert(get_random_rect(qt.bounds)) for _ in range(300)]
        assert len(qt.get_children()) == 300
        assert qt._get_depth() in [3, 4]  # can't know for sure
        qt.clear()
        assert qt.get_children() == []
        assert qt.direct_children == []
