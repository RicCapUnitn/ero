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

    @unittest.skip("Not tested")
    def test_one_person_apriori_order_maintanance(self):
        '''Test with 0.edges network that '''
        ego_node_id = 0
        folder_path = 'test/facebook/'
        self.ero.import_ego_network(ego_node_id, folder_path)
        mmnet = self.ero.mmnet

        # generate person with seed 0
        numpy.random.seed(0)

        number_of_people = mmnet.mmnet.GetModeNetByName("Person").GetNodes()
        features = self.generator.generate_one()

        for person_id in range(number_of_people + 100):
            person_features = features
            person = Person(person_features, do_mutation=True)
            mmnet.people[person_id] = person

        # generate events with random seed
        numpy.random.seed(None)

        # Import events after the persons are added to the network
        mmnet.EVENT_PERSON_EDGES_MU = 30
        self.ero.import_events('test/events/events.json')

        # Save the a-propri event relevances
        event_relevances = {event_id: 0. for event_id in mmnet.events.keys()}

        for person in mmnet.people.values():
            for event in mmnet.events.values():
                fitness = person.fitness(event)
                event_relevances[event.id] += fitness

        event_ids_apriori_order = [relevance_tuple[0] for relevance_tuple in sorted(
            event_relevances.items(), key=lambda x: x[1])]

        test_iterations = 5
        for _ in range(test_iterations):

            mmnet.propagate(1, reset_propagation=True)

            for iteration in range(50):
                mmnet.propagate(1, reset_propagation=False)

            event_ids_aposteriori_order = [
                event.id for event in sorted(mmnet.events.values())]

            self.assertEqual(event_ids_apriori_order,
                             event_ids_aposteriori_order)

    def test_convergence_large_network(self):
        '''Test that the algorthm converges on large networks

        Run 10 iterations of the propagation. Than run some iterations till the
        algorithm converges (i.e. execution time starts fluctuating over iterations).
        Run other 10 iterations and check whether the order of the events is
        stable over iterations.
        '''

        folder_path = 'test/facebook/'
        self.ero.import_ego_networks_folder(folder_path)

        mmnet = self.ero.mmnet

        # Make the test reproducible
        numpy.random.seed(0)

        number_of_people = mmnet.mmnet.GetModeNetByName("Person").GetNodes()

        features = self.generator.generate_many(10)

        for person_id in range(number_of_people + 100):
            person_features = features[person_id % len(features)]
            person = Person(person_features, do_mutation=True)
            mmnet.people[person_id] = person

        # generate events with random seed
        numpy.random.seed(None)

        # Import events after the persons are added to the network
        mmnet.EVENT_PERSON_EDGES_MU = 150

        # Save the a-propri event relevances
        event_relevances = {event_id: 0. for event_id in mmnet.events.keys()}

        for person in mmnet.people.values():
            for event in mmnet.events.values():
                fitness = person.fitness(event)
                event_relevances[event.id] += fitness

        event_ids_apriori_order = [relevance_tuple[0] for relevance_tuple in sorted(
            event_relevances.items(), key=lambda x: x[1])]

        # Do the first 10 iterations
        for _ in range(10):
            mmnet.propagate(1, reset_propagation=False)

        previous_iteration_timestamp = time.time()
        previous_iteration_time = 100000
        # Compute convergence starting point
        for iteration in range(40):
            mmnet.propagate(1, reset_propagation=False)
            current_iteration_time = time.time() - previous_iteration_timestamp

            if previous_iteration_time < current_iteration_time:
                break

            previous_iteration_time = time.time() - previous_iteration_timestamp
            previous_iteration_timestamp = time.time()

        # Test converge over the next 10 propagations
        last_iteration_events_order = [
            event.id for event in sorted(mmnet.events.values())]

        for _ in range(10):
            mmnet.propagate(1, reset_propagation=False)
            this_iteration_events_order = [
                event.id for event in sorted(mmnet.events.values())]
            self.assertEqual(last_iteration_events_order,
                             this_iteration_events_order)
            last_iteration_events_order = this_iteration_events_order
