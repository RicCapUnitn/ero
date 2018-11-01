import unittest

# Add path in order to import  the library
import sys
import os
library_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, library_path + '/../src')

import ero
from ero_exceptions import ImportException


class TestPeopleImport(unittest.TestCase):

    def setUp(self):
        self.ero = ero.Ero()

    def test_import_ego_network_from_file_present(self):
        ego_node_id = 0
        self.ero.import_ego_network(ego_node_id)

    def test_import_ego_network_from_file_not_present(self):
        ego_node_id = -1
        regexp = 'Failed to import ego network:*'
        with self.assertRaises(Warning) as warning:
            self.ero.import_ego_network(ego_node_id)
            self.assertRegexpMatches(warning.message, regexp)
