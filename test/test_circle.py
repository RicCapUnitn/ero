import unittest

# Add path in order to import  the library
import sys
import os
library_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, library_path + '/../src')

import ego_circle


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
