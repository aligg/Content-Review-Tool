
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

    __tablename__= "actions"

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


class AbuseScore(db.Model):
    """store abuse score data about comments"""

    __tablename__= "abusescores"

    score_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    item_id = db.Column(db.ForeignKey('items.item_id'))
    sub_nsfw = db.Column(db.Boolean, nullable=True)
    account_age = db.Column(db.Float, nullable=True) 
    badword_count = db.Column(db.Integer, nullable=True)
    author_karma = db.Column(db.Integer, nullable=True)
    s_safety_score = db.Column(db.Float, nullable=True)
    clf_safe_rating = db.Column(db.Float, nullable=True)
    clf_unsafe_rating = db.Column(db.Float, nullable=True)
    clf_safety_higher = db.Column(db.Boolean, nullable=True)


    #Define relationships to other tables
    item = db.relationship("Item", backref=db.backref("abusescores"))

    def __repr__(self):
        """Prettify printed output"""

        return "<Item item_id=%s clf_safe_rating=%s>" % (self.item_id, self.clf_safe_rating)


##############################################################################
#Helper functions & example data for testing

def example_data():
    """Create some sample data."""

    Action.query.delete()
    Item.query.delete()
    Reviewer.query.delete()


    reviewer = Reviewer(reviewer_id=4, email="ali.glenesk@gmail.com", handle="alig", password="$pbkdf2-sha256$29000$XgthbE1pTcmZc47xXksJgQ$Xi0f.1R2nyfRMzRpEp3ZcEx3gb1q88PCfIXuh3yLvtY", is_manager=True)
    rev2 = Reviewer(reviewer_id=5, email="miau@gmail.com", handle="miau", password="$pbkdf2-sha256$29000$LUXI.d/bm1NKKeU8Z0xJiQ$FQFZCxwG.F6CfhIMSIA9uT869LsTzyNQ8YVJ/4kTKnc", is_manager=False)

    item = Item(item_id=1, link_id="123", body="I LOVE TO POST ON REDDIT", 
                author="redditor", submission="subtest", subreddit="news",
                permalink="/r/news/comments/73xmht/officials_us_to_ask_cuba_to_cut_embassy_staff_by/dntxqkk", 
                controversiality=0, upvotes=1, downvotes=0, parent=None)
    item2 = Item(item_id=2, link_id="234", body="I LOVE TO POST ON REDDIT", 
                author="redditor", submission="subtest", subreddit="news",
                permalink="/r/news/comments/73xmht/officials_us_to_ask_cuba_to_cut_embassy_staff_by/dntxqkk", 
                controversiality=0, upvotes=1, downvotes=0, parent=None)
    item3 = Item(item_id=3, link_id="345", body="I LOVE TO POST ON REDDIT", 
                author="redditor", submission="subtest", subreddit="news",
                permalink="/r/news/comments/73xmht/officials_us_to_ask_cuba_to_cut_embassy_staff_by/dntxqkk", 
                controversiality=0, upvotes=1, downvotes=0, parent=None)
    item4 = Item(item_id=4, link_id="456", body="I LOVE TO POST ON REDDIT", 
                author="redditor", submission="subtest", subreddit="news",
                permalink="/r/news/comments/73xmht/officials_us_to_ask_cuba_to_cut_embassy_staff_by/dntxqkk", 
                controversiality=0, upvotes=1, downvotes=0, parent=None)
    item5 = Item(item_id=5, link_id="567", body="I LOVE TO POST ON REDDIT", 
                author="redditor", submission="subtest", subreddit="news",
                permalink="/r/news/comments/73xmht/officials_us_to_ask_cuba_to_cut_embassy_staff_by/dntxqkk", 
                controversiality=0, upvotes=1, downvotes=0, parent=None)
    image = Item(item_id=556, link_id="72xep5", body="https://i.redd.it/lqoz1uf6ijoz.jpg", 
                author="Smuggling_Plumz", submission = "Jabba the Trump", subreddit= "pics",
                permalink="/r/pics/comments/72xep5/jabba_the_trump/",
                controversiality=None, upvotes=71510, downvotes=0, parent="image")

    action = Action(action_id=1, item_id=1, reviewer_id=4, time_created=datetime.datetime.utcnow(), label_applied="brand_safe", notes="fine")
    action2 = Action(action_id=2, item_id=2, reviewer_id=4, time_created=datetime.datetime.utcnow(), label_applied="brand_safe", notes="fine")
    action3 = Action(action_id=3, item_id=3, reviewer_id=5, time_created=datetime.datetime.utcnow(), label_applied="brand_safe", notes="fine")
    action4 = Action(action_id=4, item_id=4, reviewer_id=4, time_created=datetime.datetime.utcnow(), label_applied="brand_safe", notes="fine")
    action5 = Action(action_id=5, item_id=5, reviewer_id=5, time_created=datetime.datetime.utcnow(), label_applied="brand_safe", notes="fine")
    action6 = Action(action_id=6, item_id=1, reviewer_id=5, time_created=datetime.datetime.utcnow(), label_applied="brand_safe", notes="fine")
    
    db.session.add_all([reviewer, rev2, item, item2, item3, item4, item5, action, image, action2, action3, action4, action5, action6])
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



