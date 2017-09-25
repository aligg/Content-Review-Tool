

import praw

def auth():
    """authorize using praw"""

reddit = praw.Reddit(client_id='pzrYrfuu5s917g',
                    client_secret="Id6SMfXIFevw1lF5NWua2Q8cgEA",
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
                    )


def grab_submissions():
    """grabs submissions from reddit controversial front page and data associated with them"""

    submissions = {}   
    for submission in reddit.subreddit('all').controversial('hour'):#reddit.front.controversial(limit=10):     
        submissions[submission.id] = {"Title" : submission.title, "URL" : submission.url, "Author" : submission.author}
       
    return submissions


def grab_comments():
    """ grabs comments associated with recent submission posts & creates dict"""

    s = grab_submissions()
    comments = {}
    for key in s.keys(): #could you do this with a dict comprehension / without all the loops
        submission = reddit.submission(url='https://www.reddit.com/' + key)
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            comments[comment.link_id] = { "comment_body" : comment.body,
                                                "comment_author" : comment.author,
                                                "subreddit" : comment.subreddit,
                                                "permalink" : comment.permalink(),
                                                "controversiality" : comment.controversiality,
                                                "submission_title" : submission.title,
                                                "comment_upvotes" : comment.ups,
                                                "comment_downvotes" : comment.downs,
                                                "num_reports" : comment.num_reports
            }
            if not comment.is_root:
                comments[comment.link_id].update({"comment_parent" : comment.parent().body})               
    return comments                
    



auth()
grab_submissions()
grab_comments()

