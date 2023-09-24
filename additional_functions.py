from collections import deque
from itertools import islice


def consume(iterator, n):
    deque(islice(iterator, n), maxlen=0)
