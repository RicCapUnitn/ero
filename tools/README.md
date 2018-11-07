# Features generation

The features generator takes as input .json files:

- comparable_features
- person_features
- event_features
- features_distributions ('feature_name'\_distribution.json)

## Comparable features

This file is a one level .json file that contains a list of the common features that should be compared when computing the fitness between the event and the person:

> {'features':[..]}

## Person features

This file contains the features that should be used in the computation of the fitness function for a person. This file is a two-level dictionary where the first level features are the same of the ones in the comparable_features.json file. A combiner(missing) should be defined.

> 'fname': 'ftype
> 'fname':{ 'subfeature_name' : 'ftype' , ... }

## Event features

This file contains the features that should be used in the computation of the fitness function for an event. This file is a two-level dictionary where the first level features are the same of the ones in the comparable_features.json file. A combiner(missing) should be defined.

> 'fname': 'ftype
> 'fname':{ 'subfeature_name' : 'ftype' , ... }

## Features distributions

This file contains the features distributions.

````json
"values": [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34],
"distribution": [0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1] ```
````
