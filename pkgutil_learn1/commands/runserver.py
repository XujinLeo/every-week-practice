
def migrate():
    print('runserver')

class Command():
    def __init__(self):
        self.name = 'runserver'

    def show_name(self):
        print(self.name)