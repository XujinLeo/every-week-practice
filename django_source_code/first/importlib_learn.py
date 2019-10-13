
# import sys
# from test import a
# from importlib.util import find_spec
#
# module = find_spec('test.a1')
#
# if module:
#     print(module.__dict__)
# else:
#     print('None')

try:
    a = 1 / 0
except:
    print('0 不能被整除')
    # 自动引发上下文异常
    raise


