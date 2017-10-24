"""Content Review Tool AKA CRT"""

from jinja2 import StrictUndefined
from flask import (Flask, jsonify, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension
from model import (connect_to_db, db, Item, Reviewer, Action, BadWord)
from datetime import (datetime, date)
from passlib.context import CryptContext
from sqlalchemy import func
import seed
import re
import dashboard
import numpy
import classifier
import random



pwd_context = CryptContext(schemes=["pbkdf2_sha256"],
                                deprecated="auto")
app = Flask(__name__)
app.secret_key = "miau"
app.jinja_env.undefined = StrictUndefined


@app.context_processor
def create_counter():
    """Creates counter showing daily reviews for logged in user with day in utc time"""

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

    return render_template("homepage.html")


@app.route('/queue')
def queue():
    """Opens the queue and retrieves items for review.
    Assures reviewer doesn't review anything they've reviewed previously,
    that a given item is reviewed 3 times tops,
    and that images are not surfaced in comments queue and vice versa. 
    """
    
    #Create a list of items reviewed by this reviewer previously - these are not fair game
    item_id_list = [a.item_id for a in Action.query.filter(Action.reviewer_id==session["reviewer id"])]

    #Create a list of items reviewed less than four times- these are fair game
    less_than_4 = []
    sql = """   select item_id from (select item_id, count(item_id) as count from actions group by 1 having count(item_id) = 3) as a;"""
    cursor = db.session.execute(sql)
    s = cursor.fetchall()
    for i in range(len(s)):
        numb= int(s[i][0])
        less_than_4.append(numb)

    #Once you're in the queue, display the correct content for the route the reviewer came from
    if "pickermode" in session:
        comments = Item.query.filter(func.lower(Item.subreddit)==session["pickermode"].lower(),db.not_(Item.item_id.in_(item_id_list)),db.not_(Item.item_id.in_(less_than_4))).limit(5).all()
    elif "imagemode" in session:
        comments = Item.query.filter(Item.parent=="image",db.not_(Item.item_id.in_(item_id_list)),db.not_(Item.item_id.in_(less_than_4))).limit(5).all()
    else:
        comments = Item.query.filter(Item.parent == None,db.not_(Item.item_id.in_(item_id_list)),db.not_(Item.item_id.in_(less_than_4))).limit(5).all() 

    #Selecting badwords from db, limiting due to regex throwing errors with non latin characters
    badwords_list = [w.word for w in BadWord.query.filter(BadWord.language == 'en')]
    matches = {}

    #Make a string of badwords separated by pipes adding \b around to indicate whole word checking
    badwords_pattern = r'\b(' + '|'.join(badwords_list) + r')\b'
    list_of_comment_bodies = [word.body.lower() for word in comments]

    #Go through all the badwords and look for them in the comment bodies
    for item in comments:
        res = re.findall(badwords_pattern, item.body.lower(), re.IGNORECASE)
        if len(res) > 0:
            matches[item.link_id] = ', '.join(res)

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
    """Displays form for reviewer to specify review parameters
    Cleans up a file containing subreddits w/ subs over 50k
    Passes 10 random subreddit ideas to the template
    """

    nicerow = ""
    subreddits = []
    for row in open("seeddata/subreddits"):
        row = row.rstrip()
        if row != "" and row[0] not in ('#', "-", "*") and len(row.split()) == 1:
            nicerow = row
            subreddits.append(nicerow)
    surprise = random.sample(subreddits, 10)


    return render_template("picker.html", 
                            surprise=surprise)

def picker_handler_api_helper():
    """live API calls here"""

    subreddit = request.form.get("subreddit")
    sortby = request.form.get("sort")
    timeframe = request.form.get("time")
    session["pickermode"] = subreddit
    reddit = seed.authorize()
    submissions = {}   
    comments = []

    subs = reddit.subreddit(subreddit).top(timeframe, limit=25)
    for submission in subs:
        submission.comment_sort = "new"
        submissions[submission.id] = submission
    
    comments = seed.grab_comments(reddit, submissions)
    print comments

    return comments


@app.route('/picker-handler', methods=["POST"])
def picker_handler():
    """Handles input from picker form, queries reddit API, adds to items db, 
    redirects to queue, if subreddit queried does not exists, passes empty list"""

    try:
        comments = picker_handler_api_helper()
        seed.load_items(comments)
        print comments
    except:
        subs = []

    # if comments == []:
    #     #do something
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


@app.route('/training')
def display_training():
    """Display training info"""

    return render_template("training.html")


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


@app.route('/dashboard')
def display_dash():
    """renders dashboard"""
    
    weekliespp = dashboard.get_table3_data()
    badrules = dashboard.rules_returning_errors()
    clfperformance = classifier.cross_validate()


    return render_template("dashboard.html", 
                            weekliespp=weekliespp,
                            badrules=badrules,
                            clfperformance=clfperformance)


@app.route('/dashboard-line-dailies.json')
def total_dailies_data():
    """return data for total daily reviews table in json format"""

    data_dict = dashboard.get_table1_data()
    
    return jsonify(data_dict)


@app.route('/dashboard-line-agreement.json')
def total_agreement_data():
    """return data for daily agreement rate in json format"""

    data_dict = dashboard.get_table2_data()
    
    return jsonify(data_dict)

@app.route('/insights-dashboard')
def display_insights_dash():
    """renders dashboard"""
    
    safety_information = dashboard.safety_score_maker()

    return render_template("insights_dashboard.html", 
                            safety_information=safety_information)

@app.route('/dashboard-sub-safety-scores.json')
def pass_safety_data_to_chart():
    """return data for the safety scores insights chart in json format"""

    data_dict = dashboard.get_insights_table_data()

    return jsonify(data_dict)


@app.route('/dashboard-automation-rate.json')
def pass_automation_rate_to_chart():
    """return data for the automation rate chart in json format"""

    data_dict = dashboard.automation_rate_chart()

    return jsonify(data_dict)


@app.route('/testing')
def testing():
    """route testing out classifier.py functionality & other things along the way"""

    # classifier.organize_data()
    # classifier.make_vectors()
    # classifier.cross_validate()
    # classifier.classify_a_comment()
    # classifier.heuristic_maker(1)
    # classifier.load_abuse_scores()
    # dashboard.heuristic_classifier(9)
    # dashboard.classifier_performance()
    # dashboard.wrongs_deep_dive()
    dashboard.rules_returning_errors()
    return "123"



if __name__ == "__main__":
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app, "postgresql:///crt")

    # DebugToolbarExtension(app)

    app.run(host='0.0.0.0')




