import os
import sys
import unittest

library_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, library_path + '/../src')

from features import *
from parsers import *
from ero_event import Event
from combiners import *
from ero_exceptions import ImportException

class TestEventParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._parser = event_parser.EventParser()

    def test_parse_valid_event(self):
        test_event = {
            "place": {
                "name": "CLab Trento",
                "location": {
                    "city": "Trento",
                    "country": "Italy",
                    "latitude": 46.06486,
                    "located_in": "181177785306461",
                    "longitude": 11.1242,
                    "street": "Piazza Fiera, 4",
                    "zip": "38122"
                }
            },
            "id":"2140675796193939"
        }
        parsed_event = self._parser.parse_event(test_event)
        self.assertIsInstance(parsed_event, Event)
        self.assertEqual(len(parsed_event.features), 2)

        age_feature = parsed_event.features[0]
        self.assertIs(age_feature, empty_feature.empty_feature)

        location_feature = parsed_event.features[1]
        expected_location = (46.06486, 11.1242)
        self.assertIsInstance(
            location_feature, composite_feature.CompositeFeature)
        self.assertEqual(location_feature.value, expected_location)
        self.assertIs(location_feature.combiner,
                      combiners.event_location_combiner)

        self.assertEqual(parsed_event.id, int("2140675796193939"[:5]))

    def test_parse_event_missing_location(self):
        test_event = {
            "place": {
                "name": "CLab Trento",
            },
            "id": "2140675796193939"
        }
        parsed_event = self._parser.parse_event(test_event)
        self.assertIsInstance(parsed_event, Event)
        self.assertEqual(len(parsed_event.features), 2)

        age_feature = parsed_event.features[0]
        self.assertIs(age_feature, empty_feature.empty_feature)

        location_feature = parsed_event.features[1]
        self.assertIs(location_feature, empty_feature.empty_feature)

        self.assertEqual(parsed_event.id, int("2140675796193939"[:5]))

    def test_parse_event_missing_id(self):
        test_event = {
            "place": {
                "name": "CLab Trento",
                "location": {
                    "city": "Trento",
                    "country": "Italy",
                    "latitude": 46.06486,
                    "located_in": "181177785306461",
                    "longitude": 11.1242,
                    "street": "Piazza Fiera, 4",
                    "zip": "38122"
                }
            }
        }
        with self.assertRaises(ImportException):
            self._parser.parse_event(test_event)
