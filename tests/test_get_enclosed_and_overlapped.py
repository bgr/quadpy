from random import randint
from quadpy import Node
from test_basic import Rectangle


key = lambda r: r.bounds


class Test_tiled:
    def setup_class(self):
        self.qt = Node(0, 0, 1000, 1000)
        # fill with 10x10 squares
        [self.qt.insert(Rectangle(x, y, x + 10, y + 10))
         for x in range(0, 1000, 10)
         for y in range(0, 1000, 10)]
        assert len(self.qt.get_children()) == 10000

    ### enclose ###

    def enclose(self, x1, y1, x2, y2):
        return self.qt.get_enclosed_children((x1, y1, x2, y2))

    def test_enclose_all(self):
        assert len(self.enclose(-1, -1, 1001, 1001)) == 10000
        assert len(self.enclose(0, 0, 1000, 1000)) == 10000

    def test_enclose_each(self):
        for x in range(0, 1000, 10):
            for y in range(0, 1000, 10):
                exp = Rectangle(x, y, x + 10, y + 10)
                assert self.enclose(x - 1, y - 1, x + 11, y + 11) == [exp]

    def test_enclose_some(self):
        got = sorted(self.enclose(377, 499, 401, 601), key=key)
        exp = sorted([
            Rectangle(380, 500, 390, 510), Rectangle(390, 500, 400, 510),
            Rectangle(380, 510, 390, 520), Rectangle(390, 510, 400, 520),
            Rectangle(380, 520, 390, 530), Rectangle(390, 520, 400, 530),
            Rectangle(380, 530, 390, 540), Rectangle(390, 530, 400, 540),
            Rectangle(380, 540, 390, 550), Rectangle(390, 540, 400, 550),
            Rectangle(380, 550, 390, 560), Rectangle(390, 550, 400, 560),
            Rectangle(380, 560, 390, 570), Rectangle(390, 560, 400, 570),
            Rectangle(380, 570, 390, 580), Rectangle(390, 570, 400, 580),
            Rectangle(380, 580, 390, 590), Rectangle(390, 580, 400, 590),
            Rectangle(380, 590, 390, 600), Rectangle(390, 590, 400, 600),
        ], key=key)
        assert got == exp

    ### overlap ###

    def overlap(self, x1, y1, x2, y2):
        return self.qt.get_overlapped_children((x1, y1, x2, y2))

    def test_overlap_all(self):
        assert len(self.overlap(-1, -1, 1001, 1001)) == 10000
        assert len(self.overlap(0, 0, 1000, 1000)) == 10000
        assert len(self.overlap(8, 8, 992, 992)) == 10000

    def test_overlap_each(self):
        # overlap at the corner where 4 rectangles meet
        for x in range(10, 1000, 10):
            for y in range(10, 1000, 10):
                exp = sorted([
                    Rectangle(x - 10, y - 10, x, y),
                    Rectangle(x - 10, y, x, y + 10),
                    Rectangle(x, y, x + 10, y + 10),
                    Rectangle(x, y - 10, x + 10, y),
                ], key=key)
                got = sorted(self.overlap(x - 1, y - 1, x + 1, y + 1), key=key)
                assert got == exp

    def test_overlap_some(self):
        got = sorted(self.overlap(387, 501, 391, 591), key=key)
        exp = sorted([
            Rectangle(380, 500, 390, 510), Rectangle(390, 500, 400, 510),
            Rectangle(380, 510, 390, 520), Rectangle(390, 510, 400, 520),
            Rectangle(380, 520, 390, 530), Rectangle(390, 520, 400, 530),
            Rectangle(380, 530, 390, 540), Rectangle(390, 530, 400, 540),
            Rectangle(380, 540, 390, 550), Rectangle(390, 540, 400, 550),
            Rectangle(380, 550, 390, 560), Rectangle(390, 550, 400, 560),
            Rectangle(380, 560, 390, 570), Rectangle(390, 560, 400, 570),
            Rectangle(380, 570, 390, 580), Rectangle(390, 570, 400, 580),
            Rectangle(380, 580, 390, 590), Rectangle(390, 580, 400, 590),
            Rectangle(380, 590, 390, 600), Rectangle(390, 590, 400, 600),
        ], key=key)
        assert got == exp

    ### under_point ###

    def under(self, x, y):
        return self.qt.get_children_under_point(x, y)

    def test_under_point_each(self):
        for x in range(10, 1000, 10):
            for y in range(10, 1000, 10):
                exp = [Rectangle(x, y, x + 10, y + 10)]
                got = self.under(x + randint(1, 9), y + randint(1, 9))
                assert got == exp


class Test_tiled_overlapping_tiles:
    def setup_class(self):
        self.qt = Node(0, 0, 90, 90)
        # put a 9x9 tile on every 3 horizontal and vertical units
        [self.qt.insert(Rectangle(x, y, x + 9, y + 9))
         for x in range(0, 80, 3)
         for y in range(0, 80, 3)]
        assert len(self.qt.get_children()) == 27 * 27

    ### enclose ###

    def enclose(self, x1, y1, x2, y2):
        return self.qt.get_enclosed_children((x1, y1, x2, y2))

    def test_enclose_all(self):
        assert len(self.enclose(-1, -1, 91, 91)) == 27 * 27
        assert len(self.enclose(0, 0, 90, 90)) == 27 * 27

    def test_enclose_each_30x30(self):
        for x in range(0, 51, 3):      # some couldn't fit near the end bounds
            for y in range(0, 51, 3):  # so skip looking for them
                assert len(self.enclose(x, y, x + 30, y + 30)) == 64

    ### overlap ###

    def overlap(self, x1, y1, x2, y2):
        return self.qt.get_overlapped_children((x1, y1, x2, y2))

    def test_overlap_all(self):
        assert len(self.overlap(-1, -1, 91, 91)) == 27 * 27
        assert len(self.overlap(0, 0, 91, 91)) == 27 * 27
        assert len(self.overlap(2, 2, 88, 98)) == 27 * 27

    ### under_point ###
    # this implicitly tests get_overlapped_children, skipped testing that
    # explicitly since it'd be too verbose

    def under(self, x, y):
        return self.qt.get_children_under_point(x, y)

    def test_under_point_each(self):
        # for these values it must be 9 rectangles under point, however for
        # some other values it might be up to 16 (at boundaries, e.g. at 9x9)
        for x in range(7, 80, 9):
            for y in range(7, 80, 9):
                assert len(self.under(x, y)) == 9
        assert len(self.under(9, 9)) == 16
