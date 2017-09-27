
from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

##############################################################################
#Model definitions

class Item(db.Model):
    """Item reviewed in CRT"""

    __tablename__ = "items"

    item_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    link_id = db.Column(db.String(30), nullable=True)
    body = db.Column(db.String(40000), nullable=False)
    author = db.Column(db.String(30), nullable=True)
    submission = db.Column(db.String(200), nullable=True)
    subreddit = db.Column(db.String(200), nullable=True)
    permalink = db.Column(db.String(200), nullable=False)
    controversiality = db.Column(db.Integer, nullable=True)
    upvotes = db.Column(db.Integer, nullable=True)
    downvotes = db.Column(db.Integer, nullable=True)
    parent = db.Column(db.String(40000), nullable=True)
    
    def __repr__(self):
        """Prettify printed output"""

        return "<Item item_id=%s link_id=%s>" % (self.item_id, self.link_id)


class Reviewer(db.Model):
    """Reviewer who reviews items in CRT"""

    __tablename__= "reviewers"

    reviewer_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(30), nullable=False)
    handle = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    is_manager = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        """Prettify printed output"""

        return "<Reviewer reviewer_id=%s handle=%s>" % (self.reviewer_id, self.handle)



class Action(db.Model):
    """actions applied by reviewers on items in CRT"""

    __tablename__="actions"

    action_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    item_id = db.Column(db.ForeignKey('items.item_id'))
    reviewer_id = db.Column(db.ForeignKey('reviewers.reviewer_id'))
    time_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow()) #not sure about this
    label_code = db.Column(db.String(5), nullable=False)
    label_applied = db.Column(db.String(30), nullable=False)

    #Define relationships to other tables
    reviewer = db.relationship("Reviewer", backref=db.backref("actions", order_by=time_created)) #curious if you can add in desc here & line below 
    item = db.relationship("Item", backref=db.backref("actions", order_by=time_created))
    

    def __repr__(self):
        """Prettify printed output"""

        return "<Action action_id=%s label_code=%s item_id=%s reviewer_id=%s" % (self.action_id, self.label_code, 
                                                                                self.item_id, self.reviewer_id)


##############################################################################
#Helper functions

def connect_to_db(app):
    """Connect the database to app"""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///crt'
    app.config['SQL_ALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    db.drop_all()
    db.create_all()
    print "Connected to DB, Woohoo!"



