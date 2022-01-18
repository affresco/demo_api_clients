import string
import random


def __id(letters=3, numbers=7):
    begin = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(letters))
    end = ''.join(random.SystemRandom().choice(string.digits) for _ in range(numbers))
    return begin + end


def message_id():
    return __id(letters=3, numbers=7)


def client_id():
    return __id(letters=2, numbers=5)
