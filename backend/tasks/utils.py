import json
from functools import wraps

import numpy as np

from urllib.parse import urlparse


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def required_args(params):
    def inner(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for p in params:
                if not kwargs.get(p):
                    raise ValueError(f'Missing param {p}')

            return func(self, *args, **kwargs)
        return wrapper
    return inner
