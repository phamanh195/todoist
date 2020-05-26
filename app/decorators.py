from flask import redirect, url_for
from flask_login import current_user
from functools import wraps


def anonymous_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        
        return view(**kwargs)
    return wrapped_view