
def migrate():
    print('migrate')

class Command():
    def __init__(self):
        self.name = 'migrate'

    def show_name(self):
        print(self.name)