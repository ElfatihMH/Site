# tickets/__init__.py
from flask import Blueprint

tickets_bp = Blueprint('tickets', __name__, template_folder='templates')

from . import routes
