import os
import sys
import unittest

library_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, library_path + '/../src')

from operator import add

import ero
import ero_propagation_thresholds as thresholds
from ero_event import Event
from ero_person import Person
from features import *


class TestPropagationThresholds(unittest.TestCase):

    def test_features_count_based_threshold(self):

        self.ero = ero.Ero()

        ego_node_id = 0
        folder_path = 'test/facebook/'
        self.ero.import_ego_network(ego_node_id, folder_path)

        mmnet = self.ero.mmnet
        iterations = 100

        propagating_node_1 = 207
        propagating_node_2 = 193
        propagating_node_3 = 195

        test_default_thresholds = [0.05, 0.1]
        test_update_rates = [0.1, 0.2, 0.3]
        test_thresholds = []

        number_of_features = 6

        for default_threshold in test_default_thresholds:
            for update_rate in test_update_rates:
                test_thresholds.append(thresholds.FeaturesCountBasedPropagationThreshold(
                    number_of_features,
                    default_threshold,
                    update_rate
                ))

        person_features = [binary_feature.BinaryFeature(0),
                           binary_feature.BinaryFeature(0),
                           normalized_feature.NormalizedFeature(0.5),
                           binary_feature.BinaryFeature(0),
                           binary_feature.BinaryFeature(0),
                           normalized_feature.NormalizedFeature(0.5)]
        event_features_1 = [binary_feature.BinaryFeature(0),
                            binary_feature.BinaryFeature(1),
                            normalized_feature.NormalizedFeature(0.6),
                            binary_feature.BinaryFeature(0),
                            binary_feature.BinaryFeature(1),
                            normalized_feature.NormalizedFeature(0.6)]
        event_features_2 = [binary_feature.BinaryFeature(1),
                            binary_feature.BinaryFeature(0),
                            normalized_feature.NormalizedFeature(0.5),
                            binary_feature.BinaryFeature(1),
                            binary_feature.BinaryFeature(0),
                            normalized_feature.NormalizedFeature(0.5)]
        event_features_3 = [binary_feature.BinaryFeature(0),
                            binary_feature.BinaryFeature(0),
                            normalized_feature.NormalizedFeature(0.5),
                            binary_feature.BinaryFeature(0),
                            binary_feature.BinaryFeature(0),
                            normalized_feature.NormalizedFeature(0.5)]

        # e3 >> e2 > e1
        # 6 >> 4 > 3.8

        event_id_1 = 0
        event_id_2 = 1
        event_id_3 = 2
        event_1 = Event(event_id_1, event_features_1)
        event_2 = Event(event_id_2, event_features_2)
        event_3 = Event(event_id_3, event_features_3)

        for person_id in range(350):
            person = Person(person_features, do_mutation=True)
            mmnet.people[person_id] = person

        event_mode = mmnet.mmnet.GetModeNetByName("Event")
        event_mode.AddNode(event_id_1)
        event_mode.AddNode(event_id_2)
        event_mode.AddNode(event_id_3)

        event_to_person_crossnet = mmnet.mmnet.GetCrossNetByName(
            "EventToPerson")
        edge_id_1 = event_to_person_crossnet.AddEdge(
            event_id_1, propagating_node_1)
        edge_id_2 = event_to_person_crossnet.AddEdge(
            event_id_2, propagating_node_2)
        edge_id_3 = event_to_person_crossnet.AddEdge(
            event_id_3, propagating_node_3)
        mmnet.event_to_person_edges[edge_id_1] = (
            event_id_1, propagating_node_1)
        mmnet.event_to_person_edges[edge_id_2] = (
            event_id_2, propagating_node_2)
        mmnet.event_to_person_edges[edge_id_3] = (
            event_id_3, propagating_node_3)
        mmnet.events = {event_id_1: event_1,
                        event_id_2: event_2,
                        event_id_3: event_3}

        for threshold in test_thresholds:
            # Print threshold values
            print('Default threshold: ' + str(threshold.default_threshold))
            print('Update rate: ' + str(threshold.update_rate))
            mmnet.propagation_threshold = threshold

            mmnet.propagate(iterations)

            # Compute and print propagation results
            sum_weights_event1_participants = [0.] * len(person_features)
            sum_weights_event2_participants = [0.] * len(person_features)
            sum_weights_event3_participants = [0.] * len(person_features)

            participants1 = 0
            participants2 = 0
            participants3 = 0

            for person in mmnet.people.values():
                if person.best_event is event_1:
                    sum_weights_event1_participants = list(
                        map(add, sum_weights_event1_participants, person.features_weights))
                    participants1 += 1
                elif person.best_event is event_2:
                    sum_weights_event2_participants = list(
                        map(add, sum_weights_event2_participants, person.features_weights))
                    participants2 += 1
                else:
                    sum_weights_event3_participants = list(
                        map(add, sum_weights_event3_participants, person.features_weights))
                    participants3 += 1

            if participants1 > 0:
                avg_weights_event1_participants = map(
                    lambda x: x / participants1, sum_weights_event1_participants)
            else:
                avg_weights_event1_participants = [0.] * len(person_features)
            if participants2 > 0:
                avg_weights_event2_participants = map(
                    lambda x: x / participants2, sum_weights_event2_participants)
            else:
                avg_weights_event2_participants = [0.] * len(person_features)
            if participants3 > 0:
                avg_weights_event3_participants = map(
                    lambda x: x / participants3, sum_weights_event3_participants)
            else:
                avg_weights_event3_participants = [0.] * len(person_features)

            print('participants1: ' + str(participants1))
            print('participants2: ' + str(participants2))
            print('participants3: ' + str(participants3))
            print('avg_weights_event1_participants: ')
            print(avg_weights_event1_participants)
            print('avg_weights_event2_participants: ')
            print(avg_weights_event2_participants)
            print('avg_weights_event3_participants: ')
            print(avg_weights_event3_participants)
            print('____________________________________________')

            mmnet.reset_propagation()
