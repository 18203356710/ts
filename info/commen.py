import functools

from flask import session, current_app, g

from info.models import User


def login_required(f):
    @functools.wraps(f)
    def wrapper(*args,**kwargs):
        user_id=session.get('user_id')
        user=None
        if user_id:
            try:
                user=User.query.filter_by(id=user_id).first()
            except Exception as e:
                current_app.logger.error(e)

        g.user=user
        return f(*args,**kwargs)
    return wrapper


