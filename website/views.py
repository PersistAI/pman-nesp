from flask import Blueprint

views = Blueprint('views', __name__)

@views.route('/')
def index():
    return render_template('index.html', **config)
