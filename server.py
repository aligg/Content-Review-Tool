"""Content Review Tool AKA CRT"""

from jinja2 import StrictUndefined
from flask import (Flask, jsonify, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension
from model import (connect_to_db, db, Item, Reviewer, Action, BadWord)
from datetime import (datetime, date)
from passlib.context import CryptContext
import seed
import re


pwd_context = CryptContext(schemes=["pbkdf2_sha256"],
                                deprecated="auto")

app = Flask(__name__)

app.secret_key = "miau"

app.jinja_env.undefined = StrictUndefined


@app.context_processor
def create_counter():
    """Creates counter showing daily reviews for logged in user with day in UTC"""

    if not session or not ("reviewer id" in session or "handle" in session):
        return dict(rev_count=[])

    sql = """
        select count(action_id)
        from actions
        where reviewer_id = :reviewer_id
        and extract(day from time_created) = :today
        ;
        """
   
    cursor = db.session.execute(sql,
                                {'reviewer_id': session["reviewer id"],
                                'today': date.today().day}
                                )
    rev_count = cursor.fetchall()
    for i in rev_count:
        rev_count = i[0]

    return dict(rev_count=rev_count)
    #need to change time to local for this to work super smoothly, both in db & here


@app.route('/')
def index():
    """Landing Page / Queue Dashboard"""

    session.pop("pickermode", None)
    session.pop("imagemode", None)
    print session

    return render_template("homepage.html")


@app.route('/queue')
def queue():
    """Opens the queue and retrieves items for review"""
    print session, "<-- Huzzah, session"
    item_id_list = [a.item_id for a in Action.query.all()]
    
    if "pickermode" in session:
        comments = Item.query.filter(Item.subreddit==session["pickermode"],db.not_(Item.item_id.in_(item_id_list))).limit(5).all()
    elif "imagemode" in session:
        comments = Item.query.filter(Item.parent=="image",db.not_(Item.item_id.in_(item_id_list))).limit(5).all()
    else:
        comments = Item.query.filter(db.not_(Item.item_id.in_(item_id_list))).limit(5).all() #could change this to allow items to be reviewed by other users up to 3 times

    badwords_list = [w.word for w in BadWord.query.all()]
    badwords = str(badwords_list)
    matches = {}
    
    for item in comments:
        for word in item.body.split():
            r = re.search(r"(?:^|\W)" + re.escape(word) + r"(?:$|\W)", badwords, re.IGNORECASE)   
            if r is None or len(word) < 3:
                continue
            else:
                matches[item.link_id] = word

    return render_template("queue.html", 
                            comments=comments,
                            batchsize = len(comments),
                            matches=matches)

@app.route('/image-queue')
def image_queue():
    """sets up image review """

    session["imagemode"]= "on"

    return redirect("/queue")


@app.route('/picker')
def display_picker():
    """Displays form for reviewer to specify review parameters"""
    print session
    return render_template("picker.html")


@app.route('/picker-handler', methods=["POST"])
def picker_handler():
    """Handles input from picker form, queries reddit API, adds to items db, redirects to queue"""

    subreddit = request.form.get("subreddit")
    sortby = request.form.get("sort")
    timeframe = request.form.get("time")
    session["pickermode"] = subreddit
    reddit = seed.authorize()

    submissions = {}   
    #use if statements for the top one
    for submission in reddit.subreddit(subreddit).top(timeframe, limit=50):
        submission.comment_sort = "new"
        submissions[submission.id] = submission
       
    comments = seed.grab_comments(reddit, submissions)
    seed.load_items(comments)

    return redirect("/queue")


@app.route('/submit', methods=["POST"])
def submit():
    """Handled submissions from queue and redirects to next page"""

    batchsize=int(request.form.get("batchsize"))

    for i in range(1,(batchsize+1)):
        item = request.form.get("item_id-"+str(i))
        labels = request.form.get("label-"+str(i))
        notes = request.form.get("notes-"+str(i))
        reviewer = request.form.get("reviewer_id")
        time_created = datetime.utcnow()

        new_action = Action(item_id=item,
                            reviewer_id=reviewer,
                            time_created=time_created,
                            label_applied=labels,
                            notes=notes)
        db.session.add(new_action)

    db.session.commit()


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
    password_hash = pwd_context.hash(password)
    is_manager = request.form.get("is_manager")

    reviewer_in_db = Reviewer.query.filter_by(email=email).all()

    if reviewer_in_db == []:
        new_reviewer = Reviewer(email=email, 
                                handle=handle,
                                password=password_hash,
                                is_manager=is_manager)

        db.session.add(new_reviewer)
        flash('New reviewer registered')
    else: 
        flash('This reviewer is already registered')

    db.session.commit()


    return redirect('/')

@app.route('/login')
def login_form():
    """Displays login form"""

    return render_template("login_form.html")

@app.route('/login-handler', methods=["POST"])
def login_handler():
    """Handles login form inputs, if valid credentials logs user in and redirects home"""

    handle = request.form.get("handle")
    password = request.form.get("password")

    reviewer=Reviewer.query.filter_by(handle=handle).first()

    if reviewer: 
        if pwd_context.verify(password, reviewer.password):
            session["reviewer id"] = reviewer.reviewer_id
            session["handle"] = reviewer.handle
            flash("You are logged in")
        else:
            flash("Incorrect credentials")
            return redirect("/login")
         
    else:
        flash("Reviewer by that handle does not exist. Ask a manager to create your account.")
        return redirect("/")

    return redirect("/")

@app.route('/logout')
def logout():
    """logs reviewer out & removes id from session"""

    session.pop("reviewer id", None)
    session.pop("handle", None)
    flash("You are now logged out")
    
    return redirect("/")



if __name__ == "__main__":
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(host='0.0.0.0')