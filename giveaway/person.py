import random
import time

class Person:
    first_name = ''
    last_name = ''
    full_name = ''
    email = ''

    def __init__(self, first_name, last_name, email):
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = first_name + ' ' + last_name
        self.email = email

class HumanizedDelay:

    def __init__(self):
        self._delay = 2.0  # nominal delay value in seconds
        self.noise = 2.0

    def apply(self):
        time.sleep(self.delay + self.noise * random.random())

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, value):
        self._delay = value
        if value == 0:
            self.noise = 0

def readpeoplefile(file):
    with open(file, 'r') as f:
        data = f.readlines()

    data = [line.rstrip('\n') for line in data]

    people = []
    for d in data:
        data_str = d.replace("\n", "")
        [first_name, last_name, email] = data_str.split(' ')
        people.append(Person(first_name, last_name, email))

    random.shuffle(people)
    return people
