import argparse

def prog_demo():
    # prog: 改变程序名
        # - 使用 `%(prog)s` 引用程序名

    parser = argparse.ArgumentParser(prog='my_progress')
    parser.add_argument('--foo', help='foo of the %(prog)s program')
    parser.parse_args('-h'.split())

def usage_demo():
    # usage: 改变usage 显示信息
    parser = argparse.ArgumentParser(prog='usage_demo', usage='%(prog)s [options] demo')
    parser.add_argument('--foo', nargs='?', help='foo help')
    parser.parse_args('-h'.split())

def description_demo():
    # description:
    parser = argparse.ArgumentParser(description='这个命令是用来显示description信息的')
    parser.parse_args('-h'.split())

def epilog_demo():
    parser = argparse.ArgumentParser(description='这个命令是用来显示description信息的', epilog='显示在参数之后的描述信息')
    parser.parse_args('-h'.split())

def parents_demo():
    # 如果多个解析器可能有相同的参数集， 那么我们可以给他抽取出来， 然后指定parents参数，就是和父类一样的效果
    # 注意：父类的解析器必须得使add_help参数为False

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--parent', type=int, help='父解析器的参数，可被继承')

    foo_parser = argparse.ArgumentParser(parents=[parent_parser])
    foo_parser.add_argument('foo')
    foo_parser.print_help()
    result = foo_parser.parse_args(['--parent', '2', 'xxx'])
    print(result)

def formatter_class_demo():
    # 默认是不能换行的，会将\n变成一个空格
    # parser = argparse.ArgumentParser(description='这个描述不能\n换行啊', epilog='换行\n啊')
    # parser.print_help()

    # 使用这个之后能能换行了
    parser = argparse.ArgumentParser(description='这个描述不能\n换行啊', epilog='换行\n啊', formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.print_help()

def prefix_chars_demo():
    # 一般情况下，我们使用-作为前缀，我们也可以自定义选项前缀。
    parser = argparse.ArgumentParser(prog='prefix_chars', prefix_chars='+')
    parser.add_argument('+f')
    parser.add_argument('++bar')
    result = parser.parse_args(['+f', 'X', '++bar', 'Y'])
    print(result)
    parser.print_help()

def add_help_demo():
    # 是否禁用-h --help选项
    parser = argparse.ArgumentParser(prog='add_help', add_help=False)
    parser.add_argument('--foo', help='foo help')
    parser.print_help()

####################
#   add_argument   #
####################

def name_demo():
    # 可选参数可以少， 位置参数不能少
    parser = argparse.ArgumentParser()
    # 可选参数-a | --age
    parser.add_argument('-a', '--age')
    # 位置参数 name
    parser.add_argument('name')
    result = parser.parse_args(['xxx'])
    print(result)
    result = parser.parse_args(['-a', '18', 'xxx'])
    print(result)
    result = parser.parse_args(['--age', '20', 'xxx'])
    print(result)

def action_demo():
    # 指定命令行参数，内置的有下面几种
    parser = argparse.ArgumentParser()

    # * store: 默认值，仅仅保存参数值，不做处理
    # parser.add_argument('-f', action='store')
    # result = parser.parse_args('-f 1'.split())

    # * store_const: 与store基本一致，但store_const只保存const关键字指定的值
    # parser.add_argument('-f', action='store_const', const=18)
    # result = parser.parse_args('-f'.split())
    # print(result)
    # result = parser.parse_args('-f 18'.split())

    # * store_true | store_true: 与store_const一致，只保存True和False
    # parser.add_argument('-f', action='store_true')
    # parser.add_argument('-b', action='store_false')
    # result = parser.parse_args('-f -b'.split())

    # * append: 将相同参数的不同值保存在一个list中
    # parser.add_argument('-f', action='append')
    # result = parser.parse_args('-f 1 -f 2 -f 3'.split())

    # * count: 统计该词出现的次数
    # parser.add_argument('-verbose', '-v', action='count')
    # 下面两句效果相同
    # result = parser.parse_args('-v -v -v'.split())
    # result = parser.parse_args('-vvv'.split())

    # * help: 输出程序的帮助信息
    # parser.add_argument('-f', action='help')
    # result = parser.parse_args('-f'.split())

    # * version: 输出程序版本信息
    parser = argparse.ArgumentParser(prog='version_demo')
    parser.add_argument('-v', action='version', version='%(prog)s 2.0')
    result = parser.parse_args('-v'.split())

    print(result)

def nargs_demo():
    # 默认一个参数后面只能跟一个值，类似这样-f a -b c,如果一个参数后面跟了多个值，关系就不会对应了，从而程序也会出错。这个时候就可以指定nargs参数了

    parser = argparse.ArgumentParser()

    # * nargs: 为整数
    # parser.add_argument('-f', nargs=2)
    # parser.add_argument('name', nargs=1)
    # result = parser.parse_args('xxx -f a b'.split())

    # * nargs: ?
    #   - 如果给出了参数值，那么就为给出的值，
    #   - 如果没有给出参数值，就会使用const关键字的值，
    #   - 如果不存在这个参数， 将生成默认值
    # parser.add_argument('-age', nargs='?', const='18', default='0')
    # result = parser.parse_args('-age 20'.split())
    # print(result)
    # result = parser.parse_args('-age'.split())
    # print(result)
    # result = parser.parse_args()
    # print(result)

    # * nargs: *
    #   - 将所有的参数保存在列表中
    # parser.add_argument('-f', nargs='*')
    # parser.add_argument('-b', nargs='*')
    # parser.add_argument('names', nargs='*')
    # result = parser.parse_args('xx xxx -f a b -b a b c'.split())

    # * nargs: +
    #   - 将所有的参数保存在列表中，要求至少有一个参数，否则报错
    # parser.add_argument('-f', nargs='+')
    # parser.add_argument('-b', nargs='+')
    # parser.add_argument('names', nargs='+')
    # result = parser.parse_args('xx xxx -f a b -b a b c'.split())

    # nargs: argparse.REMAINDER
    #   - 其余的参数全部保存在一个list中
    parser.add_argument('-f')
    parser.add_argument('-b')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    result = parser.parse_args('-f a -b a b -names xxx xxxx'.split())
    print(result)

def default_demo():
    parser = argparse.ArgumentParser()
    parser.add_argument('-age', default=18)
    result = parser.parse_args()
    print(result)
    result = parser.parse_args('-age 10'.split())
    print(result)

def type_func(value):
    print("type func " + value)
    return value

def type_demo():
    # type 接收到的参数会经过这个函数的处理， 再返回
    parser = argparse.ArgumentParser()
    parser.add_argument('f', type=int)
    parser.add_argument('file', type=type_func)
    result = parser.parse_args('18 temp.txt'.split())
    print(result)

def choices_demo():
    # 将参数的值限定在一个范围内， 超出就报错
    parser = argparse.ArgumentParser()
    parser.add_argument('move', choices=['left', 'middle', 'right'])
    result = parser.parse_args('left'.split())
    print(result)

def required_demo():
    # 指定命令行参数是否必须，默认通过-f --foo指定的额参数为可选参数, 及可以为空
    parser = argparse.ArgumentParser()
    parser.add_argument('--foo', required=True)
    result = parser.parse_args('--foo f'.split())
    print(result)

def dest_demo():
    # 自定义参数的名称
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', '--na')
    parser.add_argument('-a', dest='age')
    parser.add_argument('--gender', '-g')

    result = parser.parse_args('-n xxx -a 18 -g 男'.split())
    print(result)
    result = parser.parse_args('--na xxx -a 18 -g 男'.split())
    print(result)
    result = parser.parse_args('--name xxx -a 18 -g 男'.split())
    print(result)

if __name__ == '__main__':
    add_help_demo()
