# Django源码阅读之django.conf.settings对象

在我们平时使用django写项目的时候，如果我们相拥settings.py里面的变量，我们是不是直接导入django.conf.settings这个对象，然后我们就能狗从这个对象里面获取我们想要得到的变量了？并且如果我们想加一下自定义的配置变量，我们也可以自己向settings.py文件里面添加，然后我么在其他位置也能使用django.conf.settings这个对象来获取这些变量。

首先我们知道，py文件就是一个模块，这个文件里面的所有变量，对象，类我们都可以通过module.<变量>来获取。 但是很明显，django不是这样来获取settings.py里面的配置。而是通过django.conf.settings这个对象来获取配置的。

为什么不直接通过module.<变量名>来获取呢？

这是因为django的配置文件不止这一个settings.py文件，这个配置文件使我们可以修改的一个，但是还有一个global_settings.py文件，这个文件的位置在<python第三方包安装路径/django/conf/global_settings.py>，这个文件是我们不可以修改的。而django.conf.settings这个对象里面的属性不仅包含settings.py文件里面的变量，还包含global_settings.py文件里面的变量。

这就是为什么django不直接使用module.<变量名>来获取配置文件里面的变量的原因了。而是使用一个django.conf.settings这个对象来获取。就是为了方便我们能同时获取两个settings.py文件里面的变量。而不用单独导入两个模块来获取。而且如果我们没有阅读过源码，也不知道django还有另外一个global_settings.py文件。这就达到了封装的目的，我们知道怎么使用就可以了，但是不知道内部是怎样实现的。

接下来我们就开始阅读django.conf.settings的源码吧，来看一下django到底是怎样进行封装的。

### 准备工作
* idea: pycharm 2018.2
* django: 2.1
* python: 3.7

### 源码阅读
我们知道，setting这个位置的对象在django.conf包下面，也就是django.conf.__init__.py文件下面，我们先找到这个位置的源码。
```python
settings = LazySettings()
```

我们可以看到，在这个文件的最后面，初始化了一个LazySettings对象，赋值给了settings,所以settings其实就是LazySettings一个实例，我们首先观看LazySettings的__init__函数里面的代码。

然后我们发现LazySettings这个类没有__init__函数，但是它继承了LazyObject这个类，那么我们我们继续跟进到LazyObject这个类的__init__函数中去。

##### LazyObject.__init__()函数
```python
empty = object()

def __init__(self):
    # Note: if a subclass overrides __init__(), it will likely need to
    # override __copy__() and __deepcopy__() as well.
    self._wrapped = empty
```

我们可以看到，在__init__函数中，只是将self._wrapped属性赋值为empty, 而empty只是一个object实例化对象，也相当于什么都没有。

看到这个位置，我们好像还是没有什么眉目，接下来都不知道向什么方向继续阅读源码了。

但是我们想一下， 我么使用setting这个对象的时候，是不是直接使用settings.<变量名>就能够获取对应的值了。但是当目前为止我们好像并没有看到任何一个位置绑定了这些属性？那么我们得到的值是哪里来的呢？

大家知道，在python中有一些魔术方法，会在特定的时候就会执行这些方法。而当我们访问一个对象不存在的变量的时候，其实也会执行一个魔术方法的。

这个魔术方法的名字就是__getattr__, 这个魔术方法的执行条件就是，当我们访问一个不存在的属性的时候，就会调用这个方法。

那么我们接下来就可以找一下这个方法的里面的具体实现代码了啊。

因为我们知道settings是LazySettings对象，首先我们先在这个类里面寻找这个方法。

##### LazySettings.__getattr__函数
```python
empty = object()

def __getattr__(self, name):
    # name 是这个魔术方法的固定签名，也就是settings.<变量>中变量的值
    # 首先判断self._wrapped 是否为 empty
    # 在初始化settings这个对象的时候，我们看到了__init__函数中，就是将self._wrapped这个值赋值为了empty
    # 所以第一次进入这个函数的时候，肯定是满足这个条件的，就会执行self._setup函数代码，传入name参数
    # _setup函数代码我们在下面讲解，大家先阅读了_setup函数的代码之后，再回来继续查看这个位置
    if self._wrapped is empty:
        self._setup(name)
    
    # 在我们看了self._setup函数之后。知道了self._wrapped的值就是一个Settings的实例对象
    # 从self._wrapped对象中获取name变量，这样，我们就得到了对应的值
    val = getattr(self._wrapped, name)
    # 然后将这值添加到self.__dict__这个字典中，也就是给self也绑定这个属性，目的就是缓存
    # 因为只有获取属性没有获取到才执行__getattr__的代码，当我们获取了它的值之后，就绑定了一个属性在这个上面
    # 下次我们再获取这个属性，就不用调用 这个方法了。减少代码的量
    # 为什么添加变量到self.__dict__这个属性中就是增加属性的值呢？这是因为在python中
    # 一个对象的所有属性都存放在self.__dict__这个属性中在，这是一个字典，这也就是为什么python可以动态增减属性的原因了
    self.__dict__[name] = val
    # 返回这个得到的值
    return val
```

##### self._setup函数
```python
import os
ENVIRONMENT_VARIABLE = "DJANGO_SETTINGS_MODULE"

def _setup(self, name=None):
    # os.environ.get(key)函数，从环境变量中得到对应key的值
    # 这里的key是 'DJANGO_SETTINGS_MODULE'
    # 这句代码的意思就是从环境变量中获取 'DJANGO_SETTINGS_MODULE' 的值
    # 在我们运行django项目的时候，django会默认设置这个值为 这个项目下面的settings.py文件
    # settings_module = '<django项目名称>.settings.py'
    settings_module = os.environ.get(ENVIRONMENT_VARIABLE)
    # 如果没有这个环境变量，抛出异常
    if not settings_module:
        # 首先格式化描述信息
        desc = ("setting %s" % name) if name else "settings"
        # 这个异常时django自定义的，大家可以自己点进去查看源码，就是继承了Exception,然后什么都没有做了
        # 里面的参数就是提示信息，相信大家也能看懂了吧
        raise ImproperlyConfigured(
            "Requested %s, but settings are not configured. "
            "You must either define the environment variable %s "
            "or call settings.configure() before accessing settings."
            % (desc, ENVIRONMENT_VARIABLE))
    # 将self._wrapped 对象赋值为 Settings() 这个类的实例对象。接下来我们应该查看Settings.__init__函数里面的代码了
    self._wrapped = Settings(settings_module)
```

##### Settings.__init__()函数
```python

# 这个模块也是一个配置文件，但是我们不嗯呢修改里面的内容，大家可以自己找到这个文件看一下
from django.conf import global_settings
import importlib
import time

DEFAULT_CONTENT_TYPE_DEPRECATED_MSG = 'The DEFAULT_CONTENT_TYPE setting is deprecated.'
FILE_CHARSET_DEPRECATED_MSG = (
    'The FILE_CHARSET setting is deprecated. Starting with Django 3.1, all '
    'files read from disk must be UTF-8 encoded.'
)

def __init__(self, settings_module):
    # settings_module: '<django项目名称>.settings.py'
    # dir函数大家应该知道吧。列出某个对象或模块里面的所有属性的key，是一个列表
    # 这里的global_settings是一个模块（py文件）,就是列出这个文件里面的所有变量，对象，类等等
    # 遍历这个列表
    for setting in dir(global_settings):
        # setting是一个字符串
        # 如果这个字符串全部是大写的
        if setting.isupper():
            # setatter python的内置函数，能给一个对象增加一个属性
            # 第一个参数是增加的对象
            # 第二个参数是key
            # 第三个参数是value
            # 例如 setattr(self, 'a', 'b')
            # 那么 self.a = b
            # getattr() 聪颖对象中获取某个属性的值
            # 下面这句代码就是增加一个setting这个变量的值的属性到self上，设置值为global_setting.<settings>的值
            setattr(self, setting, getattr(global_settings, setting))

    # 这样，就把global_settings.py文件里面所有的配置信息都绑定在self这个对象上了

    # 绑定SETTINGS_MODULE属性， 设置值为settings_module
    self.SETTINGS_MODULE = settings_module

    # importlib.import_module函数，大家也比较熟悉了吧，就是根据字符串导入模块
    mod = importlib.import_module(self.SETTINGS_MODULE)

    # 初始化一个元祖
    tuple_settings = (
        "INSTALLED_APPS",
        "TEMPLATE_DIRS",
        "LOCALE_PATHS",
    )
    # 设置self._explicit_settings为一个空的集合
    self._explicit_settings = set()
    # 这个地方的mod就是我们能改变的那个settings.py文件了，和上面的for循环一样
    # 添加我们的配置信息到self对象上
    for setting in dir(mod):
        # 判断变量名是否全为大写
        if setting.isupper():
            # 得到对应的值
            setting_value = getattr(mod, setting)
            
            # 如果setting在tuple_settings元祖里面，并且对应的值不是列表或元祖
            if (setting in tuple_settings and
                    not isinstance(setting_value, (list, tuple))):
                # 抛出异常，给出提示信息，这几个变量必须是元祖或字典
                raise ImproperlyConfigured("The %s setting must be a list or a tuple. " % setting)
            # 将setting绑定到self上，值为setting_value
            setattr(self, setting, setting_value)
            # 添加setting到这个集合中
            self._explicit_settings.add(setting)

    # 如果没有self.SECRET_KEY这个变量，也就是配置文件中没有这个配置
    # 抛出异常，
    if not self.SECRET_KEY:
        raise ImproperlyConfigured("The SECRET_KEY setting must not be empty.")

    # 这里首先我们先看一下self.is_overridden函数
    # def is_overridden(self, setting):
    #     return setting in self._explicit_settings
    # 也就是判断给定的setting是否在self._explicit_settings中，也就是settings.py文件中
    # 返回True or False
    # 这里就是判断DEFAULT_CONTENT_TYPE在settings.py文件中吗
    if self.is_overridden('DEFAULT_CONTENT_TYPE'):
        # 如果在的话，给出警告，第一个参数是警告的提示信息，第二个参数为警告类型，大家可以自己看一下python 中warning模块的用法，这里就不做详细讲解了。
        # 警告的提示信息的值也在函数上面罗列出来了
        warnings.warn(DEFAULT_CONTENT_TYPE_DEPRECATED_MSG, RemovedInDjango30Warning)
    # 和上面的判断一样。
    if self.is_overridden('FILE_CHARSET'):
        warnings.warn(FILE_CHARSET_DEPRECATED_MSG, RemovedInDjango31Warning)

    # 如果time这个模块有tzset这个属性 并且settings.py文件有TIME_ZONE这个值
    # 在windows下，time是没有tzset这个函数的，只有Unix操作系统才有这个函数
    # 也就是windows下是不会执行这里的代码的， Unix才会执行
    if hasattr(time, 'tzset') and self.TIME_ZONE:
        # pathlib.Path()函数，方便我们对文件目录操作，大家可以自己查看一下这个函数的用法
        # 根据传入的路径，初始化一个对象
        zoneinfo_root = Path('/usr/share/zoneinfo')
        # 根据self.TIME_ZONE的值拼接路径
        # self.TIME_ZONE.split('/')将这个字符串以'/'分割，返回一个列表
        # *[]， 将一个列表打散一个一个的变量
        # 假设self.TIME_ZONE的值为 'Asia/shanghai'
        # 那么 self.TIME_ZONE.split('/') = ['Asia', 'shanghai']
        # *self.TIME_ZONE.split('/') = 'Asia', 'shanghai'
        zone_info_file = zoneinfo_root.joinpath(*self.TIME_ZONE.split('/'))
        # 如果zoneinfo_root文件存在，但是zone_info_file文件不存在，抛出异常
        if zoneinfo_root.exists() and not zone_info_file.exists():
            raise ValueError("Incorrect timezone setting: %s" % self.TIME_ZONE)
        # 更新时区
        os.environ['TZ'] = self.TIME_ZONE
        # 根据环境变量中的时区，重新计算当前时间。
        # 大家可以自己查看一下time.tzset函数的用法，还是挺简单的
        time.tzset()
```

通过上面的代码，相信大家就知道django是通过怎样的方式来获取settings.py或global_settings.py文件中的所有配置了吧。

既然我们读代码读到这里了，还有两个位置我们也说一下，一个是__setattr__函数，一个是__delattr__函数。
* __setattr__(self, name, value): 在我们对这个实例对象设置新值时候，就会默认调用这个函数。 name和value是固定签名。name就是设置的属性的名称，value就是这个属性对应的值。
* __delattr__(self, name): 在我们删除这个属性的时候，就会调用这个函数。name也是这个属性的名称。

### __setattr__()函数

首先我们先查看一下setattr函数的源码。
```python
def __setattr__(self, name, value):
    # 首先我们得知道，在python中，每个对象的所有属性都存放在self.__dict__这个属性里面
    # 这是一个字典，这也就是为什么python可以随时增加和删除属性的原因，
    # 直接增加和删除self.__dict__字典里面的值就可以了

    # 如果name == '_wrapped'，通过上面的代码我们知道，所有的settings的属性都绑定在了self._wrapped这个属性上了    
    if name == '_wrapped':
        # 清空self.__dict__这个字典
        self.__dict__.clear()
    else:
        # 从self.__dict__中删除（弹出）键值对
        self.__dict__.pop(name, None)
    # 调用父类的__setattr__方法
    super().__setattr__(name, value)
```

### super().__setattr__()函数
```python
empty = object()

def __setattr__(self, name, value):
    # 如果name == '_wrapped'
    if name == "_wrapped":
        # 设置这个属性为对应的 value
        self.__dict__["_wrapped"] = value
    else:
        # 首先判断self._wrapped 是否为 empty, 这里和我们__init__函数中的判断一样，也就不多说了
        if self._wrapped is empty:
            # 执行self._setup()函数， 上面我们也对这个函数做了讲解的
            self._setup()
        # 然后调用python的内置函数，setattr()函数， 给self._wrapped对象的name属性设置值为value
        # 这个位置调用setattr()函数的时候， 应该会调用self._wrapped这个对象的__setattr__这个魔术方法
        # 但是这个对象对应的类中并没有编写这个魔术方法，所以就直接设置新值了、
        setattr(self._wrapped, name, value)
```

### __delattr__()函数
```python
def __delattr__(self, name):
    # 首选调用super().__delattr__函数
    super().__delattr__(name)
    # 因为在我们获取了一个settings这个对象里面的值之后，就会将这个值也绑定在自己这个对象中。这点我们可以
    # 从__getattr__方法中可以看出来，这样后面再次获取这个属性的时候，就首先从self.__dict__中获取，如果没有
    # 的话，在去self._wrapped这个对象中获取
    # 所以我们删除这个属性的时候，也要从self.__dict__中将它删除。
    # 如果self.__dict__中没有这个key， 那么使用self.__dict__.pop(name)就会抛出异常，
    # 但是我们可以添加第二个参数，就不会抛出异常了，没有这个key的时候，就会返回第二个参数设置的值
    # 这里就是None。
    self.__dict__.pop(name, None)
```

### super().__delattr__()函数
```python
empty = object()
def __delattr__(self, name):
    # 如果删除的属性为_wrapped
    if name == "_wrapped":
        # 抛出异常， 不能够删除_wrapped
        raise TypeError("can't delete _wrapped.")
    # 这里也是和上面一样的了，就不多说了
    if self._wrapped is empty:
        self._setup()
    # 调用python内置的函数，delattr()，删除对应的属性
    # 这里和上面setattr函数也是一样的，如果这个实例对应的类重写了__delattr__函数
    # 那么就会调用这个魔术函方法，如果没有重写，就会直接删除
    delattr(self._wrapped, name)
``` 

以上就是django中 django.conf.settings 对象的源码理解，通过阅读了它的源码，我们可以知道以下几点：
1. 知道了另外一个配置文件，global_settings.py文件，里面也存放了很多配置信息。
2. 在settings.py文件里面的命名规则，只有全部大写的变量，我们才能够通过django.conf.settings对象获取他
3. 每一个实例对象的所有属性都存在self.__dict__这个字典中
4. 当获取对象的属性时，如果在self.__dict__和self.__class__.__dict__中没有找到这个变量时，就会调用__getattr__这个魔术方法, self.__dict__大家应该知道是什么， 而self.__class__dict其实和self.__dict__差不多，只是存放的是类的相关属性。所以得到一个实例对象的属性时，查找顺序是self.__dict__ > self.__class__.__dict__ > __getattr__ 。
5. 当我们给对象设置新的属性时或者调用setattr()这个内置函数时，就会调用魔术方法__setattr__函数
6. 当我们使用del关键字或者delattr()内置函数删除属性时，就会调用__delattr__魔术方法
