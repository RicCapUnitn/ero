import unittest
import sys
import os
library_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, library_path + '/../src')

import ero_person
import ero_event
from features import *


class TestPerson(unittest.TestCase):

    def test_fitness(self):
        features1 = [binary_feature.BinaryFeature(1),
                     binary_feature.BinaryFeature(0),
                     normalized_feature.NormalizedFeature(0.5)]
        features2 = [binary_feature.BinaryFeature(1),
                     binary_feature.BinaryFeature(1),
                     normalized_feature.NormalizedFeature(0.3)]
        expected_fitness = 1. + 0. + 0.2
        person = ero_person.Person(features1)
        event = ero_event.Event(features2, "2140675796193939")
        self.assertEqual(person.fitness(event), expected_fitness)
