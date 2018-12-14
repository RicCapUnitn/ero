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
import snap

class TestEventOptimizationAlgorithm(unittest.TestCase):

    def setUp(self):
        self.test_folder = './test/istat/'
        self.generator = features_generator.PeopleFeaturesGenerator(
            './test/istat/person_features.json',
            './test/istat/comparable_features.json')
        self.generator.import_features_distributions_from_folder(
            self.test_folder)

        self.ero = ero.Ero(do_crossover=True)
        folder_path = 'test/facebook/'
        self.ero.import_ego_networks_folder(folder_path)

    @unittest.skip("Large network does not work")
    def test_optimization(self):
        mmnet = self.ero.mmnet

        number_of_people = mmnet.mmnet.GetModeNetByName("Person").GetNodes()

        features_1 = self.generator.generate_one()
        features_2 = self.generator.generate_one()
        features_3 = self.generator.generate_one()
        features = [features_1, features_2, features_3]

        person_nodes = mmnet.mmnet.GetModeNetByName("Person").Nodes()
        person_counter = 0
        for node in person_nodes:
            person_id = node.GetId()
            #print(person_counter,person_id)
            person_features = features[person_counter % len(features)]
            person = Person(person_features, do_mutation=True)
            person.set_features_weights(1.0)
            mmnet.people[person_id] = person
            person_counter += 1

        # Import events after the persons are added to the network
        mmnet.EVENT_PERSON_EDGES_MU = 500
        self.ero.import_events('test/events/events.json')

        events = mmnet.events.values()

        # Save the a-propri event relevances
        event_relevances = {}

        # Estimate which event is the best one for each person
        for person in mmnet.people.values():
            max_fitness = 0
            event_id = None
            for event in events:
                if event.id not in event_relevances:
                    event_relevances[event.id] = 0
                fitness = person.fitness(event)
                if fitness > max_fitness:
                    event_id = event.id
                    max_fitness = fitness
            event_relevances[event_id] += 1

        a_priori_relevance_order = [relevance_tuple[0] for relevance_tuple in sorted(event_relevances.items(), key=lambda x: x[1])]
        
        mmnet.propagate(20)

        # Rewrite the a-posteori event relevances into a dictionaty like the a-priori relevances
        final_relevances = {}
        for event in mmnet.events.values():
            final_relevances[event.id] = event.relevance

        # Save the a-posteori dictionary like the a-priori dictionary to have a equal order in case of multiple events with the same relevance
        a_posteory_relevance_order = []
        final_relevance_order = [relevance_tuple[0] for relevance_tuple in sorted(final_relevances.items(), key=lambda x: x[1])]

        self.assertEqual(a_priori_relevance_order, final_relevance_order)
