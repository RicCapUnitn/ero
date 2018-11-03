import unittest

# Add path in order to import  the library
import sys
import os
library_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, library_path + '/../src')

import features
from features import *


class TestBinaryFeature(unittest.TestCase):

    def test_init(self):
        feature = binary_feature.BinaryFeature(1)
        self.assertTrue(feature.value)

    def test_similarity_equal_features(self):
        bf1 = binary_feature.BinaryFeature(0)
        bf2 = binary_feature.BinaryFeature(False)
        self.assertEqual(bf1.similar(bf2), 1.)

    def test_similarity_non_equal_features(self):
        bf1 = binary_feature.BinaryFeature(0)
        bf2 = binary_feature.BinaryFeature(True)
        self.assertEqual(bf1.similar(bf2), 0.)


class TestNormalizedFeature(unittest.TestCase):
    def test_init(self):
        feature = normalized_feature.NormalizedFeature(0.5)
        self.assertEqual(feature.value, 0.5)

    def test_default_similarity_equal_features(self):
        bf1 = normalized_feature.NormalizedFeature(0.3)
        bf2 = normalized_feature.NormalizedFeature(0.5)
        self.assertEqual(bf1.similar(bf2), 0.2)


class TestComparableFeature(unittest.TestCase):

    def test_different_type_features_similarity(self):
        bf1 = binary_feature.BinaryFeature(0)
        bf2 = normalized_feature.NormalizedFeature(0.5)
        with self.assertRaises(TypeError):
            bf1.similar(bf2)
