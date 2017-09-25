
import os
import praw

def auth():
    """authorize using praw"""

# client_id=os.environ['CLIENT_ID'],
# client_secret=os.environ['CLIENT_SECRET'],
# user_agent=os.environ['USER_AGENT']
#not working for some reason will check in directly for now

reddit = praw.Reddit(client_id="qAShGvc4GtLyGw",
                    client_secret="cfRNOuQ18a-Zr4Yj46uOosrUxWk",
                    user_agent="uMozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
                    )



def grab_submissions():
    """grabs submissions from reddit controversial front page and data associated with them"""

    submissions = {}   
    for submission in reddit.subreddit('all').controversial('hour'):#reddit.front.controversial(limit=10):     
        submission.comment_sort = "new"
        submissions[submission.id] = {"Title" : submission.title, "URL" : submission.url, "Author" : submission.author}
       
    return submissions


def grab_comments():
    """ grabs comments associated with recent submission posts & creates dict"""

    s = grab_submissions()
    comments = {}
    count = 0

    for key in s.keys(): #could you do this with a dict comprehension / without all the loops
        submission = reddit.submission(url='https://www.reddit.com/' + key)
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list(): 
            if count < 3:
                comments[comment.link_id] = { "body" : comment.body,
                                                    "author" : comment.author,
                                                    "subreddit" : comment.subreddit,
                                                    "permalink" : comment.permalink(),
                                                    "controversiality" : comment.controversiality,
                                                    "submission" : submission.title,
                                                    "upvotes" : comment.ups,
                                                    "downvotes" : comment.downs,
                                                    "num_reports" : comment.num_reports
                }
                
                if not comment.is_root:
                    comments[comment.link_id].update({"parent" : comment.parent().body}) 
            count += 1           
    print comments
    return comments                
    



auth()
grab_submissions()
grab_comments()

