import unittest
import sys
import os

library_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, library_path + '/../src')

import ero_person
import ero_event
from combiners import *
from features import *


class TestLocationCombiner(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.person_location = {
            'current_location': (46.064785, 11.127795),
            'home_location': (46.068268, 11.118582),
            'work_location': (46.056249, 11.130175)
        }
        cls.event_location = (46.052505, 11.130151)
        cls.expected_similarity = 0.6

    def test_person_location_combiner(self):
        similarity = combiners.person_location_combiner(
            self.person_location, self.event_location)
        self.assertEqual(similarity, self.expected_similarity)

    def test_event_location_combiner(self):
        similarity = combiners.event_location_combiner(
            self.event_location, self.person_location)
        self.assertEqual(similarity, self.expected_similarity)
