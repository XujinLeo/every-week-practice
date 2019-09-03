# Django源码阅读

我们知道，我们运行一个django项目的时候，需要进入项目的根目录，然后输入命令，`python manage.py runserver`，这样，我们就启动了一个django项目。那么相当于`manage.py`这个文件就是django的入口，我们就这里开始阅读源码吧。

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
* os.environ.setdefault(key,value):首先我们可以简单的理解为os.environ就是一个字典，而这个方法就是如果key不存在os.environ中，anemia就新建一个key这个键，并且值为value，如果存在，什么都不做，返货当前key的值。所以这句代码的意思就是设置`DJANGO_SETTINGS_MODULE`这个环境变量，值为`<当前项目名称.settings>`

接下来就是尝试从django.core.management中导入execute_from_command_line这个函数。如果导入失败，就抛出ImportError这样一个异常。并且给出提示信息，
