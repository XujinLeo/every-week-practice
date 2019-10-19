import time

var = 'hello world'

class TestError(Exception):
    pass

class Test():
    def __init__(self):
        self.__dict__['value'] = 1
        self.value = 1

    def __setattr__(self, key, value):
        if key == 'value':
            value += 100
        self.__dict__[key] = value

    def __delattr__(self, item):
        self.__dict__.pop(item, None)

if __name__ == '__main__':
    test = Test()
    print(test.value)

    del test.aa
    print(test.__dict__)