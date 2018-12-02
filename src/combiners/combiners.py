from geopy.distance import distance


def DEFAULT_NORMALIZED_COMBINER(value1, value2):
    return 1. - abs(value1 - value2)


def person_location_combiner(person_location, event_location):
    '''Defines a combiner between a person location and an event location

    Args:
        person_location(dict): current, home and work location as keys
        event_location(tuple): (latitude, longitude)
    '''

    current_location = person_location['current_location']
    home_location = person_location['home_location']
    work_location = person_location['work_location']

    current_distance_km = distance(current_location, event_location).km
    home_distance_km = distance(home_location, event_location).km
    work_distance_km = distance(work_location, event_location).km

    distances = [current_distance_km, home_distance_km, work_distance_km]
    # Following parameters should be computed
    max_event_distances = [2, 1, 7]
    weights = [0.5, 0.4, 0.1]

    return sum((dist < max_dist) * weight for dist, max_dist, weight in zip(distances, max_event_distances, weights))


def event_location_combiner(event_location, person_location):
    '''Defines a combiner between an event location and a person location

    Args:
        event_location(tuple): (latitude, longitude)
        person_location(dict): current, home and work location as key
    '''
    return person_location_combiner(person_location, event_location)

#def person_cultural_interest_cobiner(person_interest):
    #pass
