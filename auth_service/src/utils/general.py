import random
import string


def make_random_string():
    return ''.join(random.sample(string.ascii_lowercase + string.digits, 10))
