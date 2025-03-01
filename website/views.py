from flask import Blueprint, render_template, current_app

views = Blueprint('views', __name__)

@views.route('/')
def index():
    return render_template('index.html', **current_app.config)
