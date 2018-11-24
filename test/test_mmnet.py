import unittest

# Add path in order to import  the library
import sys
import os
library_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, library_path + '/../src')

from contextlib import contextmanager

import ero
from ero_exceptions import ImportException


class TestPeopleImport(unittest.TestCase):
    ''' Test the import of ego networks

    We test for:
        + nodes number
        + edges number
        + circles number
    '''

    def check_ego_network(
            self, expected_number_of_nodes, expected_number_of_edges,
            expected_number_of_circles, expected_number_of_events):

        ero_mmnet = self.ero.mmnet
        snap_mmnet = ero_mmnet.mmnet

        mmnet_number_of_nodes = snap_mmnet.GetModeNetByName(
            'Person').GetNodes()
        self.assertEqual(mmnet_number_of_nodes, expected_number_of_nodes)

        mmnet_number_of_events = snap_mmnet.GetModeNetByName(
            'Event').GetNodes()
        self.assertEqual(mmnet_number_of_events, expected_number_of_events)

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
        expected_number_of_nodes = 334
        expected_number_of_edges = 2852
        expected_number_of_circles = 1
        expected_number_of_events = 0

        with self.assertNotRaises(UserWarning):
            self.ero.import_ego_network(ego_node_id)
            self.check_ego_network(expected_number_of_nodes,
                                   expected_number_of_edges,
                                   expected_number_of_circles,
                                   expected_number_of_events)

    def test_import_ego_network_from_file_not_present(self):
        ego_node_id = -1
        regexp = 'Failed to import ego network:*'
        with self.assertRaises(UserWarning) as warning:
            self.ero.import_ego_network(ego_node_id)
            self.assertRegexpMatches(warning.message, regexp)

    def test_import_ego_networks_folder(self):
        folder_path = 'test/facebook/'
        expected_number_of_nodes = 3963
        expected_number_of_edges = 89176
        expected_number_of_circles = 10
        expected_number_of_events = 0

        with self.assertNotRaises(UserWarning):
            self.ero.import_ego_networks_folder(folder_path)
            self.check_ego_network(expected_number_of_nodes,
                                   expected_number_of_edges,
                                   expected_number_of_circles,
                                   expected_number_of_events)

    def test_import_events(self):
        ego_node_id = 0
        expected_number_of_nodes = 334
        expected_number_of_edges = 2852
        expected_number_of_circles = 1
        expected_number_of_events = 25

        self.ero.import_ego_network(ego_node_id)
        self.ero.import_events('test/events/events.json')
        self.check_ego_network(expected_number_of_nodes,
                                   expected_number_of_edges,
                                   expected_number_of_circles,
                                   expected_number_of_events)

        crossnet_person_to_event = self.ero.mmnet.mmnet.GetCrossNetByName(
            "EventToPerson")
        self.assertNotEqual(crossnet_person_to_event.GetEdges(), 0) # Edge count is random, no exact assertion possible

    def test_get_event(self):
        ego_node_id = 0

        self.ero.import_ego_network(ego_node_id)
        self.ero.import_events('test/events/events.json')
        self.assertIsNotNone(self.ero.mmnet.get_event(19208))

