
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
    submission = db.Column(db.String(300), nullable=True)
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
    password = db.Column(db.String(100), nullable=False)
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
    time_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    label_applied = db.Column(db.String(30), nullable=False)
    notes = db.Column(db.String(100), nullable=True)

    #Define relationships to other tables
    reviewer = db.relationship("Reviewer", backref=db.backref("actions", order_by=time_created)) 
    item = db.relationship("Item", backref=db.backref("actions", order_by=time_created))
    

    def __repr__(self):
        """Prettify printed output"""

        return "<Action action_id=%s label_applied=%s item_id=%s reviewer_id=%s>" % (self.action_id, self.label_applied, 
                                                                                self.item_id, self.reviewer_id)


class BadWord(db.Model):
    """bad words highlighted in tool"""

    __tablename__= "badwords"

    word_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    word = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(10), nullable=True)
    category = db.Column(db.String(50), default="profanity", nullable=True)

    def __repr__(self):
        """Prettify printed output"""

        return "<Word word_id=%s word=%s>" % (self.word_id, self.word)


##############################################################################
#Helper functions & example data for testing

def example_data():
    """Create some sample data."""

    Action.query.delete()
    Item.query.delete()
    Reviewer.query.delete()


    reviewer = Reviewer(reviewer_id=1, email="ali.glenesk@gmail.com", handle="alig", password="password", is_manager=True)
    rev2 = Reviewer(reviewer_id=2, email="miau@gmail.com", handle="miau", password="miau", is_manager=False)

    item = Item(item_id=1, link_id="123", body="I LOVE TO POST ON REDDIT", 
                author="redditor", submission="subtest", subreddit="news",
                permalink="/r/news/comments/73xmht/officials_us_to_ask_cuba_to_cut_embassy_staff_by/dntxqkk", 
                controversiality=0, upvotes=1, downvotes=0, parent=None)
    image = Item(item_id=556, link_id="72xep5", body="https://i.redd.it/lqoz1uf6ijoz.jpg", 
                author="Smuggling_Plumz", submission = "Jabba the Trump", subreddit= "pics",
                permalink="/r/pics/comments/72xep5/jabba_the_trump/",
                controversiality=None, upvotes=71510, downvotes=0, parent="image")

    action = Action(action_id=1, item_id=1, reviewer_id=1, time_created=datetime.datetime.utcnow(), label_applied="brand_safe", notes="fine")
    
    db.session.add_all([reviewer, rev2, item, action, image])
    db.session.commit()

def connect_to_db(app, db_uri="postgresql:///crt"):
    """Connect the database to app"""

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    db.create_all()
    print "Connected to DB, Woohoo!"



