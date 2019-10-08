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
