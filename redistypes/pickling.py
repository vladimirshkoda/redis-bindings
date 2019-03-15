"""Common pickling functions."""

import pickle
from functools import partial


def loads(value):
    """Unpickles value, raises a ValueError in case anything fails."""
    try:
        obj = pickle.loads(value)
    except Exception as e:
        raise ValueError('Cannot unpickle value', e)
    return obj


# Serialize pickle dumps using the highest pickle protocol (binary, by default uses ascii)
dumps = partial(pickle.dumps, protocol=pickle.HIGHEST_PROTOCOL)
