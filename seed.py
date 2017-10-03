
import os
import praw

from sqlalchemy import func
from model import (Action, Reviewer, Item, BadWord, connect_to_db, db)
from server import app
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
    for submission in reddit.subreddit('all').top('hour', limit=50):#reddit.front.controversial(limit=10):     
        submission.comment_sort = "new"
        submissions[submission.id] = submission
       
    return submissions


def grab_comments(reddit):
    """ grabs comments associated with recent submission posts & creates dict"""

   
    s = grab_submissions(reddit)

    comments = {}
    count = 0
   
    for key, submission in s.items(): #could you do this with a dict comprehension / without all the loops
        submission.comments.replace_more(limit=0)
        num_comments = min(len(submission.comments), 3)
        for comment_num in range(0, num_comments): 
            comment = submission.comments[comment_num]
            comments[comment.link_id] = { "body" : comment.body,
                                                "author" : comment.author.name,
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
            # count += 1           
    return comments


def load_items():
    """Populate items table with data from Reddit API"""

    link_id_list = [a.link_id for a in Item.query.all()]

    for link_id, values in grab_comments(reddit).items(): 
        if link_id not in link_id_list:
            parent = values.get('parent', None)
            item = Item(
                link_id = link_id,
                body = values['body'],
                author = values['author'],
                submission = values['submission'],
                subreddit = values['subreddit'],
                permalink = values['permalink'],
                controversiality = values['controversiality'],
                upvotes = values['upvotes'],
                downvotes = values['downvotes'],
                parent = parent)
            print link_id, values['body']
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

    # Get the max word_id in the database
    result = db.session.query(func.max(BadWord.word_id)).one()
    max_id = int(result[0])

    # Set the value for the next word_id to be max_id + 1
    query = "SELECT setval('badwords_word_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

    

reddit = authorize()
# grab_comments(reddit)




if __name__ == "__main__":

    connect_to_db(app)

    # db.create_all()

    load_items()
    #load_words()
    set_val_user_id()


    
 

