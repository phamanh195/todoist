from flask import Blueprint
from .forms import LoginForm


auth = Blueprint('auth', __name__)


@auth.app_context_processor
def inject_login_form():
    return dict(login_form=LoginForm())


from . import views, errors