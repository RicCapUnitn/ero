import unittest
from operator import add, truediv

# Add path in order to import  the library
import sys
import os
library_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, library_path + '/../src')

from contextlib import contextmanager

import ero
from ero_event import Event
from ero_person import Person
from ero_exceptions import ImportException
from features import *


class TestPeopleImport(unittest.TestCase):
    ''' Test the import of ego networks

    We test for:
        + nodes number
        + edges number
        + circles number
    '''

    def check_ego_network(
            self, expected_number_of_nodes, expected_number_of_edges,
            expected_number_of_circles):

        ero_mmnet = self.ero.mmnet
        snap_mmnet = ero_mmnet.mmnet

        mmnet_number_of_nodes = snap_mmnet.GetModeNetByName(
            'Person').GetNodes()
        self.assertEqual(mmnet_number_of_nodes, expected_number_of_nodes)

        mmnet_number_of_edges = snap_mmnet.GetCrossNetByName(
            'PersonToPerson').GetEdges()
        self.assertEqual(mmnet_number_of_edges, expected_number_of_edges)

        mmnet_number_of_circles = len(ero_mmnet.circles)
        self.assertEqual(mmnet_number_of_circles,
                         expected_number_of_circles)

    def setUp(self):
        self.ero = ero.Ero()

    @contextmanager
    def assertNotRaises(self, exc_type):
        try:
            yield None
        except exc_type:
            raise self.failureException('{} raised'.format(exc_type.__name__))

    def test_import_ego_network_from_file_present(self):

        ego_node_id = 0
        folder_path = 'test/facebook/'
        expected_number_of_nodes = 333
        expected_number_of_edges = 2519
        expected_number_of_circles = 1

        with self.assertNotRaises(UserWarning):
            self.ero.import_ego_network(ego_node_id, folder_path)
            self.check_ego_network(expected_number_of_nodes,
                                   expected_number_of_edges,
                                   expected_number_of_circles)

    def test_import_ego_network_from_file_not_present(self):
        ego_node_id = -1
        folder_path = 'test/facebook/'
        regexp = 'Failed to import ego network:*'
        with self.assertRaises(UserWarning) as warning:
            self.ero.import_ego_network(ego_node_id, folder_path)
            self.assertRegexpMatches(warning.message, regexp)

    def test_import_ego_networks_folder(self):
        folder_path = 'test/facebook/'
        expected_number_of_nodes = 3959
        expected_number_of_edges = 85087
        expected_number_of_circles = 10

        with self.assertNotRaises(UserWarning):
            self.ero.import_ego_networks_folder(folder_path)
            self.check_ego_network(expected_number_of_nodes,
                                   expected_number_of_edges,
                                   expected_number_of_circles)


class TestPropagation(unittest.TestCase):

    def setUp(self):
        self.ero = ero.Ero()

        ego_node_id = 0
        folder_path = 'test/test_networks/'
        self.ero.import_ego_network(ego_node_id, folder_path)

    def test_get_person_direct_reachable_people_distance1(self):
        mmnet = self.ero.mmnet

        propagating_node = 4
        expected_d1_people = frozenset([3, 5, 6, 7, 8, 9])

        d1_people = frozenset(
            mmnet._get_person_direct_reachable_people(propagating_node))

        self.assertEqual(d1_people, expected_d1_people)

    def test_get_person_direct_reachable_people_erdos2(self):
        mmnet = self.ero.mmnet

        propagating_node = 4
        expected_d2_people = frozenset([2, 4, 10, 11, 12, 13, 14])

        d1_people = frozenset(
            mmnet._get_person_direct_reachable_people(propagating_node))

        d2_people = frozenset()
        for person_id in d1_people:
            d2_people |= frozenset(
                mmnet._get_person_direct_reachable_people(person_id))

        self.assertEqual(d2_people, expected_d2_people)

    def test_get_event_direct_reachable_people(self):
        mmnet = self.ero.mmnet
        propagating_node = 4
        expected_reachable_people = frozenset([propagating_node])

        event_id = 0
        event_mode = mmnet.mmnet.GetModeNetByName("Event")
        event_mode.AddNode(event_id)
        event_to_person_crossnet = mmnet.mmnet.GetCrossNetByName(
            "EventToPerson")
        edge_id = event_to_person_crossnet.AddEdge(event_id, propagating_node)
        mmnet.event_to_person_edges[edge_id] = (event_id, propagating_node)

        reachable_people = frozenset(
            mmnet._get_event_direct_reachable_people(event_id))

        self.assertEqual(reachable_people, expected_reachable_people)

    def test_propagation_single_event_one_iteration(self):
        '''
        Event is linked to the propagating_node only;
        People have same features(only people at distance <=2 are reached)
        Relevance = propagating_node + all nodes at distance <=1
        '''
        mmnet = self.ero.mmnet
        propagating_node = 4
        expected_reached_nodes = 14

        person_features = [binary_feature.BinaryFeature(0),
                           normalized_feature.NormalizedFeature(1)]
        event_features = [binary_feature.BinaryFeature(1),
                          normalized_feature.NormalizedFeature(0.5)]

        event_id = 0
        event = Event(event_id, event_features)

        number_of_people = mmnet.mmnet.GetModeNetByName("Person").GetNodes()

        for person_id in range(number_of_people + 1):
            person = Person(person_features)
            person.set_features_weights(1.)
            mmnet.people[person_id] = person

        event_mode = mmnet.mmnet.GetModeNetByName("Event")
        event_mode.AddNode(event_id)
        event_to_person_crossnet = mmnet.mmnet.GetCrossNetByName(
            "EventToPerson")
        edge_id = event_to_person_crossnet.AddEdge(event_id, propagating_node)
        mmnet.event_to_person_edges[edge_id] = (event_id, propagating_node)
        mmnet.events = {event_id: event}

        mmnet.propagate(1)

        self.assertEqual(event.relevance, expected_reached_nodes)

    def test_propagation_single_event_multiple_iterations(self):
        '''
        Event is linked to the propagating_node only;
        People have same features(only people at distance <=2 are reached)
        # iterations
        Relevance = (propagating_node + all nodes at distance <=1) *
        '''
        mmnet = self.ero.mmnet

        iterations = 10
        propagating_node = 4
        expected_reached_nodes_one_iteration = 14
        expected_relevance = expected_reached_nodes_one_iteration * iterations

        person_features = [binary_feature.BinaryFeature(0),
                           normalized_feature.NormalizedFeature(1)]
        event_features = [binary_feature.BinaryFeature(0),
                          normalized_feature.NormalizedFeature(0.)]

        event_id = 0
        event = Event(event_id, event_features)

        number_of_people = mmnet.mmnet.GetModeNetByName("Person").GetNodes()

        for person_id in range(number_of_people + 1):
            person = Person(person_features)
            person.set_features_weights(1.)
            mmnet.people[person_id] = person

        event_mode = mmnet.mmnet.GetModeNetByName("Event")
        event_mode.AddNode(event_id)
        event_to_person_crossnet = mmnet.mmnet.GetCrossNetByName(
            "EventToPerson")
        edge_id = event_to_person_crossnet.AddEdge(event_id, propagating_node)
        mmnet.event_to_person_edges[edge_id] = (event_id, propagating_node)
        mmnet.events = {event_id: event}

        mmnet.propagate(iterations)

        self.assertEqual(event.relevance, expected_relevance)

    def test_propagation_multiple_events_one_iteration_single_overlap(self):
        '''
        Event is linked to the propagating_node only;
        People have same features(only people at distance <=2 are reached)
        Relevance = propagating_node + all nodes at distance <=1
        event_2 prevails on event_1 on node 3
        '''
        mmnet = self.ero.mmnet

        propagating_node_1 = 2
        propagating_node_2 = 4

        expected_reached_nodes_1 = 14
        expected_reached_nodes_2 = 12

        person_features = [binary_feature.BinaryFeature(0),
                           normalized_feature.NormalizedFeature(1)]
        event_features_1 = [binary_feature.BinaryFeature(0),
                            normalized_feature.NormalizedFeature(0.)]
        event_features_2 = [binary_feature.BinaryFeature(0),
                            normalized_feature.NormalizedFeature(0.2)]

        event_id_1 = 0
        event_id_2 = 1
        event_1 = Event(event_id_1, event_features_1)
        event_2 = Event(event_id_2, event_features_2)

        number_of_people = mmnet.mmnet.GetModeNetByName("Person").GetNodes()
        for person_id in range(number_of_people + 1):
            person = Person(person_features)
            person.set_features_weights(1.)
            mmnet.people[person_id] = person

        event_mode = mmnet.mmnet.GetModeNetByName("Event")
        event_mode.AddNode(event_id_1)
        event_mode.AddNode(event_id_2)

        event_to_person_crossnet = mmnet.mmnet.GetCrossNetByName(
            "EventToPerson")
        edge_id_1 = event_to_person_crossnet.AddEdge(
            event_id_1, propagating_node_1)
        edge_id_2 = event_to_person_crossnet.AddEdge(
            event_id_2, propagating_node_2)
        mmnet.event_to_person_edges[edge_id_1] = (
            event_id_1, propagating_node_1)
        mmnet.event_to_person_edges[edge_id_2] = (
            event_id_2, propagating_node_2)
        mmnet.events = {event_id_1: event_1,
                        event_id_2: event_2}

        mmnet.propagate(1)

        self.assertEqual(event_1.relevance, expected_reached_nodes_1)
        self.assertEqual(event_2.relevance, expected_reached_nodes_2)

    def test_propagation_multiple_events_multiple_iteration(self):
        '''
        Event is linked to the propagating_node only;
        People have same features(only people at distance <=2 are reached)

        Since event_2 prevails on event_1 on node 3, relevance is computed as
        << Relevance = propagating_node + all nodes at distance <=1 >> at the
        first iteration, then propagating_node_1 is never propagate again
        (its fitness <= fitness to event_2)
        '''
        mmnet = self.ero.mmnet

        iterations = 10

        expected_relevance_1 = 14 + 2 * (iterations - 1)
        expected_relevance_2 = 12 * iterations

        propagating_node_1 = 2
        propagating_node_2 = 4

        person_features = [binary_feature.BinaryFeature(0),
                           normalized_feature.NormalizedFeature(1)]
        event_features_1 = [binary_feature.BinaryFeature(0),
                            normalized_feature.NormalizedFeature(0.)]
        event_features_2 = [binary_feature.BinaryFeature(0),
                            normalized_feature.NormalizedFeature(0.2)]

        event_id_1 = 0
        event_id_2 = 1
        event_1 = Event(event_id_1, event_features_1)
        event_2 = Event(event_id_2, event_features_2)

        number_of_people = mmnet.mmnet.GetModeNetByName("Person").GetNodes()
        for person_id in range(number_of_people + 1):
            person = Person(person_features)
            person.set_features_weights(1.)
            mmnet.people[person_id] = person

        event_mode = mmnet.mmnet.GetModeNetByName("Event")
        event_mode.AddNode(event_id_1)
        event_mode.AddNode(event_id_2)

        event_to_person_crossnet = mmnet.mmnet.GetCrossNetByName(
            "EventToPerson")
        edge_id_1 = event_to_person_crossnet.AddEdge(
            event_id_1, propagating_node_1)
        edge_id_2 = event_to_person_crossnet.AddEdge(
            event_id_2, propagating_node_2)
        mmnet.event_to_person_edges[edge_id_1] = (
            event_id_1, propagating_node_1)
        mmnet.event_to_person_edges[edge_id_2] = (
            event_id_2, propagating_node_2)
        mmnet.events = {event_id_1: event_1,
                        event_id_2: event_2}

        mmnet.propagate(iterations)

        self.assertEqual(event_1.relevance, expected_relevance_1)
        self.assertEqual(event_2.relevance, expected_relevance_2)
        self.assertIs(mmnet.events[0], event_1)

    def test_propagation_with_mutation_multiple_events(self):
        '''Test whether relevant features emerge when mutating over participants'''
        mmnet = self.ero.mmnet

        iterations = 100

        propagating_node_1 = 1
        propagating_node_2 = 10

        person_features = [binary_feature.BinaryFeature(0),
                           binary_feature.BinaryFeature(0),
                           normalized_feature.NormalizedFeature(0.5)]
        event_features_1 = [binary_feature.BinaryFeature(0),
                            binary_feature.BinaryFeature(1),
                            normalized_feature.NormalizedFeature(0.6)]
        event_features_2 = [binary_feature.BinaryFeature(1),
                            binary_feature.BinaryFeature(0),
                            normalized_feature.NormalizedFeature(0.5)]

        event_id_1 = 0
        event_id_2 = 1
        event_1 = Event(event_id_1, event_features_1)
        event_2 = Event(event_id_2, event_features_2)

        number_of_people = mmnet.mmnet.GetModeNetByName("Person").GetNodes()
        for person_id in range(number_of_people + 1):
            person = Person(person_features, do_mutation=True)
            mmnet.people[person_id] = person

        event_mode = mmnet.mmnet.GetModeNetByName("Event")
        event_mode.AddNode(event_id_1)
        event_mode.AddNode(event_id_2)

        event_to_person_crossnet = mmnet.mmnet.GetCrossNetByName(
            "EventToPerson")
        edge_id_1 = event_to_person_crossnet.AddEdge(
            event_id_1, propagating_node_1)
        edge_id_2 = event_to_person_crossnet.AddEdge(
            event_id_2, propagating_node_2)
        mmnet.event_to_person_edges[edge_id_1] = (
            event_id_1, propagating_node_1)
        mmnet.event_to_person_edges[edge_id_2] = (
            event_id_2, propagating_node_2)
        mmnet.events = {event_id_1: event_1,
                        event_id_2: event_2}

        mmnet.propagate(iterations)

        sum_weights_event1_participants = [0.] * len(person_features)
        sum_weights_event2_participants = [0.] * len(person_features)

        participants1 = 3
        participants2 = 12

        for person in mmnet.people.values():
            if person.best_event is event_1:
                sum_weights_event1_participants = list(
                    map(add, sum_weights_event1_participants, person.features_weights))
            else:
                sum_weights_event2_participants = list(
                    map(add, sum_weights_event2_participants, person.features_weights))

        avg_weights_event1_participants = map(
            lambda x: x / participants1, sum_weights_event1_participants)
        avg_weights_event2_participants = map(
            lambda x: x / participants2, sum_weights_event2_participants)

        default_weight = 0.5

        self.assertGreater(avg_weights_event1_participants[0], default_weight)
        self.assertLess(avg_weights_event1_participants[1], default_weight)
        self.assertGreater(avg_weights_event1_participants[2], default_weight)

        self.assertLess(avg_weights_event2_participants[0], default_weight)
        self.assertGreater(avg_weights_event2_participants[1], default_weight)
        self.assertGreater(avg_weights_event2_participants[2], default_weight)

    def test_reset_propagation(self):
        mmnet = self.ero.mmnet

        person = Person([])
        event = Event(0, [])

        mmnet.people[0] = person
        mmnet.events[0] = event

        person.best_event = event
        person.best_fitness = 0.5
        event.relevance = 4

        mmnet.reset_propagation()

        self.assertEqual(mmnet.people[0].best_event, None)
        self.assertEqual(mmnet.people[0].best_fitness, 0.)
        self.assertEqual(mmnet.events[0].relevance, 0)


class TestEventsImport(unittest.TestCase):

    def setUp(self):
        self.ero = ero.Ero()

    def test_import_events(self):
        ego_node_id = 0
        folder_path = 'test/facebook/'
        expected_number_of_events = 12

        self.ero.import_ego_network(ego_node_id, folder_path)

        # Generate random people to test
        person_features = [binary_feature.BinaryFeature(0),
                           normalized_feature.NormalizedFeature(1)]
        person = Person(person_features)
        for person_id in range(1000):
            self.ero.mmnet.people[person_id] = person

        self.ero.import_events('test/events/events.json')

        ero_mmnet = self.ero.mmnet
        mmnet_number_of_events = ero_mmnet.mmnet.GetModeNetByName(
            'Event').GetNodes()
        self.assertEqual(mmnet_number_of_events, expected_number_of_events)

        crossnet_event_to_person = self.ero.mmnet.mmnet.GetCrossNetByName(
            "EventToPerson")
        # Edge count is random, no exact assertion possible
        self.assertNotEqual(crossnet_event_to_person.GetEdges(), 0)

    def test_get_event(self):
        ego_node_id = 0
        folder_path = 'test/facebook/'
        self.ero.import_ego_network(ego_node_id, folder_path)

        # Generate random people to test
        person_features = [binary_feature.BinaryFeature(0),
                           normalized_feature.NormalizedFeature(1)]
        person = Person(person_features)
        for person_id in range(1000):
            self.ero.mmnet.people[person_id] = person

        self.ero.import_events('test/events/events.json')
        self.assertIsNotNone(self.ero.mmnet.get_event(15322))


class TestMMnet(unittest.TestCase):

    @unittest.skip('Use this test to check what is the minimum number of iterations the algorithm requires to converge')
    def test_iterations_number(self):

        self.ero = ero.Ero()

        ego_node_id = 0
        folder_path = 'test/facebook/'
        self.ero.import_ego_network(ego_node_id, folder_path)

        mmnet = self.ero.mmnet
        iterations = 5

        propagating_node_1 = 207
        propagating_node_2 = 193
        propagating_node_3 = 195

        test_default_thresholds = [0.05, 0.1]
        test_update_rates = [0.1, 0.2, 0.3]
        test_thresholds = []

        number_of_features = 6

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
        print('relevance1: ')
        print(event_1.relevance)
        print('relevance2: ')
        print(event_2.relevance)
        print('relevance3: ')
        print(event_3.relevance)
        print('____________________________________________')
