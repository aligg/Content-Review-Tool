
from flask_sqlalchemy import SQLAlchemy
import datetime


db = SQLAlchemy()


##############################################################################
#Model definitions

class Item(db.Model):
    """Item reviewed in CRT"""

    __tablename__ = "items"

    item_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    link_id = db.Column(db.String(15), nullable=True)
    body = db.Column(db.String(40000), nullable=False)
    author = db.Column(db.String(15), nullable=True)
    parent = db.Column(db.String(40000), nullable=True)
    submission = db.Column(db.String(100), nullable=True)
    subreddit = db.Column(db.String(100), nullable=True)
    permalink = db.Column(db.String(100), nullable=False)
    controversiality = db.Column(db.Integer, nullable=True)
    upvotes = db.Column(db.Integer, nullable=True)
    downvotes = db.Column(db.Integer, nullable=True)
    #total reviews -> default is 1 assuming add to db upon submit
    #agreement rate
    #last action -> timestamp
    #platform


class Reviewer(db.Model):
    """Reviewer who reviews items in CRT"""

    __tablename__= "reviewers"

    reviewer_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(30), nullable=False)
    handle = db.Column(db.String(20), nullable=False)
    is_manager = db.Column(db.Boolean, nullable=False, default=False)



class Action(db.Model):
    """actions applied by reviewers on items in CRT"""

    __tablename__="actions"

    action_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    item_id = db.Column(db.ForeignKey('items.item_id'))
    reviewer_id = db.Column(db.ForeignKey('reviewers.reviewer_id'))
    time_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow()) #not sure about this
    label_code = db.Column(db.String(5), nullable=False)
    label_applied = db.Column(db.String(30), nullable=False)



##############################################################################
#Helper functions

def connect_to_db(app):
    """Connect the database to app"""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'pstgresql:///tofillin'
    app.config['SQL_ALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ = "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB, Woohoo!"



