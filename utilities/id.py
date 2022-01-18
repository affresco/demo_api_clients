import random
import string


def generate_id(length=6):
    id_ = ''.join(random.choice(string.digits + string.ascii_lowercase + string.digits + string.ascii_uppercase + string.digits) for i in range(length))
    return str(id_).title()