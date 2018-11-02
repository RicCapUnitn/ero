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
        with self.assertNotRaises(UserWarning):
            self.ero.import_ego_network(ego_node_id)

    def test_import_ego_network_from_file_not_present(self):
        ego_node_id = -1
        regexp = 'Failed to import ego network:*'
        with self.assertRaises(UserWarning) as warning:
            self.ero.import_ego_network(ego_node_id)
            self.assertRegexpMatches(warning.message, regexp)

    def test_import_ego_networks_folder(self):
        folder_path = 'test/facebook/'
        with self.assertNotRaises(UserWarning):
            self.ero.import_ego_networks_folder(folder_path)
