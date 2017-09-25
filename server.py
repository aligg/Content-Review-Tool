"""Content Review Tool AKA CRT"""

from jinja2 import StrictUndefined
from flask import (Flask, jsonify, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension
from model import(connect_to_db, db, Item, Reviewer, Action)

app = Flask(__name__)

app.secret_key = "miau"

app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
    """Landing Page / Queue Dashboard"""

    return render_template("homepage.html")




if __name__ == "__main__":
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(host='0.0.0.0')