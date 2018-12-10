import unittest
import sys
import os
library_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, library_path + '/../src')
sys.path.insert(0, library_path + '/../tools')

import features_generator
import ero
from ero_person import Person
from ero_event import Event


class TestEventOptimizationAlgorithm(unittest.TestCase):

    def setUp(self):
        self.test_folder = './test/istat/'
        self.generator = features_generator.PeopleFeaturesGenerator(
            './test/istat/person_features.json',
            './test/istat/comparable_features.json')
        self.generator.import_features_distributions_from_folder(
            self.test_folder)

        self.ero = ero.Ero(do_crossover=True)
        ego_node_id = 0
        folder_path = 'test/test_networks/'
        self.ero.import_ego_network(ego_node_id, folder_path)

    def test_optimization(self):
        mmnet = self.ero.mmnet

        number_of_people = mmnet.mmnet.GetModeNetByName("Person").GetNodes()

        features_1 = self.generator.generate_one()
        features_2 = self.generator.generate_one()
        features_3 = self.generator.generate_one()
        features = [features_1, features_2, features_3]

        for person_id in range(number_of_people + 1):
            person_features = features[person_id % len(features)]
            person = Person(person_features, do_mutation=True)
            person.set_features_weights(1.0)
            mmnet.people[person_id] = person

        # Import events after the persons are added to the network
        mmnet.EVENT_PERSON_EDGES_MU = 70
        self.ero.import_events('test/events/events.json')

        events = mmnet.events.values()

        # Save the a-propri event relevances
        event_relevances = {}

        # Estimate which event is the best one for each person
        for person in mmnet.people.values():
            max_fitness = 0
            event_id = None
            for event in events:
                fitness = person.fitness(event)
                if person.fitness(event) > max_fitness:
                    event_id = event.id
                    max_fitness = fitness
            if event_id not in event_relevances:
                event_relevances[event_id] = 1
            else:
                event_relevances[event_id] += 1


        # TODO: Figure out a good iteration count
        mmnet.propagate(20)

        # TODO: Decide on assertions
        # Maybe just check some general ordering like a-priori event order is equal to a-posteriori order
        final_relevances = sorted([event.relevance for event in mmnet.events.values() if event.relevance != 0])

        self.assertEqual(len(mmnet.people.values()), sum(event_relevances.values()))
        #self.assertEqual(sum(final_relevances), len(mmnet.people.values()))

        # Compare the sorted relevances
        self.assertEqual(final_relevances, sorted(event_relevances.values()))

        # Compare the relevances event by event
        for event in mmnet.events.values():
            if event.id in event_relevances:
                self.assertEqual(event.relevance, event_relevances[event.id])
            else:
                self.assertEqual(event.relevance, 0)
