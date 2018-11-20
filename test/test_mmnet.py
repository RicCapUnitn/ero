import unittest

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

    def test_get_person_direct_reachable_people_erdos1(self):
        mmnet = self.ero.mmnet
        propagating_node = 4

        # nodes at distance = 1
        erdos1 = frozenset(
            mmnet._get_person_direct_reachable_people(propagating_node))
        expected_erdos1 = frozenset([3, 5, 6, 7, 8, 9])
        self.assertEqual(erdos1, expected_erdos1)

    def test_get_person_direct_reachable_people_erdos2(self):
        mmnet = self.ero.mmnet
        propagating_node = 4

        # nodes at distance = 1
        erdos1 = frozenset(
            mmnet._get_person_direct_reachable_people(propagating_node))

        # nodes at distance = 2
        erdos2 = frozenset()
        for person_id in erdos1:
            erdos2 |= frozenset(
                mmnet._get_person_direct_reachable_people(person_id))
        expected_erdos2 = frozenset([2, 4, 10, 11, 12, 13, 14])
        self.assertEqual(erdos2, expected_erdos2)

    def test_event_direct_reachable_people(self):
        mmnet = self.ero.mmnet
        propagating_node = 4

        # Add event to mmnet
        event_id = 0
        event_mode = mmnet.mmnet.GetModeNetByName("Event")
        event_mode.AddNode(event_id)
        event_to_person_crossnet = mmnet.mmnet.GetCrossNetByName(
            "EventToPerson")
        edge_id = event_to_person_crossnet.AddEdge(event_id, propagating_node)
        mmnet.event_to_person_edges[edge_id] = (event_id, propagating_node)

        reachable_people = frozenset(
            mmnet._get_event_direct_reachable_people(event_id))
        self.assertEqual(reachable_people, frozenset([propagating_node]))

    def test_propagation_single_event_one_iteration(self):
        '''
        Event is linked to the propagating_node only;
        People have same features(only people at distance <=2 are reached)
        Relevance = propagating_node + all nodes at distance <=1
        '''
        mmnet = self.ero.mmnet
        propagating_node = 4
        expected_reached_nodes = 7

        # Add features to network
        person_features = [binary_feature.BinaryFeature(0),
                           normalized_feature.NormalizedFeature(1)]
        event_features = [binary_feature.BinaryFeature(1),
                          normalized_feature.NormalizedFeature(0.5)]
        expected_fitness = 0.5

        person = Person(person_features)
        event_id = 0
        event = Event(event_id, event_features)

        number_of_people = mmnet.mmnet.GetModeNetByName("Person").GetNodes()
        print(number_of_people)
        for person_id in range(number_of_people + 1):
            mmnet.people[person_id] = person

        event_mode = mmnet.mmnet.GetModeNetByName("Event")
        event_mode.AddNode(event_id)
        event_to_person_crossnet = mmnet.mmnet.GetCrossNetByName(
            "EventToPerson")
        edge_id = event_to_person_crossnet.AddEdge(event_id, propagating_node)
        mmnet.event_to_person_edges[edge_id] = (event_id, propagating_node)
        mmnet.events = [event]

        mmnet.propagate()

        self.assertEqual(event.relevance, expected_reached_nodes)

    @unittest.skip('Not Implemented Yet')
    def test_propagation_single_event_multiple_iterations(self):
        raise NotImplementedError

    @unittest.skip('Not Implemented Yet')
    def test_propagation_multiple_events_one_iteration(self):
        raise NotImplementedError

    @unittest.skip('Not Implemented Yet')
    def test_propagation_multiple_events_multiple_iteration(self):
        raise NotImplementedError
