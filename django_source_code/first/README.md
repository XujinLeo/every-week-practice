# Django源码阅读之manager.py文件阅读

我们知道，我们运行一个django项目的时候，需要进入项目的根目录，然后输入命令，`python manage.py runserver`，这样，我们就启动了一个django项目。那么相当于`manage.py`这个文件就是django的入口，我们就这里开始阅读源码吧。

这篇文章可能有点长，因为我实在是找不到可以在哪里分割出来，就全部放在一片文章里面了。

### 准备工作
* idea: pycharm 2018.2
* django: 2.1
* python: 3.7

打开manage.py文件，我么可以看到这个文件里面就只有main函数。
```python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
```

首先使用了os模块设置了环境变量。
* os.environ.setdefault(key,value):首先我们可以简单的理解为os.environ就是一个字典，而这个方法就是如果key不存在os.environ中，anemia就新建一个key这个键，并且值为value，如果存在，什么都不做，返回当前key的值。所以这句代码的意思就是设置`DJANGO_SETTINGS_MODULE`这个环境变量，值为`<当前项目名称.settings>`

接下来就是尝试从django.core.management中导入execute_from_command_line这个函数。如果导入失败，就抛出ImportError这样一个异常。并且给出提示信息。

sys.argv相信大家也知道，就是命令行中输入的命令，以空格分割出来的一个列表，比如说我们的输入的命令为python manage.py runserver, 那么sys.argv的值就为`['<项目的绝对路径>/manage.py', 'runserver']`。

然后将这个值作为参数传入`execute_from_command_line`函数中。

接下来我们看一下这个函数里面的代码。
```python
def execute_from_command_line(argv=None):
    """Run a ManagementUtility."""
    # 实例化对象
    utility = ManagementUtility(argv)
    # 执行该对象的额execute方法
    utility.execute()
```
这个函数里面首先实例化了一个ManagementUtility对象，并且传入参数argv，这里的argv也就是我么上面的sys.argv。

居然是实例化对象，那么就相当于执行ManagementUtility的__init__方法，所以接下来我们查看一下这个方法里面的代码。
```python
def __init__(self, argv=None):
    # 将argv赋值给self.argv 如果argv为None的话， self.argv 的值就为sys.argv[:]。 
    # 这里的argv是有值的，所以就直接是argv的值了，也就是sys.argv
    self.argv = argv or sys.argv[:]
    # 设置prog_name属性。
    self.prog_name = os.path.basename(self.argv[0])
    if self.prog_name == '__main__.py':
        self.prog_name = 'python -m django'
    self.settings_exception = None
```

* os.path.basename(path): 获取文件所处的文件夹,这里的self.argv[0]的值为`<项目的绝对路径>/manage.py`， 所以self.prog_name的值为`<项目的绝对路径>`。肯定不等于`__main__.py`的。 就不会执行if里面的代码了。

对象初始化完成，就会执行execute函数看。接下来我们就去看一下execute函数里面的代码。

```python
def execute(self):
    # 赋值subcommand这个变量为self.argv[1],self.argv就是sys.argv，在__init__函数里面我们可以看到对这个属性的赋值
    # 如果没有self.argv[1]这个值，也就是输入命令为 python manage.py， 那么久赋值为'help'
    try:
        subcommand = self.argv[1]
    except IndexError:
        subcommand = 'help'  # Display help if no arguments were given.

    # Preprocess options to extract --settings and --pythonpath.
    # These options could affect the commands that are available, so they
    # must be processed early.
    
    # 创建一个命令解释器，有关CommandParser的用法可以参考这篇博客
    # https://blog.csdn.net/xujin0/article/details/100591524
    parser = CommandParser(usage='%(prog)s subcommand [options] [args]', add_help=False, allow_abbrev=False)
    # 添加可选参数 settings
    parser.add_argument('--settings')
    # 添加可选参数 pythonpath
    parser.add_argument('--pythonpath')
    # 添加参数args，nargs="*"， 表示除了上面两个我们添加的参数之外，其他所有的参数都会放在args这个列表里面。
    parser.add_argument('args', nargs='*')  # catch-all
    try:
        # parser.parse_known_args 解析 self.argv[2:]的值，也就是解析参数，返回所有add_argument函数添加过的参数的值和其他的值
        # parser.parse_known_args()和parse_args函数效果一样，只是parse_known_args接收多余的参数并不会报错，
        # 而是直接返回一个列表。也就是这个函数会返回一个Namespace对象和列表。Namespace对象就包含了我们add_argument函数添加的所有参数的值
        options, args = parser.parse_known_args(self.argv[2:])
        # 处理默认的参数， 然后我们进入这个函数，它的代码就只有几行
        handle_default_options(options)
        
        # def handle_default_options(options):
        #    如果传入了settings参数，设置环境变量DJANGO_SETTINGS_MODULE的值为settings参数的值
        #    if options.settings:
        #        os.environ['DJANGO_SETTINGS_MODULE'] = options.settings
        #    如果传入pythonpath参数，就添加这个参数的值到sys.path的第一个位置中
        #    sys.path是python搜索模块的路径集，是一个列表。大家可以自己随便写一个代码打印一下这个变量的值。
        #    if options.pythonpath:
        #       sys.path.insert(0, options.pythonpath)
        
    # 捕捉CommandError异常，并忽略    
    except CommandError:
        pass  # Ignore any option errors at this point.

    # 查看settings.py文件里面是否含有INSTALLED_APPS这个变量。
    # 至于为什么settings这个变量就可以得到settings.py文件里面的值，我们后面单独会写一篇博客讲解，这里大家先知道就可以了
    # settings的路径为 from django.conf import settings， 大家也可以自己先查看源码
    # 如果没有这个变量，抛出异常，赋值给self.settings_exception
    try:
        settings.INSTALLED_APPS
    except ImproperlyConfigured as exc:
        self.settings_exception = exc
    except ImportError as exc:
        self.settings_exception = exc

    # 我们只要获取过settings里面的变量，那么这个值就为True,这部分源码也留在settings那一部风再讲。
    # 所以就会执行下面的代码
    if settings.configured:
        # 当我们执行python manager.py runserver 的时候，这个条件肯定满足，就要知心下面的代码
        if subcommand == 'runserver' and '--noreload' not in self.argv:
            # autoreload.check_errors是一个装饰器，然后传入django.setup这个函数作为参数。
            # 这个装饰器的作用就是检查django.setup 函数是否会执行出错，如果出错了，就会抛出异常。   从而执行except里面的代码
            # 其实django.setup函数就是django项目运行钱需要做的一些配置，setup函数功能我们在下面会说到。
            try:
                autoreload.check_errors(django.setup)()
            except Exception:
                # The exception will be raised later in the child process
                # started by the autoreloader. Pretend it didn't happen by
                # loading an empty list of applications.
                # defaultdict, 就是一个初始化一个字典，和普通字典的区别就是如果从字典里面获取没有的key的值，就会得到一个默认的值.
                # 也就是defaultdict函数里面参数的值. OrderedDict 有序字典
                apps.all_models = defaultdict(OrderedDict)
                apps.app_configs = OrderedDict()
                apps.apps_ready = apps.models_ready = apps.ready = True
                # 上面几句代码就是对他们几个参数的赋值

                # Remove options not compatible with the built-in runserver
                # (e.g. options for the contrib.staticfiles' runserver).
                # Changes here require manually testing as described in
                # #27522.
                _parser = self.fetch_command('runserver').create_parser('django', 'runserver')
                _options, _args = _parser.parse_known_args(self.argv[2:])
                for _arg in _args:
                    self.argv.remove(_arg)

        # 如果不满足上面的情况，就直接执行django.setup函数，
        else:
            django.setup()

    # 这个函数里面的代码我暂时也没有看懂，大家知道的可以给我分享一下 ，谢谢
    # 但是这个函数进去之后，遇到第一个判断条件就会直接返回，相当于这个函数什么都没做。所以暂时不影响我们继续阅读源码
    self.autocomplete()

    # 如果子命令为 help
    if subcommand == 'help':
        # 如果命令行后面还跟有--commands参数，执行下面的代码
        # 例如: python manage.py help --commands
        if '--commands' in args:
            sys.stdout.write(self.main_help_text(commands_only=True) + '\n')
        # self.main_help_text函数的代码在下面我们讲解,这个函数就会返回一个字符窜回来，
        # 然后sys.stdout.write就会将返回的字符窜输出在终端
            
        # 如果没有其他参数
        # 例如 'python manager.py' or 'python manager.py help'
        elif not options.args:
            sys.stdout.write(self.main_help_text() + '\n')
        # 如果后面是其他命令参数，就显示盖命令的帮助文档
        # 例如： python manage.py help runserver/migrate 等等
        else:
            self.fetch_command(options.args[0]).print_help(self.prog_name, options.args[0])
    # 如果subcommand==version,或者有--versin的参数，就显示django的版本信息到终端
    elif subcommand == 'version' or self.argv[1:] == ['--version']:
        sys.stdout.write(django.get_version() + '\n')
    # 如果self.argv[1:] 包含--help 或者 -h, 也显示帮助文档
    elif self.argv[1:] in (['--help'], ['-h']):
        sys.stdout.write(self.main_help_text() + '\n')
    # 如果上面都不是，比如runserver, migrate, makemigrations等等， 就执行下面的函数.
    else:
        # 执行fetch_command()函数 然后在这个函数的基础上继续执行run_from_argv函数
        # 那么相当于fetch_commands()函数应该返回了一个包含run_from_argv函数的对象
        # fetch_commands()函数源码我们在下面阅读
        self.fetch_command(subcommand).run_from_argv(self.argv)
```

##### django.setup()函数
找到django.setup的源码，这个函数的大概功能就是注册app， 配置logging
```python
def setup(set_prefix=True):
    from django.apps import apps
    from django.conf import settings
    from django.urls import set_script_prefix
    from django.utils.log import configure_logging

    # 配置logging, 前面我们说到过，settings就能够得到所有settings.py文件里面的变量，但是这个说法其实是有点片面的，
    # 它还能够得到另外一个settings.py文件里面的变量，这个文件的路径为 '<python第三方包存放位置>/django/conf/global_settings.py'
    # 后面我们会单独写一篇博客，为什么settings会有这两个配置文件的值
    # 然后我们可以看到
    #       settings.LOGGING_CONFIG的值为 'logging.config.dictConfig'
    #       settings.LOGGING的值默认为{}, 如果我们在settings.py文件里面配置了LOGGING变量的话，就为LOGGING的值
    #                   这也就是为什么我们配置django logging的时候，需要在settings.py文件里面通过LOGGING变量配置
    # configure_logging函数的代码阅读请看下面
    configure_logging(settings.LOGGING_CONFIG, settings.LOGGING)
    # 设置prefix
    #       settings.FORCE_SCRIPT_NAME的值为 None
    if set_prefix:
        # 所以这里传入set_script_prefix函数的参数为 '/'
        set_script_prefix(
            '/' if settings.FORCE_SCRIPT_NAME is None else settings.FORCE_SCRIPT_NAME
        )
        # set_script_prefix函数具体代码, 这个函数的文件位置为 '<python第三方包存放位置>/django/urls/base.py'
        # 将local()这个对象赋值给_prefixes, local()这个对象包含了本文件里面的所有变量，大家可以自己打印一下这个对象的值
        # _prefixes = local()
        # def set_script_prefix(prefix):
        #    如果prefix不是以'/'结尾，就加一个'/'
        #    if not prefix.endswith('/'):
        #        prefix += '/'
        #    给_prefixes增加一个属性vlue，并且赋值为prefix
        #    _prefixes.value = prefix
        
    # 注册settings里面的app
    # settings.INSTALLED_APPS的值就是我们可以配置的settings文件里面的INSTALLED_APPS的值，也就是我们注册app的位置
    # 具体代码阅读请看下面
    apps.populate(settings.INSTALLED_APPS)
```
### configure_logging()函数
```python
def configure_logging(logging_config, logging_settings):
    # 首先我们知道这两个参数的值分别为：
    #       logging_config：'logging.config.dictConfig'
    #       logging_settings：settings.LOGGING的值，为{}或者我们自己配置的值

    # 这个函数涉及到了logging模块的学习，大家可以参考这篇博客了解logging
    # 'https://blog.csdn.net/xujin0/article/details/100900715'
    if logging_config:
        # import_string函数，望文生义，通过字符串导入模块，
        # 所以其实这个函数就是导入 logging.config.dictConfig 这个函数
        # import_string源码阅读可以查看下面位置
        logging_config_func = import_string(logging_config)

        # 通过DEFAULT_LOGGING这个字典配置logger
        # DEFAULT_LOGGING这个字典的值在这个文件的最上面，大家可以自己查看，这里就没有罗列出来了
        logging.config.dictConfig(DEFAULT_LOGGING)

        # logging_config_func也就是相当于 logging.config.dictConfig这个函数， 也是配置logger
        # 如果我们自己在settings.py文件里面配置了LOGGING这个变量的话，就会执行这个if下面的代码，更新对logger的配置
        if logging_settings:
            logging_config_func(logging_settings)
```
### import_string()函数
这个函数的位置在 '<python第三方包存放位置>/django/utils/module_loading.py' 文件中
```python
from importlib import import_module
def import_string(dotted_path):
    # 通过上面我们对源码的阅读，知道dotted_path的值为'logging.config.dictConfig'
    try:
        # string.rsplit('.', 1) 对字符串从右边以'.'开始分割一次
        # 所以 module_path = logging.config
        # class_name = dictConfig
        module_path, class_name = dotted_path.rsplit('.', 1)
        # 捕捉ValueError的异常，给出提示信息
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    # 通过importlib.import_module() 导入 logging.config 模块
    module = import_module(module_path)

    try:
        # 通过内置的getattr函数得到dictConfig函数，然后返回
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError('Module "%s" does not define a "%s" attribute/class' % (
            module_path, class_name)
        ) from err
```

### app.populate()函数
```python
def populate(self, installed_apps=None):
    # installed_apps 的值为 ：settings.INSTALLED_APPS的值，
    # 大概内容为：INSTALLED_APPS = [
    #                                'django.contrib.admin',
    #                                'django.contrib.auth',
    #                                'django.contrib.contenttypes',
    #                                'django.contrib.sessions',
    #                                'django.contrib.messages',
    #                                'django.contrib.staticfiles',
    #                                '一些自己的app',
    #                            ]

    # 如果这个值为True， 就直接返回，但是最开始初始化这个对象的时候，这个值被设置为了False
    if self.ready:
        return

    # self._lock属性在初始化时被设置为 threading.RLock()
    # 就是一个线程锁，这个锁和threading.Lock()只有一点细微的区别
    # threading.RLock()可以允许多次acquire，只要保证acquire和release成对出现就可以了
    # 而threading.Lock()只允许一次acquire，然后就必须release之后再acquire
    # with语法就是一个上下文管理器，大家有兴趣的可以自己去看一下，这里就不做讲解了
    with self._lock:
        if self.ready:
            return

        # 当一个线程进入这个位置之后，就会设置self.loading = True
        # 如果这个值为True，就会抛出一个RuntimeError的异常，给出提示信息
        # 也就是这个位置同一时刻只有一个线程能进入
        if self.loading:
            raise RuntimeError("populate() isn't reentrant")
        self.loading = True

        # Phase 1: initialize app configs and import app modules.
        # 第一步： 初始化app的配置和导入app的模块
        
        # 上面我们知道installed_apps的值为一系列字符串，
        for entry in installed_apps:
            # 如果entry是AppConfig这个类型的，就直接赋值app_config为entry
            # 但是很明显这里不是，知识一系列的字符串，所以不会执行这里的代码，而是执行else里面的代码
            if isinstance(entry, AppConfig):
                app_config = entry
            else:
            # 调用AppConfig.create函数，将得到的结果赋值给app_config
            # 这里会得到一个AppConfig或者其子类的实例对象
            # AppConfig.create 函数我们在下面讲解
                app_config = AppConfig.create(entry)
            # self.app_config是用来存放每个app的配置信息的
            # key 为 app_config.label
            # value 为 app_config
            # 这点我们可以从下面几句代码可以看出来
            # app_config.label = app_name.rpartition(".")[2]
            # 我们通过阅读AppConfig.create函数可以看出来， 所以app_config.label的值也就是为app的名字
            if app_config.label in self.app_configs:
                # 如果这里面包含了这个key，表示app的名称冲突了，也就是提示说的Application labels 不唯一
                raise ImproperlyConfigured(
                    "Application labels aren't unique, "
                    "duplicates: %s" % app_config.label)

            # 将这个app_config存入self.app_configs字典
            # key 为 app_config.label
            # value 为 app_config
            self.app_configs[app_config.label] = app_config
            # 设置app_config的apps属性为self, 即当前app这个对象
            app_config.apps = self

        # collections.Counter()函数
        # 计算一个序列的相同值出现次数
        counts = Counter(
            app_config.name for app_config in self.app_configs.values())
        # counts.most_common得到次数最多的一个数据，返回对应的值和出现次数
        # 如果count > 1， 就存入这个列表中
        duplicates = [
            name for name, count in counts.most_common() if count > 1]
        # 如果这个duplicates不为空，所以有值出现次数大于一，也就是有重复的app，抛出一个异常
        if duplicates:
            raise ImproperlyConfigured(
                "Application names aren't unique, "
                "duplicates: %s" % ", ".join(duplicates))

        # 设置这个属性的值为True
        self.apps_ready = True

        # Phase 2: import models modules.
        # 第二步， 导入模型相关模块
        # self.app_configs.values 存放了所有的app_config这个对象，
        # 然后依次调用这个对象的import_models()方法, app_config的类又是<python第三方包安装路径>/django/apps/config.py.AppConfig这个类
        # 然后我们在这个类下面找到import_models函数,这个函数里面只有一点点代码，这里就罗列出来直接讲解了
        for app_config in self.app_configs.values():
            app_config.import_models()
        # def import_models(self):   
        #      self.apps就是当前这个app对象，前面代码出我们看到了对每个app_config.apps 赋值为了 self
        #      但是这个apps.all_models在__init__函数里面赋值为了 self.all_models = defaultdict(OrderedDict)
        #      所以每次访问一个不存在的key时，就会新建一个OrderedDict这样一个字典为默认值, key就是app.config.label，就是当前app的名字
        #      self.models = self.apps.all_models[self.label]
        #      module_has_submodule函数，判断self.module这个模块是否含有子模块MODELS_MODULE_NAME
        #      self.module这个属性里面存放了这个app对顶的module
        #      这里的MODELS_MODULE_NAME的值为  'models' 也就是查看每个app下面时候含有models函数
        #      如果有的话，就导入这个模块，并且将这个模块绑定在self.models_module属性中
        #      module_has_submodule函数里面的代码也很简单，主要就是注意一下 importlib.util.find_spec 这个函数， 
        #      这个函数被重命名为了 importlib_find函数，也就是查看能否从一个模块中导入一个子模块，
        #      如果能导入，就返回这个子模块，如果不能，就返回None
        #      对这个函数的更多理解大家可以自己查看一下python importlib.util.find_spec函数的文档
        #      if module_has_submodule(self.module, MODELS_MODULE_NAME):
        #          models_module_name = '%s.%s' % (self.name, MODELS_MODULE_NAME)
        #          self.models_module = import_module(models_module_name)
        
        # 这个函数使用来清除一些测试的缓存的，不影响我们阅读代码，这里就不说了
        self.clear_cache()

        # 设置这个变量为True
        self.models_ready = True

        # Phase 3: run ready() methods of app configs.
        # 第三步： 执行每个app_config的ready函数
        # self.get_app_configs()函数就是返回了self.app_configs.values()
        # 和上面的第二步遍历的对象一样，大家可以自己查看这个函数的源码验证
        # 只是多了一下判断，self.ready这个变量是否为True了，如果不是，抛出异常，给出提示信息 
        # 'Apps aren't loaded yet' : 应用程序还没有加载
        for app_config in self.get_app_configs():
            app_config.ready()
        
        # 设置ready属性为True
        self.ready = True
        # self.ready_event我们在__init__函数中可以看到被初始化为了 threading.Event()
        # 这个对象调用set()方法之后，后面调用wait()的所有线程将会被唤醒
        # 对threading.Event()的理解具体可参考这篇博客https://blog.csdn.net/u012067766/article/details/79734630
        self.ready_event.set()
```

### AppConfig.create()函数
```python
def create(cls, entry):
    """
    Factory that creates an app config from an entry in INSTALLED_APPS.
    这是一个根据settings.INSTALLED_APPS列表来创建对象的工厂函数
    """
    try:
        # 根据字符窜导入模块, 这里的entry就是settings.INSTALLED_APPS里面的每一个值
        module = import_module(entry)

    except ImportError:
        # 如果导入失败，设置module为None
        module = None

        # string.rpartition前面我们见过这个函数了，从右边开始以点开始分割字符窜，值分割一次，返回三个值
        # 分割符前面的， 分割符， 分割符后面的 
        mod_path, _, cls_name = entry.rpartition('.')
        
        # 如果没有这个值， 抛出异常, raise后面什么都没有的话，就会自动引发上下文的异常，这里就是ImportError
        if not mod_path:
            raise

    # try: exception: else结构中，只有try里面的代码没有出错时， 才会执行里面的代码
    else:
        try:
            # module就是我们每一个app， module.default_app_config这个变量我们就需要
            # 去这个包下面的__init__.py文件里面寻找, 我们自己的app下面一般都没有这个变量。
            # 而django自带的app下面都是有这个变量的，如django.contrib.admin, django.contrib.auth这些app
            # 所以这里使用了Try语句
            entry = module.default_app_config
        except AttributeError:
            # 如果没有这个变量的话，直接实例当前类，并返回 ，当前类也就是AppConfig  
            # 大家可以查看这个类的构造函数
            # 第一个参数为 app_name
            # 第二个参数为 app_module
            # 并且分别赋值给了self.name, self.module这两个属性
            return cls(entry, module)
        else:
            # 如果try语句没有出错，也就是有default_app_config这个变量
            # 继续调用rpartition函数，default_app_config是一个字符窜，大家可以自己验证一下
            # default_app_config的变量大概为 'django.contrib.auth.apps.AuthConfig',我们也就以他作为例子
            # 所以 mod_path = 'django.contrib.auth.apps' 
            # cls_name = 'AuthConfig'
            mod_path, _, cls_name = entry.rpartition('.')

    # 根绝mod_path导入module -> django.contrib.auth.apps
    mod = import_module(mod_path)
    try:
        # 得到调用getatter得到default_app_config指定的类
        # 也就是 AuthConfig
        cls = getattr(mod, cls_name)
    except AttributeError:
        # 捕获AttributeError异常
        # 如果module is None, module也就是当前app这个包
        if module is None:
            # mod = <当前这个包>.apps
            # mod.__dict__是一个字典，存放了<当前这个包>.apps模块下面的所有值。类，函数，对象，变量等。
            # 如果满足条件 是type的实例对象，并且是AppConfig的子类，并且不是AppConfig， 就放入这个列表中
            # 这里我们需要注意一点是，什么是type的实例对象？
            # 在python中，每个类我们都可以看做是type的实例对象，所有这个判断条件也就是寻找 '类'
            # sorted大家都知道了吧，就是排序
            candidates = sorted(
                repr(name) for name, candidate in mod.__dict__.items()
                if isinstance(candidate, type) and
                issubclass(candidate, AppConfig) and
                candidate is not AppConfig
            )
            # 如果candidates有值，也就是存在这样的一个类，抛出异常
            # 给出提示信息， <当前这个包>.apps 不包含 <cls_name> 这个类，可以选择的类有:将上面candidates里面的类罗列出来
            if candidates:
                raise ImproperlyConfigured(
                    "'%s' does not contain a class '%s'. Choices are: %s."
                    % (mod_path, cls_name, ', '.join(candidates))
                )
            # 再次执行import_module函数
            import_module(entry)
        else:
            # raise 引发AttributeError异常
            raise

    # 如果 cls不是AppConfig的子类， 抛出异常。
    if not issubclass(cls, AppConfig):
        raise ImproperlyConfigured(
            "'%s' isn't a subclass of AppConfig." % entry)

    try:
        # 获取cls.name这个类属性
        app_name = cls.name
    except AttributeError:
        # 抛出异常， cls必须包含name这个属性
        raise ImproperlyConfigured(
            "'%s' must supply a name attribute." % entry)

    # 确保name属性指定的模块是一个可用的模块
    try:
        # 通过app_name 变量，导入module， 并赋值给app_module
        app_module = import_module(app_name)
    except ImportError:
        # 抛出异常， 不能够导入这个模块， 请核对模块名是否正确
        raise ImproperlyConfigured(
            "Cannot import '%s'. Check that '%s.%s.name' is correct." % (
                app_name, mod_path, cls_name,
            )
        )

    # 返回当前cls的实例化对象, 这里的cls为defaule_app_config指向的类
    # 他是AppConfig的之类，所有构造函数是一样的
    return cls(app_name, app_module)
```

### self.main_help_text()函数

首先找到main_help_text的源码
```python
def main_help_text(self, commands_only=False):
    """Return the script's main help text, as a string."""
    # 如果传入commands_only参数并且为True,就直接调用get_commands函数，
    # get_commands函数会返回一个字典，字典的结构为{'<命令的名称>':'<命令所属的app的名称>'}
    # 然后使用python的内置函数，sorted对字典进行排序,赋值给usage变量.
    # 使用sorted对字典进行排序，默认是对key进行排序，然后返回一个排序好的列表,存放的所有的key
    # get_commands()函数内容也会在下面讲解
    if commands_only:
        usage = sorted(get_commands())
        
    # 如果没有传入commands_only参数或者为False
    else:
        # 初始化usage变量，赋值为一个列表
        usage = [
            "",
            "Type '%s help <subcommand>' for help on a specific subcommand." % self.prog_name, # 这里的self.prog_name的值就为 manage.py
            "",
            "Available subcommands:",
        ]
        # 初始化commands_dict
        # defaultdict函数前面我们已经说过他的用法了，如果key不存在，就设置为默认的值，这里就是 lambda:[]，也就是为一个列表
        commands_dict = defaultdict(lambda: [])
        # 上面我们说到了get_commands返回的是一个字典，这里就是对这个字典进行遍历
        for name, app in get_commands().items():
            if app == 'django.core':
                app = 'django'
            else:
                # string.rpartition('.') 从字符串的右边开始以第一个‘.’分割，得到一个元祖(<.的前面部分>, '.', '.的后面部分')
                # 例如 'django.core.management'.rpartition('.')[-1] 得到的值就为 management
                app = app.rpartition('.')[-1]
            # 将app设置为key， 增加这个key对应列表中的值为name
            # 所以commands_dict 的值大概为这样
            # {'django':['migrate', 'makemigrations', ...],'auth':['createsuperuser', 'changepassowrd', ...], ...}
            # 这个里面就存储了所有的django中的命令
            commands_dict[app].append(name)
        # 获取颜色风格？这里代码我也没看懂，知道的小伙伴可以跟我分享一下
        style = color_style()
        # 对commands_dict中的key进行排序，并遍历
        for app in sorted(commands_dict):
            # 添加一个空字符窜，目的是为了每个app之间有换行
            usage.append("")
            # style.NOTICE()函数我也不知道在做什么，应该是设置传入参数的颜色，知道的小伙伴可以跟我分享一下
            # 但是没关系，也不影响我们继续阅读，我们就可以直接看做 usage.append("[%s]" % app), 就是添加一个这样的字符窜
            usage.append(style.NOTICE("[%s]" % app))
            # 对commands_dict[app]进行排序， 遍历
            for name in sorted(commands_dict[app]):
                # 添加字符窜到usage中
                usage.append("    %s" % name)
        # 如果这个属性不为None，继续将这个属性添加到usage中，这个属性存放了settings模块的异常,前面我们在execute函数中说到过
        if self.settings_exception is not None:
            usage.append(style.NOTICE(
                "Note that only Django core commands are listed "
                "as settings are not properly configured (error: %s)."
                % self.settings_exception))

    # string.join()函数， 将序列中的每一个元素用string拼接起来
    # 这里就是用\n拼接usage列表中的每一个元素，然后返回。
    # 大家可以执行python manage.py help 和 python manage.py help --commands这两条命令
    # 对比着查看的效果一起阅读源码，就会更加清楚了
    return '\n'.join(usage)
```

##### get_commands()函数
找到get_commands的源码
```python
def get_commands():

    # 使用字典生成式初始化一个字典，赋值给commands
    # key是name， value都是'django.core'
    # name 是循环find_commands(__path__[0])这个函数得到的
    # 这里先说一下__path__这个魔术变量
    # 它存放的是当前包的路径，因为当前文件是 '<python第三方包存放路径>/django/core/management/__init__.py'
    # 所以这里的__path__就为 ['<python第三方包存放路径>/django/core/management']
    # 然后我们查看find_commands函数的源码，find_commands源码阅读我放在下面的，
    # 大家可以在下面查看了find_commands函数的源码，再回来继续看这个位置， 就知道commands里面大概是一些什么值了
    # commands = {'runserver':'django.core', 'migrate':'django.core', ... }
    commands = {name: 'django.core' for name in find_commands(__path__[0])}

    # 前面我们说到过，只要访问了settings里面的变量并且没有出现异常，这个值就为True,所以这个歌时候这个值是为True的
    # 也就不会执行里面的代码
    if not settings.configured:
        return commands

    # reversed函数，翻转一个列表，头变尾，尾变头
    # app.get_app_configs()， 获取每个app注册了的app的模块
    # app
    # 然后遍历，这样就能过获取每个注册了的app下面的所有命令了，包括我们自定义的命令
    for app_config in reversed(list(apps.get_app_configs())):
        # 获取每个模块下的management包(文件夹), 得到路径
        # 这也就是为什么我们自定义命令的时候，必须在app下面新建一个management的包了
        path = os.path.join(app_config.path, 'management')
        # 更新commands这个字典，key为name，value为app_config.name
        # 因为这里和上面初始化commands这个字典是用到的方法差不多，这里就不细说了
        commands.update({name: app_config.name for name in find_commands(path)})
    
    return commands
```

##### find_commands函数
```python
import pkgutil

def find_commands(management_dir):
    # 首先通过传入的management_dir拼接路径，比如传入的'<python的第三方包存放位置>/django/core'
    # 得到这个下面的 commands文件夹, 这也是为什么我们自定义命令的时候还需要在<management_dir>下面新建一个commands的包
    command_dir = os.path.join(management_dir, 'commands')
    # 通过标准库pkgutil的iter_modules函数，得到这个包下面所有的模块，
    # 这里首先说一下pkgutil.iter_modules函数的用法.
    # 假设我们传入的参数就为'<python的第三方包存放位置>/django/core/management'
    # 那么我们就可以得到这个包下面所有的模块(py文件), 和包
    # 大家可以自己查看一下'<python的第三方包存放位置>/django/core/management'这个下面有哪些文件，包
    # 其实就是我们常用的runserver.py, migrate.py这些文件
    
    # 下面一句代码可改写为以下代码，就方便理解了
    # _ : 在这里没有什么用户的一个值， 用 '_' 占位方便解包操作
    # name : 模块或包的名字（文件名或文件夹的名字， 没有后缀名）
    # is_pkg : 是否是包，如果是一个包，那么这个值就为True
    # result = []
    # for _, name, is_pkg in pkgutil.iter_modules([command_dir]):
    #   if not is_pkg and not name.startswith('_'):
    #       result.append(name)
    # return result
    # 这样， 就得到这个模块下所有的命令了，也就是py文件的名称
    return [name for _, name, is_pkg in pkgutil.iter_modules([command_dir])
            if not is_pkg and not name.startswith('_')]
```

### self.fetch_command()函数
```python
def fetch_command(self, subcommand):
    # 首先我们知道subcommand参数的值就是我们得到的子命令， 我们可以假设就为runserver
    # get_commands函数前面我们也说过了它的用法，得到所有的命令，返回的是一个字典
    # key 是 命令的名称
    # value 是命令所属的模块，也就是所属app, 都是字符串
    commands = get_commands()
    try:
        # 得到所属app的名字, runserver所属的app的名字为 `django.core`
        app_name = commands[subcommand]
    # 捕获KeyError的异常, 也就是没有这个命令
    except KeyError:
        # os.environ中如果有这个参数, 从settings里面获取一下INSTALLED_APPS变量
        if os.environ.get('DJANGO_SETTINGS_MODULE'):
            settings.INSTALLED_APPS
        else:
        # 如果没有， 打印没有设置下面这一句话, sys.stderr.write标准输出, 和print功能差不多
            sys.stderr.write("No Django settings specified.\n")
        # 获取名称和subcommand相似的命令
        # python标准库：difflib.get_close_matches()函数返回一个最大匹配结果的列表，
        # 第一个参数为需要匹配的字符串，第二个参数匹配的源
        # 这个函数也就是从第二个参数里面找出和第一个字符窜相似的字符窜，并返回一个列表
        # 放在这个位置就是找到和subcommand命令相似的命令.
        possible_matches = get_close_matches(subcommand, commands)
        # 打印 不知道的命令<subcommand>
        sys.stderr.write('Unknown command: %r' % subcommand)
        # 如果找到了一些相似的命令
        if possible_matches:
            # 打印 ：你要执行的命令是否为 possible_matches[0]这个命令
            sys.stderr.write('. Did you mean %s?' % possible_matches[0])
        # 打印 ：可以使用<self.prog_name> help 查看用法
        sys.stderr.write("\nType '%s help' for usage.\n" % self.prog_name)
        # 结束程序
        sys.exit(1)
    # 如果是BaseCommand实例对象
    if isinstance(app_name, BaseCommand):
        # 直接赋值给klass
        klass = app_name
    else:
        # 执行load_command_class函数，返回值赋值给klass， 这个函数也很简单
        klass = load_command_class(app_name, subcommand)
        # def load_command_class(app_name, name):
        #     按照上面的例子 ：app_name的值为django.core
        #     name的值就为subcommand的值 我们假设为runserver
        #     '%s.management.commands.%s' % (app_name, name) 的值就为 'django.core.management.commands.runserver'
        #     module 就是这个模块了   
        #     module = import_module('%s.management.commands.%s' % (app_name, name))
        #     返回module.Command()这个类的实例化对象
        #     return module.Command()
        
    # 返回klass, 所有klass也就是Command的实例化对象
    return klass
```

### fetch_command(suncommad).run_from_argv(sys.argv)函数
```python
def run_from_argv(self, argv):
    # 设置这个变量为True
    self._called_from_command_line = True
    # 调用create_parser函数，这个函数里面就是创建一个argparse.ArgumentParser对象，前面我们已经说过这个的用法了
    # 这里就不说了，里面的代码也很简单，大家可以自己阅读以下
    parser = self.create_parser(argv[0], argv[1])

    # 解析命令行中的参数
    options = parser.parse_args(argv[2:])
    # vars函数，可以吧一个对象的属性变成一个字典
    cmd_options = vars(options)
    # 从字典中获取args这个变量
    args = cmd_options.pop('args', ())
    # 这个函数我们前面也说了它的用法，这里也就不说了
    handle_default_options(options)
    try:
        # 执行self.execute函数，这个函数里面就是每个命令的入口函数了
        # 所以每个函数都不一样，这里就不阅读了，到后面阅读每个命令的具体实现源码的时候，再开始阅读
        self.execute(*args, **cmd_options)
    
    # 捕获异常
    except Exception as e:
        # 抛出异常
        if options.traceback or not isinstance(e, CommandError):
            raise

        # 打印一些提示异常xinx
        if isinstance(e, SystemCheckError):
            self.stderr.write(str(e), lambda x: x)
        else:
            self.stderr.write('%s: %s' % (e.__class__.__name__, e))
        # 结束程序
        sys.exit(1)
    finally:
        try:
            # 关闭一些execute函数中使用过的连接
            connections.close_all()
        except ImproperlyConfigured:
            # Ignore if connections aren't setup at this point (e.g. no
            # configured settings).
            pass
```

以上就是manage.py文件执行的源码了，这里代码的确涉及到很多，这篇文章也有点长，因为我实在是找不到从哪个位置开可以给他们分割出来，就全部写在了这一篇文章里面。

最后，我想说，看源码真的是一件很费神很费力的事情，经常看着看着就不知道自己在哪里了。

如果上面有理解错误的位置，欢迎大家提出来，谢谢大家的阅读。
