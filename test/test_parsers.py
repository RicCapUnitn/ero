import unittest

from eroproject.combiners import *
from eroproject.ero_event import Event
from eroproject.ero_exceptions import ImportException
from eroproject.features import *
from eroproject.parsers import *


class TestEventParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        comparable_features = ['age', 'location', 'allows_smokers', 'teather']
        cls._parser = event_parser.EventParser(comparable_features)

    def test_parse_valid_event(self):
        test_event = {
            "name": "Classicla Opera",
            "start_time": "19:30",
            "end_time": "22:30",
            "place": {
                "name": "Philharmonic Society of Trento",
                "location": {
                    "latitude": 46.066723,
                    "longitude": 11.120487,
                },
            },
            "allows_smokers": False,
            "teather": True,
            "cinema": False,
            "museum": False,
            "classical_music_concerts": True,
            "other_concerts": False,
            "sports_show": False,
            "disco": False,
            "monuments": False,
            "do_sports": False,
            "interests": [],
            "politics": False,
            "religion": False,
            "social_activities": False,
            "id": "1532214687109127"
        }
        parsed_event = self._parser.parse_event(test_event)
        self.assertIsInstance(parsed_event, Event)
        self.assertEqual(len(parsed_event.features), 4)

        age_feature = parsed_event.features[0]
        self.assertIs(age_feature, empty_feature.empty_feature)

        location_feature = parsed_event.features[2]
        expected_location = (46.066723, 11.120487)
        self.assertIsInstance(
            location_feature, composite_feature.CompositeFeature)
        self.assertEqual(location_feature.value, expected_location)
        self.assertIs(location_feature.combiner,
                      combiners.event_location_combiner)

        expected_shortened_id = int("1532214687109127"[:5])
        self.assertEqual(parsed_event.id, expected_shortened_id)

    def test_parse_event_missing_location(self):
        test_event = {
            "name": "Classicla Opera",
            "start_time": "19:30",
            "end_time": "22:30",
            "place": {
                "name": "Philharmonic Society of Trento"
            },
            "allows_smokers": False,
            "teather": True,
            "cinema": False,
            "museum": False,
            "classical_music_concerts": True,
            "other_concerts": False,
            "sports_show": False,
            "disco": False,
            "monuments": False,
            "do_sports": False,
            "interests": [],
            "politics": False,
            "religion": False,
            "social_activities": False,
            "id": "1532214687109127"
        }
        parsed_event = self._parser.parse_event(test_event)
        self.assertIsInstance(parsed_event, Event)
        self.assertEqual(len(parsed_event.features), 4)

        age_feature = parsed_event.features[0]
        self.assertIs(age_feature, empty_feature.empty_feature)

        location_feature = parsed_event.features[2]
        self.assertIs(location_feature, empty_feature.empty_feature)

        expected_shortened_id = int("1532214687109127"[:5])
        self.assertEqual(parsed_event.id, expected_shortened_id)

    def test_parse_event_missing_id(self):
        test_event = {
            "name": "Classicla Opera",
            "start_time": "19:30",
            "end_time": "22:30",
            "place": {
                "name": "Philharmonic Society of Trento",
                "location": {
                    "latitude": 46.066723,
                    "longitude": 11.120487,
                },
            },
            "allows_smokers": False,
            "teather": True,
            "cinema": False,
            "museum": False,
            "classical_music_concerts": True,
            "other_concerts": False,
            "sports_show": False,
            "disco": False,
            "monuments": False,
            "do_sports": False,
            "interests": [],
            "politics": False,
            "religion": False,
            "social_activities": False,
        }

        with self.assertRaises(ImportException):
            parsed_event = self._parser.parse_event(test_event)

    def test_parse_binary_features(self):
        test_event = {
            "name": "Classicla Opera",
            "start_time": "19:30",
            "end_time": "22:30",
            "place": {
                "name": "Philharmonic Society of Trento",
                "location": {
                    "latitude": 46.066723,
                    "longitude": 11.120487,
                },
            },
            "allows_smokers": False,
            "teather": True,
            "cinema": False,
            "museum": False,
            "classical_music_concerts": True,
            "other_concerts": False,
            "sports_show": False,
            "disco": False,
            "monuments": False,
            "do_sports": False,
            "interests": [],
            "politics": False,
            "religion": False,
            "social_activities": False,
            "id": "1532214687109127"
        }
        parsed_event = self._parser.parse_event(test_event)
        features = parsed_event.features

        # allow_smokers
        self.assertIsInstance(features[1], binary_feature.BinaryFeature)
        self.assertEqual(features[1].value, False)

        # teather
        self.assertIsInstance(features[3], binary_feature.BinaryFeature)
        self.assertEqual(features[3].value, True)
