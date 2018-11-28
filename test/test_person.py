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
        default_features_weight = 0.5
        features1 = [binary_feature.BinaryFeature(1),
                     binary_feature.BinaryFeature(0),
                     normalized_feature.NormalizedFeature(0.5)]
        features2 = [binary_feature.BinaryFeature(1),
                     binary_feature.BinaryFeature(1),
                     normalized_feature.NormalizedFeature(0.3)]
        expected_fitness = (default_features_weight * 1. +
                            default_features_weight * 0. +
                            default_features_weight * 0.8) / 3.
        person = ero_person.Person(features1)
        event = ero_event.Event(0, features2)
        self.assertEqual(person.fitness(event), expected_fitness)

    def test_weights(self):
        features1 = [binary_feature.BinaryFeature(1),
                     normalized_feature.NormalizedFeature(0.5)]
        features2 = [binary_feature.BinaryFeature(1),
                     normalized_feature.NormalizedFeature(0.3)]
        weights = [0.1, 0.7]
        expected_fitness = (0.1 * 1 + 0.7 * 0.8) / 2.

        person = ero_person.Person(features1)
        person.features_weights = weights
        event = ero_event.Event(0, features2)

        self.assertEqual(person.fitness(event), expected_fitness)

    def test_set_features_weights(self):
        features = [binary_feature.BinaryFeature(1),
                    normalized_feature.NormalizedFeature(0.5)]
        person = ero_person.Person(features)

        default_features_weights = [0.5] * len(features)
        expected_features_weights = [0.7] * len(features)

        self.assertListEqual(person.features_weights, default_features_weights)

        person.set_features_weights(0.7)

        self.assertListEqual(person.features_weights,
                             expected_features_weights)
