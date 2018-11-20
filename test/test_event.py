import unittest
import os
import sys


library_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, library_path + '/../src')

import features
from features import *

from ero_event import Event


class TestEvent(unittest.TestCase):

    def test_sorting_by_relevance(self):
        events = [Event(0, []), Event(1, []), Event(2, [])]
        events[0].relevance = 0.5
        events[1].relevance = 0.7
        events[2].relevance = 0.2
        events.sort()
        self.assertEqual(events[0].id, 2)
        self.assertEqual(events[1].id, 0)
        self.assertEqual(events[2].id, 1)
