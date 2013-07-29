import pytest
from quadpy import Node
from quadpy.quadtree import fits, overlaps
from quadpy.rectangle import Rectangle, random_rectangle



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
        (0.001, 0.001, 0.002, 0.002),
        (1023.998, 0.001, 1023.999, 0.002),
        (1023.998, 1023.998, 1023.999, 1023.999),
        (0.001, 1023.998, 0.002, 1023.999),
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
        assert qt.get_children() == [rect1, rect2]

        qt.remove(rect1)
        assert qt.get_children() == [rect2]

        qt.insert(rect1)
        assert qt.get_children() == [rect1, rect2]

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
        assert qt.get_children() == [rect1, rect2]

        qt.remove(rect1)
        assert qt.get_children() == [rect2]

        qt.insert(rect1)
        assert qt.get_children() == [rect1, rect2]

        qt.remove(rect2)
        assert qt.get_children() == [rect1]

        qt.remove(rect1)
        assert qt.get_children() == []
        assert qt.direct_children == []

    def test_clear(self):
        qt = Node(0, 0, 1000, 1000)
        [qt.insert(random_rectangle(qt.bounds)) for _ in range(300)]
        assert len(qt.get_children()) == 300
        assert qt._get_depth() in [3, 4]  # can't know for sure
        qt.clear()
        assert qt.get_children() == []
        assert qt.direct_children == []


class Test_reinsert:
    @pytest.mark.parametrize('max_depth', list(range(1, 20)))
    def test_reinsert_into_same_quadrant(self, max_depth):
        bounds = (0.001, 0.001, 0.002, 0.002)
        qt = Node(0, 0, 1024, 1024, max_depth)
        assert qt._get_depth() == 0
        assert qt._get_number_of_nodes() == 1
        rect = Rectangle(*bounds)

        qt.insert(rect)
        assert qt._get_depth() == max_depth
        assert qt._get_number_of_nodes() == 1 + max_depth * 4
        # make sure that top-left quadrant is the only one subdivided
        depths = [qt.quadrants[i]._get_depth() for i in range(4)]
        assert depths == [max_depth - 1, 0, 0, 0]

        # change coords and reinsert into same place
        qt.reinsert(rect)
        assert qt._get_depth() == max_depth
        assert qt._get_number_of_nodes() == 1 + max_depth * 4
        depths = [qt.quadrants[i]._get_depth() for i in range(4)]
        assert depths == [max_depth - 1, 0, 0, 0]

    @pytest.mark.parametrize('max_depth', list(range(1, 14)))
    def test_reinsert_into_another_quadrant(self, max_depth):
        bounds_1 = (0.01, 0.01, 0.02, 0.02)
        bounds_2 = (1023.998, 1023.998, 1023.999, 1023.999)
        qt = Node(0, 0, 1024, 1024, max_depth)
        assert qt._get_depth() == 0
        assert qt._get_number_of_nodes() == 1
        rect = Rectangle(*bounds_1)
        qt.insert(rect)
        assert qt._get_depth() == max_depth
        assert qt._get_number_of_nodes() == 1 + max_depth * 4

        # make sure that top-left quadrant is the only one subdivided
        depths = [qt.quadrants[i]._get_depth() for i in range(4)]
        assert depths == [max_depth - 1, 0, 0, 0]

        # change coords and reinsert
        rect.bounds = bounds_2
        qt.reinsert(rect)
        assert qt._get_depth() == max_depth
        assert qt._get_number_of_nodes() == 1 + max_depth * 4

        # make sure that bottom-right quadrant is the only one subdivided
        depths = [qt.quadrants[i]._get_depth() for i in range(4)]
        assert depths == [0, 0, 0, max_depth - 1]
