import unittest

from eroproject.combiners import *
from eroproject.features import *


class TestEmptyFeature(unittest.TestCase):

    def test_other_similar_empty(self):
        other = binary_feature.BinaryFeature(1)
        empty = empty_feature.empty_feature
        self.assertEqual(other.similar(empty), 0)

    def test_empty_similar_other(self):
        other = binary_feature.BinaryFeature(1)
        empty = empty_feature.empty_feature
        self.assertEqual(empty.similar(other), 0)

    def test_empty_similar_empty(self):
        empty = empty_feature.empty_feature
        self.assertEqual(empty.similar(empty), 0)


class TestBinaryFeature(unittest.TestCase):

    def test_init(self):
        feature = binary_feature.BinaryFeature(1)
        self.assertTrue(feature.value)

    def test_init_string_true(self):
        feature = binary_feature.BinaryFeature("True")
        self.assertTrue(feature.value)

    def test_init_string_false(self):
        feature = binary_feature.BinaryFeature("False")
        self.assertFalse(feature.value)

    def test_similarity_equal_features(self):
        bf1 = binary_feature.BinaryFeature(0)
        bf2 = binary_feature.BinaryFeature(False)
        self.assertEqual(bf1.similar(bf2), 1.)

    def test_similarity_non_equal_features(self):
        bf1 = binary_feature.BinaryFeature(0)
        bf2 = binary_feature.BinaryFeature(True)
        self.assertEqual(bf1.similar(bf2), 0.)

    @unittest.skip('See issue #10')
    def test_similarity_bad_initialized_feature_to_empty_feature_other(self):
        bf = binary_feature.BinaryFeature(1)
        wrong_initialized_bf = binary_feature.BinaryFeature(None)
        with self.assertRaises(NotImplementedError):
            bf.similar(wrong_initialized_bf)

    @unittest.skip('See issue #10')
    def test_similarity_bad_initialized_feature_to_empty_feature_self(self):
        wrong_initialized_bf = binary_feature.BinaryFeature(None)
        other = binary_feature.BinaryFeature(1)
        with self.assertRaises(NotImplementedError):
            wrong_initialized_bf.similar(other)


class TestNormalizedFeature(unittest.TestCase):
    def test_init(self):
        feature = normalized_feature.NormalizedFeature(0.5)
        self.assertEqual(feature.value, 0.5)

    def test_default_similarity_equal_features(self):
        bf1 = normalized_feature.NormalizedFeature(0.3)
        bf2 = normalized_feature.NormalizedFeature(0.5)
        self.assertEqual(bf1.similar(bf2), 0.8)


class TestComparableFeature(unittest.TestCase):

    def test_invalid_instantiation(self):
        with self.assertRaises(NotImplementedError):
            comparable_feature.ComparableFeature().similar()

    def test_invalid_subclass_declaration(self):

        class InvalidFeature(comparable_feature.ComparableFeature):
            def __init__(self):
                pass

        with self.assertRaises(NotImplementedError):
            InvalidFeature().similar(InvalidFeature())

    def test_different_type_features_similarity(self):
        bf1 = binary_feature.BinaryFeature(0)
        bf2 = normalized_feature.NormalizedFeature(0.5)
        with self.assertRaises(TypeError):
            bf1.similar(bf2)


class TestCompositeFeature(unittest.TestCase):

    def test_location_similarity(self):
        person_location = {
            'current_location': (46.064785, 11.127795),
            'home_location': (46.068268, 11.118582),
            'work_location': (46.056249, 11.130175)
        }
        event_location = (46.052505, 11.130151)
        expected_similarity = 0.6

        cf1 = composite_feature.CompositeFeature(
            person_location, combiners.person_location_combiner)
        cf2 = composite_feature.CompositeFeature(
            event_location, combiners.event_location_combiner)

        similarity = cf1.similar(cf2)
        self.assertEqual(similarity, expected_similarity)
