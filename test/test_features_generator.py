import unittest
import warnings

import numpy

from tools import features_generator
from eroproject.features import *

warnings.simplefilter("ignore")


class TestFeaturesGenerator(unittest.TestCase):

    def setUp(self):
        self.test_folder = './test/istat/'
        self.generator = features_generator.PeopleFeaturesGenerator(
            './test/istat/person_features.json',
            './test/istat/comparable_features.json')
        self.generator.import_features_distributions_from_folder(
            self.test_folder)

    def test_import_features_from_folder(self):
        self.assertEqual(
            set(self.generator.distributions.keys()),
            set(["age", "allows_smokers", "cinema", "classical_music_concerts", "disco", "do_sports", "monuments", "museum", "other_concerts", "politics", "religion", "social_activities", "sports_show", "teather"]))
        self.assertListEqual(
            self.generator.sorted_comparable_features_names,
            ["age", "allows_smokers", "cinema", "classical_music_concerts", "disco", "do_sports", "interests", "job", "location", "monuments", "museum", "other_concerts", "politics", "religion", "social_activities", "sports_show", "teather"])

    def test_generate_single_set_of_features(self):
        features = self.generator.generate_one()
        self.assertEqual(len(features), 17)
        self.assertIs(type(features[0]), binary_feature.BinaryFeature)
        self.assertIs(features[6], empty_feature.empty_feature)
        # for feature in features[5:]:
        #self.assertIs(feature, empty_feature.empty_feature)

    def test_generate_multiple_set_of_features(self):
        features = self.generator.generate_many(3)
        self.assertEqual(len(features), 3)
        self.assertIs(type(features[0]), list)
        self.assertEqual(len(features[0]), 17)
        self.assertIs(type(features[0][0]), binary_feature.BinaryFeature)
        self.assertIs(features[0][6], empty_feature.empty_feature)
        # for feature in features[0][5:]:
        #self.assertIs(feature, empty_feature.empty_feature)
