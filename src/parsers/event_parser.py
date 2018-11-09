import warnings

from combiners import *
from ero_event import Event
from features import *


class EventParser():

    def __init__(self, comparable_features):
        '''Features found in imported comparable_features.json'''
        self.comparable_features = comparable_features

    def parse_event(self, event):
        '''Parse event to get comparable features'''
        event_features = []

        for feature in self.comparable_features:
            try:
                parser_name = '_parse_' + str(feature)
                parser = getattr(self, parser_name)
                event_features.append(parser(event))
            except AttributeError:
                warnings.warn(
                    'No parse function implemented for feature: ' + str(feature))
                event_features.append(empty_feature.empty_feature)

        return Event(event_features)

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
