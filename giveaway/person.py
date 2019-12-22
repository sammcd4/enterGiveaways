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


def readpeoplefile(file):
    with open(file, 'r') as f:
        data = f.readlines()

    data = [line.rstrip('\n') for line in data]

    people = []
    for d in data:
        data_str = d.replace("\n", "")
        [first_name, last_name, email] = data_str.split(' ')
        people.append(Person(first_name, last_name, email))

    return people
