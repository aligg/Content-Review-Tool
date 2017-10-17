import os
import praw
from sqlalchemy import func
from model import (Action, Reviewer, Item, BadWord, connect_to_db, db, AbuseScore)
import datetime
from classifier import (heuristic_maker, organize_data, make_vectors, cross_validate)


def authorize():
    """authorize using praw"""

    reddit = praw.Reddit(client_id=os.environ['CLIENT_ID'],
        client_secret=os.environ['CLIENT_SECRET'],
        user_agent=os.environ['USER_AGENT'])
    
    return reddit


def grab_submissions(reddit):
    """grabs submissions & associated data from reddit front page and add to a dict"""

    submissions = {} 
    for submission in reddit.subreddit('all').top('week', limit=30):     
        submission.comment_sort = "new"
        submissions[submission.id] = submission
       
    return submissions



def grab_images(reddit):
    """grabs images from pics subreddit and add to a dict"""
    
    images={}
    for submission in reddit.subreddit('pics').top('day', limit=30):
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
   
    for _, submission in s.items(): #still would like to refactor this to be faster/ with less looping
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

    for row in open("seeddata/badwords"):
        row = row.rstrip()
        word_id, word, language = row.split(",")

        word = BadWord(word_id=word_id,
                        word=word,
                        language=language,
                    category="profanity")

        db.session.add(word)
    db.session.commit()



def set_val_word_id():
    """Set value for the next word_id after seeding badwords table"""

    result = db.session.query(func.max(BadWord.word_id)).one()
    max_id = int(result[0])

    query = "SELECT setval('badwords_word_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


def load_abuse_scores():
    """Populate initial abuse score database"""

    item_ids = """select item_id from items where parent is Null and item_id not in (select item_id from abusescores) limit 10;"""
    cursor = db.session.execute(item_ids)
    comment_data = cursor.fetchall()
    item_id_list = [item_id[0] for item_id in comment_data]
    
    for item_id in item_id_list:
        comment_heuristics = heuristic_maker(item_id)
       
        
        item = AbuseScore(item_id = item_id,
                            sub_nsfw = comment_heuristics[item_id]['sub_nsfw'],
                            account_age = comment_heuristics[item_id]['account_age_days'],
                            badword_count = comment_heuristics[item_id]['badword_count'],
                            author_karma = comment_heuristics[item_id]['author_karma'],
                            s_safety_score = comment_heuristics[item_id]['s_safety_score'],
                            clf_safe_rating = comment_heuristics[item_id]['clf_safe_rating'],
                            clf_unsafe_rating = comment_heuristics[item_id]['clf_unsafe_rating'],
                            clf_safety_higher = comment_heuristics[item_id]['clf_safety_higher'])
        db.session.add(item)

    db.session.commit()
        

reddit = authorize()


if __name__ == "__main__":
    
    from server import app
    connect_to_db(app)

    # load_images()
    # load_items()
    # set_val_word_id()
    organize_data()
    make_vectors()
    cross_validate()
    load_abuse_scores()


    
 

