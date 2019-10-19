
def make_migrations():
    print('make migrations')

class Command():
    def __init__(self):
        self.name = 'make migrations'

    def show_name(self):
        print(self.name)