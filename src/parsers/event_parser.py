import warnings

from combiners import *
from ero_event import Event
from ero_exceptions import ImportException
from features import *


class EventParser():

    def __init__(self, comparable_features):
        '''Features found in imported comparable_features.json'''
        self.comparable_features = sorted(comparable_features)

    def parse_event(self, event):
        '''Parse event to get comparable features

        Raises:
            ImportException: when the event has no id'''
        event_features = []

        try:
            event_id = self._get_snap_id_from_facebook_event_id(event['id'])
        except KeyError:
            raise ImportException(
                'Trying to import event with no valid id')

        for feature in self.comparable_features:
            try:
                parser_name = '_parse_' + str(feature)
                parser = getattr(self, parser_name)
                event_features.append(parser(event))
            except AttributeError:
                warnings.warn(
                    'No parse function implemented for feature: ' + str(feature))
                event_features.append(empty_feature.empty_feature)

        return Event(event_id, event_features)

    def _parse_location(self, event):
        '''Get the event location

        Returns:
            (latitude,longitude)
        '''
        try:
            location = event['place']['location']
            coordinates = (location['latitude'], location['longitude'])
            return composite_feature.CompositeFeature(coordinates, combiners.event_location_combiner)
        except KeyError:
            return empty_feature.empty_feature

    def _parse_binary_feature(self, event, feature_key):
        '''
        Parse a binary feature

        Returns:
            The binary feature as True or False            
        '''
        try:
            binary_value = event[feature_key]
            return binary_feature.BinaryFeature(1 if binary_value else 0)
        except KeyError:
            return empty_feature.empty_feature        

    def _get_snap_id_from_facebook_event_id(self, fb_event_id):
        '''Shorten id to fit into Snap C++ int

        Params:
            fb_event_id: facebook string event_id
        Return:
            An id that the snap.py library accepts

        TODO:
            A better solution would be to generate ids and store the mapping in
            a dictionary.
        '''
        return int(fb_event_id[:5])

    # Define all the indirections of the binary features
    def _parse_allows_smokers(self, event):
        return self._parse_binary_feature(event, "allows_smokers")

    def _parse_teather(self, event):
        return self._parse_binary_feature(event, "teather")

    def _parse_cinema(self, event):
        return self._parse_binary_feature(event, "cinema")

    def _parse_museum(self, event):
        return self._parse_binary_feature(event, "museum")

    def _parse_classical_music_concerts(self, event):
        return self._parse_binary_feature(event, "classical_music_concerts")

    def _parse_other_concerts(self, event):
        return self._parse_binary_feature(event, "other_concerts")

    def _parse_sports_show(self, event):
        return self._parse_binary_feature(event, "sports_show")

    def _parse_disco(self, event):
        return self._parse_binary_feature(event, "disco")

    def _parse_monuments(self, event):
        return self._parse_binary_feature(event, "monuments")

    def _parse_do_sports(self, event):
        return self._parse_binary_feature(event, "do_sports")

    def _parse_politics(self, event):
        return self._parse_binary_feature(event, "politics")

    def _parse_religion(self, event):
        return self._parse_binary_feature(event, "religion")

    def _parse_social_activities(self, event):
        return self._parse_binary_feature(event, "social_activities")
