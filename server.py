"""Content Review Tool AKA CRT"""

from jinja2 import StrictUndefined
from flask import (Flask, jsonify, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension
from model import (connect_to_db, db, Item, Reviewer, Action, BadWord)
from datetime import (datetime, date)
from passlib.context import CryptContext
import seed
import re
import dashboard
import numpy
import classifier


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
    print session

    return render_template("homepage.html")


@app.route('/queue')
def queue():
    """Opens the queue and retrieves items for review.

    Assures reviewer doesn't review anything they've reviewed previously, that a given item is reviewed 3 times tops, and that images are not surfaced in comments queue and vice versa. 

    """
    
    item_id_list = [a.item_id for a in Action.query.filter(Action.reviewer_id==session["reviewer id"])]

    less_than_4 = []
    sql = """   select item_id from (select item_id, count(item_id) as count from actions group by 1 having count(item_id) = 3) as a;"""
    cursor = db.session.execute(sql)
    s = cursor.fetchall()

    for i in range(len(s)):
        numb= int(s[i][0])
        less_than_4.append(numb)

    
    if "pickermode" in session:
        comments = Item.query.filter(Item.subreddit==session["pickermode"],db.not_(Item.item_id.in_(item_id_list)),db.not_(Item.item_id.in_(less_than_4))).limit(5).all()
    elif "imagemode" in session:
        comments = Item.query.filter(Item.parent=="image",db.not_(Item.item_id.in_(item_id_list)),db.not_(Item.item_id.in_(less_than_4))).limit(5).all()
    else:
        comments = Item.query.filter(Item.parent == None,db.not_(Item.item_id.in_(item_id_list)),db.not_(Item.item_id.in_(less_than_4))).limit(5).all() 

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

    link_ids = []
    for item in comments:
        link_ids.append(item.link_id)

    link_ids = tuple(link_ids)
    
###########################One idea###################################
    # sql = """ select word 
    #         from badwords 
    #         where word in (select body from items where link_id in :link_ids)
    # """
    # cursor = db.session.execute(sql,
    #                             {'link_ids': link_ids}
    #                             )
    # output = cursor.fetchall()

###########################Second idea###################################
    # sql = """select word
    #         from badwords
    #         where :comment like '%word%'

    # """

    # cursor = db.session.execute(sql, 
    #                             {'comment' : 'i am a fuck fuck'}
    #                             )
    # output= cursor.fetchall()

###########################Third idea###################################
    # list_of_comment_bodies = [word.body.lower() for word in comments]
  
    # for badword in badwords_list:
    #     if badword.lower() in list_of_comment_bodies:
    #         print "Found badword", badword
    #     else:
    #         continue
    # #     for comment in list_of_comment_bodies:


    # print "             "
    # print "Link ID tuple", link_ids
    # print "             "
    # print "Output", output
    # print "       "
    


    #what I really want to do is check if any term in badwords can be found anywhere in comment body.
    #currently what I am doing is checking if any word in the comment can be found in a list of badwords
    #problems: // job triggers off of blow job // fuck. does not trigger off of fuck //^I ^am ^a ^bot will not find itself // not picking up if multiple badwords in string 
    #I want to be able to find multiple badwords as well. 


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
    safety_information = dashboard.safety_score_maker()

    return render_template("dashboard.html", weekliespp=weekliespp)


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


@app.route('/testing')
def testing():
    """route testing out classifier.py functionality & other things along the way"""

    # classifier.organize_data()
    # classifier.make_vectors()
    # classifier.cross_validate()
    dashboard.heuristic_maker()

    return "123"



if __name__ == "__main__":
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app, "postgresql:///crt")

    DebugToolbarExtension(app)

    app.run(host='0.0.0.0')




