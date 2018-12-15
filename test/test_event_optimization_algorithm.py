from __future__ import print_function

import time
import unittest

import numpy

from eroproject import ero, snap
from tools import features_generator
from eroproject.ero_event import Event
from eroproject.ero_person import Person


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
        folder_path = 'test/facebook/'
        #self.ero.import_ego_network(ego_node_id, folder_path)
        self.ero.import_ego_networks_folder(folder_path)

        # numpy.random.seed(0)

    @unittest.skip("Large network does not work")
    def test_optimization(self):
        start_time = time.time()
        mmnet = self.ero.mmnet

        number_of_people = mmnet.mmnet.GetModeNetByName("Person").GetNodes()

        features = self.generator.generate_many(1)

        print("people features")
        print("--- %s seconds ---" % (time.time() - start_time))

        for person_id in range(number_of_people + 100):
            person_features = features[person_id % len(features)]
            person = Person(person_features, do_mutation=True)
            mmnet.people[person_id] = person

        print("--- %s seconds ---" % (time.time() - start_time))

        # Import events after the persons are added to the network
        mmnet.EVENT_PERSON_EDGES_MU = 50
        self.ero.import_events('test/events/events.json')

        print("events import")
        print("--- %s seconds ---" % (time.time() - start_time))

        # Save the a-propri event relevances
        event_relevances = {event_id: 0 for event_id in mmnet.events.keys()}

        # Estimate which event is the best one for each person
        for person in mmnet.people.values():
            max_fitness = 0
            event_id = None
            for event in mmnet.events.values():
                if event.id not in event_relevances:
                    event_relevances[event.id] = 0

                fitness = person.fitness(event)
                if fitness > max_fitness:
                    event_id = event.id
                    max_fitness = fitness
            event_relevances[event_id] += 1

        event_ids_apriori_order = [relevance_tuple[0] for relevance_tuple in sorted(
            event_relevances.items(), key=lambda x: x[1])]

        print("fitness")
        print("--- %s seconds ---" % (time.time() - start_time))

        prev_iteration = time.time()
        for iteration in range(3):
            mmnet.propagate(1, reset_propagation=False)
            print("iteration: " + str(iteration))
            print("--- %s seconds ---" % (time.time() - prev_iteration))
            prev_iteration = time.time()

        print("propagation")
        print("--- %s seconds ---" % (time.time() - start_time))

        event_ids_aposteriori_order = [
            event.id for event in sorted(mmnet.events.values())]

        print(event_ids_apriori_order, file=open(
            '/home/ric/Desktop/apriori.txt', 'w+'))
        print(event_ids_aposteriori_order, file=open(
            '/home/ric/Desktop/aposteriori.txt', 'w+'))
        print([relevance_tuple[1] for relevance_tuple in sorted(
            event_relevances.items(), key=lambda x: x[1])], file=open(
                '/home/ric/Desktop/apriori.txt', 'a'))
        print([
            event.relevance for event in sorted(mmnet.events.values())], file=open(
                '/home/ric/Desktop/aposteriori.txt', 'a'))

        self.assertEqual(event_ids_apriori_order,
                         event_ids_aposteriori_order)
