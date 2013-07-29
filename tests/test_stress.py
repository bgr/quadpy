import pytest
from random import randint, shuffle
from quadpy import Node
from quadpy.rectangle import random_rectangle


quadtree_bounds_params = [
    (0, 0, 100, 100),
    (100, 100, 1000, 1000),
    (30, 30, 40, 40),
    (0, 0, 1, 1),  # very small quadtree should work
    (-1000, -1000, 100, 100),  # negative bounds should work
    (-1000, -1000, -300, -300),
    (200, 300, 400, 700),  # non-square quadtree should work
    (-1000, -300, -200, -100),
]


class Test_stress_insert_remove_reinsert_one_item:
    @pytest.mark.parametrize('quadtree_bounds', quadtree_bounds_params)
    @pytest.mark.parametrize('max_depth', list(range(1, 20)))
    def test_insert_and_remove(self, quadtree_bounds, max_depth):
        params = quadtree_bounds + (max_depth,)
        qt = Node(*params)
        rect = random_rectangle(quadtree_bounds)
        print 'Testing with {0}, {1}'.format(qt, rect)  # shown if test fails
        assert qt.direct_children == []
        assert qt.get_children() == []
        qt.insert(rect)
        assert qt.get_children() == [rect]
        qt.remove(rect)
        assert qt.direct_children == []
        assert qt.get_children() == []

    @pytest.mark.parametrize('quadtree_bounds', quadtree_bounds_params)
    @pytest.mark.parametrize('max_depth', list(range(1, 20)))
    def test_insert_and_reinsert(self, quadtree_bounds, max_depth):
        params = quadtree_bounds + (max_depth,)
        qt = Node(*params)
        rect = random_rectangle(quadtree_bounds)
        print 'Testing with {0}, {1}'.format(qt, rect)  # shown if test fails
        assert qt.direct_children == []
        assert qt.get_children() == []
        qt.insert(rect)
        assert qt.get_children() == [rect]
        qt.reinsert(rect)
        assert qt.get_children() == [rect]


# tests below are slow, take a few minutes, however they DID catch few bugs

class Test_stress_insert_and_remove_many_items:
    @pytest.mark.parametrize('n_elems', [1, 4, 10, 40, 100, 400, 1000])
    @pytest.mark.parametrize('quadtree_bounds', quadtree_bounds_params)
    @pytest.mark.parametrize('max_depth', list(range(1, 12)))
    @pytest.mark.parametrize('removal_order', [0, 1, 2])
    @pytest.mark.slow
    def test(self, n_elems, quadtree_bounds, max_depth, removal_order):
        rects = [random_rectangle(quadtree_bounds) for _ in range(n_elems)]
        params = quadtree_bounds + (max_depth,)
        qt = Node(*params)
        [qt.insert(r) for r in rects]
        key = lambda r: r.bounds
        assert sorted(qt.get_children(), key=key) == sorted(rects, key=key)
        assert len(qt.get_children()) == n_elems

        pop_element = [
            lambda: rects.pop(0),
            lambda: rects.pop(),
            lambda: rects.pop(randint(0, len(rects) - 1)),
        ][removal_order]

        while rects:
            rect = pop_element()
            qt.remove(rect)
            assert sorted(qt.get_children(), key=key) == sorted(rects, key=key)

        assert qt.get_children() == []


class Test_stress_reinsert:
    @pytest.mark.parametrize('n_elems', [1, 4, 10, 40, 100, 400])
    @pytest.mark.parametrize('quadtree_bounds', quadtree_bounds_params)
    @pytest.mark.parametrize('max_depth', list(range(1, 12)))
    @pytest.mark.parametrize('change_bounds', [True, False])
    @pytest.mark.slow
    def test(self, n_elems, quadtree_bounds, max_depth, change_bounds):
        rects = [random_rectangle(quadtree_bounds) for _ in range(n_elems)]
        params = quadtree_bounds + (max_depth,)
        qt = Node(*params)
        [qt.insert(r) for r in rects]
        key = lambda r: r.bounds
        assert sorted(qt.get_children(), key=key) == sorted(rects, key=key)
        assert len(qt.get_children()) == n_elems

        shuffle(rects)

        for r in rects:
            if change_bounds:
                new_bounds = random_rectangle(quadtree_bounds).bounds
                r.bounds = new_bounds
            qt.reinsert(r)
            assert sorted(qt.get_children(), key=key) == sorted(rects, key=key)
