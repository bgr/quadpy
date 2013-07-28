"""
Quadtree implementation for Python
https://github.com/bgr/quadpy

Based on "MX-CIF Quadtrees implementation in javascript" by Patrick DeHaan
https://github.com/pdehn/jsQuad

original copyright notice:
------------------------------------------------------------------------------
Copyright (c) 2011 Patrick DeHaan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
------------------------------------------------------------------------------
"""


def fits(bounds_inside, bounds_around):
    """Returns True if bounds_inside fits entirely within bounds_around."""
    x1_min, y1_min, x1_max, y1_max = bounds_inside
    x2_min, y2_min, x2_max, y2_max = bounds_around
    return (x1_min >= x2_min and x1_max <= x2_max
            and y1_min >= y2_min and y1_max <= y2_max)


def overlaps(bounds_A, bounds_B):
    """Returns True if bounds_A and bounds_B partially overlap."""
    x1_min, y1_min, x1_max, y1_max = bounds_A
    x2_min, y2_min, x2_max, y2_max = bounds_B
    x_overlaps = (x1_min <= x2_min <= x1_max) or (x2_min <= x1_min <= x2_max)
    y_overlaps = (y1_min <= y2_min <= y1_max) or (y2_min <= y1_min <= y2_max)
    return x_overlaps and y_overlaps


class Node(object):
    def __init__(self, x_min, y_min, x_max, y_max, max_depth=4, parent=None):
        if x_min > x_max:
            raise ValueError("x_min cannot be greater than x_max")
        if y_min > y_max:
            raise ValueError("y_min cannot be greater than y_max")
        if max_depth < 0:
            raise ValueError("max_depth cannot be less than 0")
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.max_depth = max_depth
        self.direct_children = []
        self.quadrants = []
        self.parent = parent
        self.bounds = (x_min, y_min, x_max, y_max)

    def subdivide(self):
        x_min, y_min = self.x_min, self.y_min
        x_max, y_max = self.x_max, self.y_max
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        depth = self.max_depth - 1
        self.quadrants = [
            Node(x_min, y_min, x_center, y_center, depth, self),
            Node(x_center, y_min, x_max, y_center, depth, self),
            Node(x_min, y_center, x_center, y_max, depth, self),
            Node(x_center, y_center, x_max, y_max, depth, self),
        ]

    def clear(self):
        self.direct_children = []
        [q.clear() for q in self.quadrants]
        self.quadrants = []

    def insert(self, child):
        if fits(child.bounds, self.bounds):
            self._insert(child)
        else:
            self.direct_children.append(child)
            child.qt_parent = self
        # TODO: non-enclosed objects should probably either throw an error or
        # cause the node to create parents for itself. This solutions keeps
        # track of the object, but will cause false positives when selection
        # boundaries enclose the node. Another possible solution is to create
        # a seperate container for them.

    def _insert(self, child):
        # try to subdivide in any case
        if not self.quadrants and self.max_depth > 0:
            self.subdivide()

        # choose which sub-node to put it in
        # child must fit entirely (must not cross node's boundaries)
        for q in self.quadrants:
            if fits(child.bounds, q.bounds):
                q._insert(child)
                return
        # no better sub-node found, put it inside self
        self.direct_children.append(child)
        child.qt_parent = self

    def reinsert(self, child):
        parent = child.qt_parent
        parent._remove(child)
        parent._reinsert(child)

    def _reinsert(self, child):
        if fits(child.bounds, self.bounds):
            self._insert(child)
        else:
            if self.parent is None:
                raise ValueError("New child bounds don't fit in quadtree")
            self.parent._reinsert(child)

    def remove(self, child):
        # child has reference to parent so we don't have to search the tree
        child.qt_parent._remove(child)  # in original it says .remove, bug

    def _remove(self, child):
        self.direct_children.remove(child)
        self._try_cleanup()

    def _try_cleanup(self):
        # if this node and all sub-nodes are empty, clean and tell parent to
        # attempt cleanup also since it might be empty too
        if not self.get_children():
            self.clear()
            if self.parent:
                self.parent._try_cleanup()

    def get_children(self):
        subchildren = [ch for q in self.quadrants for ch in q.get_children()]
        return self.direct_children + subchildren

    def fix_bounds(self, bounds):
        x1, y1, x2, y2 = bounds
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        return (x1, y1, x2, y2)

    def get_enclosed_children(self, within_bounds):
        # assure that bounds have proper values
        within_bounds = self.fix_bounds(within_bounds)

        # no overlap
        if not overlaps(within_bounds, self.bounds):
            return []

        # entire node is enclosed, return everything
        if fits(self.bounds, within_bounds):
            return self.get_children()

        # node is partially overlapped, try to get subchildren
        enclosed_subchildren = [ch for q in self.quadrants for ch
                                in q.get_enclosed_children(within_bounds)]
        # find enclosed children
        enclosed_children = [ch for ch in self.direct_children
                             if fits(ch.bounds, within_bounds)]

        return enclosed_children + enclosed_subchildren

    def get_overlapped_children(self, bounds):
        # assure that bounds have proper values
        bounds = self.fix_bounds(bounds)

        # no overlap
        if not overlaps(bounds, self.bounds):
            return []

        # entire node is enclosed, return everything
        if fits(self.bounds, bounds):
            return self.get_children()

        # node is partially overlapped, try to get subchildren
        overlapped_subchildren = [ch for q in self.quadrants
                                  for ch in q.get_overlapped_children(bounds)]
        # find overlapped children
        overlapped_children = [ch for ch in self.direct_children
                               if overlaps(ch.bounds, bounds)]

        return overlapped_children + overlapped_subchildren

    def get_children_under_point(self, x, y):  # TODO: inconsistent api
        return self.get_overlapped_children((x, y, x, y))  # hack

    def _get_depth(self):
        # for testing and debug
        if not self.quadrants:
            return 0
        return 1 + max(q._get_depth() for q in self.quadrants)

    def _get_number_of_nodes(self):
        # for testing and debug
        if not self.quadrants:
            return 1
        return 1 + sum(q._get_number_of_nodes() for q in self.quadrants)

    def __repr__(self):
        params = [str(p) for p in list(self.bounds) + [self.max_depth,
                                                       self.parent]]
        return "{0}({1})".format(self.__class__.__name__, ', '.join(params))
