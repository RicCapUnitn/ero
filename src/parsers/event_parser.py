import warnings

from combiners import *
from ero_event import Event
from features import *
from ero_exceptions import ImportException


class EventParser():

    def __init__(self):
        self.comparable_features = ["age", "location"]

    def parse_event(self, event):
        '''Parse event to get comparable features

        Raises:
            ImportException: when the event has no id'''
        event_features = []
        event_id = -1
        
        try:
            event_id = event['id']
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

        try:
            event_id = event['id']
        except:
            warnings.warn('Event id cannot be parsed.')
            raise
        
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
