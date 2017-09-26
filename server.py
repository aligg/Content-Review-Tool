"""Content Review Tool AKA CRT"""

from jinja2 import StrictUndefined
from flask import (Flask, jsonify, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension
from model import(connect_to_db, db, Item, Reviewer, Action)
#from seed import grab_comments, auth


app = Flask(__name__)

app.secret_key = "miau"

app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Landing Page / Queue Dashboard"""

    return render_template("homepage.html")


@app.route('/queue')
def queue():
    """Opens the queue and retrieves items for review"""

    comments = Item.query.limit(5).all()

    return render_template("queue.html", comments=comments)


@app.route('/submit')
def submit():
    """Handled submissions from queue and redirects to next page"""

    #this route should: 
    #add comment submitted into db with label
    #redirect user to new batch or home for now


    return redirect('/queue')


@app.route('/add-reviewer')
def new_reviewer():
    """Display form to add a new reviewer"""

    return render_template("add_reviewer.html")


@app.route('/reg-handler', methods=["POST"])
def add_reviewer():
    """Processes form inputs and adds new reviewer to the db"""

    email = request.form.get("email")
    handle = request.form.get("handle")
    password = request.form.get("password")
    is_manager = request.form.get("is_manager")

    reviewer_in_db = Reviewer.query.filter_by(email=email).all()

    if reviewer_in_db == []:
        new_reviewer = Reviewer(email=email, 
                                handle=handle,
                                password=password,
                                is_manager=is_manager)

        db.session.add(new_reviewer)
        flash('New reviewer registered')
    else: 
        flash('This reviewer is already registered')

    db.session.commit()


    return redirect('/')



if __name__ == "__main__":
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(host='0.0.0.0')