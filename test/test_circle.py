import unittest

from eroproject.features import *
from eroproject import ero_ego_circle as ego_circle


class TestEgoCircle(unittest.TestCase):

    def test_item_in_circle(self):
        circle = ego_circle.EgoCircle('name', [0, 1, 2])
        self.assertTrue(0 in circle)

    def test_item_not_in_circle(self):
        circle = ego_circle.EgoCircle('name', [0, 1, 2])
        self.assertTrue(3 not in circle)

    def test_iteration(self):
        circle = ego_circle.EgoCircle('name', [0, 1, 2])
        self.assertListEqual(list(circle.__iter__()), [0, 1, 2])
