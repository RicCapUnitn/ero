import os
# Add path in order to import  the library
import sys
import unittest
import warnings

import numpy

library_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, library_path + '/../src')
sys.path.insert(0, library_path + '/../tools')

import features
import features_generator
from features import *

warnings.simplefilter("ignore")


class TestFeaturesGenerator(unittest.TestCase):

    def setUp(self):
        self.test_folder = './test/istat/'
        self.generator = features_generator.FeaturesGenerator(
            './test/istat/person_features.json',
            './test/istat/event_features.json',
            './test/istat/comparable_features.json')
        self.generator.import_features_distributions_from_folder(
            self.test_folder)

    def test_import_features_from_folder(self):
        self.assertEqual(
            set(self.generator.distributions.keys()),
            set(['allows_smokers', "age"]))
        self.assertListEqual(
            self.generator.sorted_comparable_features_names,
            ["age", "allows_smokers", "interests", "job", "location"])

    def test_generate_single_set_of_features(self):
        features = self.generator.generate_one()
        self.assertEqual(len(features), 5)
        self.assertIs(type(features[0]), binary_feature.BinaryFeature)
        for feature in features[2:]:
            self.assertIs(feature, empty_feature.empty_feature)

    def test_generate_multiple_set_of_features(self):
        features = self.generator.generate_many(3)
        self.assertEqual(len(features), 3)
        self.assertIs(type(features[0]), list)
        self.assertEqual(len(features[0]), 5)
        self.assertIs(type(features[0][0]), binary_feature.BinaryFeature)
        for feature in features[0][2:]:
            self.assertIs(feature, empty_feature.empty_feature)
