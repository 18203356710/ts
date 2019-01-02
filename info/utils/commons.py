from flask import session, current_app, g
from info.models import User
# 定义全局校验用户是否登录(封装检查用户是否登录功能。)
# 思路是:定义一个装饰器,在每个需要登录的页面增加检查用户的功能(在对应视图函数上增加)

# 这里有一个注意点:装饰器会默认改变被装饰函数的__name__的属性为装饰器内层函数的函数引用
# 两种解决办法:
#           第一种是,在内层函数返回之前,用被装饰函数的.__name__(外层函数的形参)赋值给内层函数的.__name__
#                   如下函数:在return上面增加一行,wrapper.__name__ = user.__name__ 即可
#           第二种是:通过一个python自带的标准模块,实现被装饰的参数属性不发生变化,import funtools
import functools


def login_required(users):
    # 第二种方法,内层函数上面使用,参数为外层函数的形参(被装饰函数的引用)
    @functools.wraps(users)
    def wrapper(*args, **kwargs):
        # 一、获取session获取用户id，用来判断用户是否登录,
        #    这里也可以使用redis的get，但是太麻烦了，要知道redis的键，因为键比较长
        #    session简单一点,他用什么存的，就用它获取
        user_id = session.get('user_id')
        user = None
        # 判断用户是否存在,如果存在,查询数据库的用户id
        if user_id:
            try:
                user = User.query.filter_by(id=user_id).first()
            except Exception as e:
                current_app.logger.error(e)
                user = None
        # 使用应用上下文变量g，用来传递数据,把查询到的用户数据，使用g变量传递给视图函数
        g.user = user
        # 第一种解决装饰器装饰函数的问题
        # 在返回内部函数之前，把被装饰的函数的函数的__name__属性赋值该内部函数的__name__属性
        # wrapper.__name__ = user.__name__
        return users(*args, **kwargs)

    return wrapper
