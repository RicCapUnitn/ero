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
        events = {0: Event(0, []),
                  1: Event(1, []),
                  2: Event(2, [])}
        events[0].relevance = 0.5
        events[1].relevance = 0.7
        events[2].relevance = 0.2
        sorted_events = sorted(events.values())
        self.assertEqual(sorted_events[0].id, 2)
        self.assertEqual(sorted_events[1].id, 0)
        self.assertEqual(sorted_events[2].id, 1)
