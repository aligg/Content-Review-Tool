
import os
import praw

from sqlalchemy import func
from model import (Action, Reviewer, Item, BadWord, connect_to_db, db)
import datetime


def authorize():
    """authorize using praw"""

    reddit = praw.Reddit(client_id=os.environ['CLIENT_ID'],
        client_secret=os.environ['CLIENT_SECRET'],
        user_agent=os.environ['USER_AGENT'])
    
    return reddit


def grab_submissions(reddit):
    
    """grabs submissions from reddit controversial front page and data associated with them"""

    submissions = {} 
    for submission in reddit.subreddit('all').top('day', limit=50):#reddit.front.controversial(limit=10):     
        submission.comment_sort = "new"
        submissions[submission.id] = submission
       
    return submissions



def grab_images(reddit):
    """grabs images from pics subreddit and create dictionary"""
    
    images={}
    for submission in reddit.subreddit('pics').top('day', limit=50):
        s=submission
        images[s.id] = {"body" : s.url,
                    "subreddit" : s.subreddit.display_name,
                    "permalink": s.permalink,
                    "submission" : s.title,
                    "upvotes": s.ups,
                    "downvotes": s.downs,
                    "author": s.author.name}
    return images



def grab_comments(reddit, s=None):
    """ grabs comments associated with recent submission posts & creates dict"""

    if not s:
        s = grab_submissions(reddit)

    comments = {}
    count = 0
   
    for key, submission in s.items(): #could you do this with a dict comprehension / without all the loops
        submission.comments.replace_more(limit=0)
        num_comments = min(len(submission.comments), 3)
        for comment_num in range(0, num_comments): 
            comment = submission.comments[comment_num]
            comments[comment.link_id] = { "body" : comment.body,
                                                "subreddit" : comment.subreddit.display_name,
                                                "permalink" : comment.permalink(),
                                                "controversiality" : comment.controversiality,
                                                "submission" : submission.title,
                                                "upvotes" : comment.ups,
                                                "downvotes" : comment.downs,
                                                "num_reports" : comment.num_reports
            }
            
            if not comment.is_root:
                comments[comment.link_id].update({"parent" : comment.parent().body}) 
            if comment.author is not None:
                comments[comment.link_id].update({"author" : comment.author.name})
            # count += 1           
    return comments


def load_items(comments=None):
    """Populate items table with data from Reddit API"""

    link_id_list = [a.link_id for a in Item.query.all()]
    
    if comments is None:
        comments = grab_comments(reddit)

    for link_id, values in comments.items(): 
        if link_id not in link_id_list:
            parent = values.get('parent', None)
            author = values.get('author', None)
            item = Item(
                link_id = link_id,
                body = values['body'],
                author = author,
                submission = values['submission'],
                subreddit = values['subreddit'],
                permalink = values['permalink'],
                controversiality = values['controversiality'],
                upvotes = values['upvotes'],
                downvotes = values['downvotes'],
                parent = parent)
            print "DB seeded with more comments!"
            db.session.add(item)

    db.session.commit()

def load_images():
    """Populate items table with image data from Reddit API"""

    link_id_list = [a.link_id for a in Item.query.all()]

    images = grab_images(reddit)

    for link_id, values in images.items(): 
        if link_id not in link_id_list:
            author = values.get('author', None)
            item = Item(
                link_id = link_id,
                body = values['body'],
                author = author,
                submission = values['submission'],
                subreddit = values['subreddit'],
                permalink = values['permalink'],
                upvotes = values['upvotes'],
                downvotes = values['downvotes'],
                parent = "image")
            print "DB seeded with images!"
            db.session.add(item)

    db.session.commit()


def load_words():
    """Populate base data from badwords db"""

    for row in open("seeddata"):
        row = row.rstrip()
        word_id, word, language = row.split(",")

        word = BadWord(word_id=word_id,
                        word=word,
                        language=language,
                    category="profanity")

        db.session.add(word)
    db.session.commit()



def set_val_user_id():
    """Set value for the next word_id after seeding badwords table"""

    result = db.session.query(func.max(BadWord.word_id)).one()
    max_id = int(result[0])

    query = "SELECT setval('badwords_word_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

    

reddit = authorize()


if __name__ == "__main__":
    
    from server import app
    connect_to_db(app)

    # load_images()
    load_items()
    set_val_user_id()


    
 

