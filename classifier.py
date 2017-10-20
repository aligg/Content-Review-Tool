from model import (connect_to_db, db, Item, Reviewer, Action, BadWord, AbuseScore)
from dashboard import (agreement_rate_by_item, safety_score_maker)
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn import cross_validation
from sklearn import metrics
import praw
import os
import re
import time
#Goal: Predict whether a comment is safe or not safe with reasonably high precision, maybe 85%?

vectorizer = TfidfVectorizer()
classifier = BernoulliNB() 

def organize_data():
    """Grab label and comment body data from db, excluding those without 100% agreement rates. Return two lists"""
    
    ##create list of item_ids with agr rates below 100%
    s = []
    for key, value in agreement_rate_by_item().items():
        if value['agreement_rate'] != 1:
                s.append(key)
    
    ## grab all items from actions table, excluding images  
    sql = """
    select a.item_id, a.label_applied, i.body 
    from actions a
    join items i
    on a.item_id = i.item_id
    where a.item_id not in (select item_id from items where parent like '%image%')
    group by 1,2,3
    order by 1 asc;
    """

    cursor = db.session.execute(sql)
    items = cursor.fetchall()

    labels = []
    comments = []
    for item in items:
        if item[0] not in s: #exclude poor quality
            labels.append(item[1])
            comments.append(item[2])
    
    return (labels, comments)

def make_vectors():
    """transform text into vectors """

    labels = organize_data()[0]
    comments = organize_data()[1]


    X = vectorizer.fit_transform(comments)
    Y = np.array(labels)

    return (X, Y)

    #print X.shape, Y.shape (as of 10/9 shape is (357, 2598) (357,) items in list + unique words I thinK? 

def cross_validate():
    """Cross-validate """

    X = make_vectors()[0]
    Y = make_vectors()[1]


    cv = cross_validation.StratifiedKFold(Y,5)

    precision = []
    recall = []
    for train, test in cv:
        X_train = X[train]
        X_test = X[test]
        Y_train = Y[train]
        Y_test = Y[test]
    #print len(Y_train), len(Y_test) (as of 10/9 299 and 73 respectively)
        classifier.fit(X_train, Y_train)
        Y_hat = classifier.predict(X_test)
        p,r,_,_ = metrics.precision_recall_fscore_support(Y_test, Y_hat) #want to understand this line better 
        precision.append(p[1])
        recall.append(r[1])

    print 'precision:',np.average(precision), '+/-', np.std(precision) #as of 10/9 13% precision and 4% recall #as of 10/12 28% precision 11% recall 
    print 'recall:', np.average(recall), '+/-', np.std(recall)


def classify_a_comment(comment_body):
    """output what classifier thinks for a specific comment"""
    
    body = comment_body
    body = vectorizer.transform([body])

    classifier_output = classifier.predict_proba(body)
    # print "Label order", classifier.classes_
    # print "Brand Safe", classifier_output[0][0]
    # print "Not Brand Safe", classifier_output[0][1]
    
    return classifier_output

def is_nsfw(reddit, subreddit):
    """check if subreddit is nsfw, helper function for heuristic, removing api call from the main function"""

    s = reddit.subreddit(subreddit)
    if s.over18:
        sub_nsfw = True
    elif s.over18 is False:
        sub_nsfw = False
    else: 
        sub_nsfw = None

    return sub_nsfw

def memoize(f):
    """ memo to reduce api calls, receives reddit object & curr_subreddit from heuristic maker"""
    
    memo = {}
    def helper(x, y): 
        if y not in memo:            
            memo[y] = f(x, y)
        return memo[y]
    return helper

is_nsfw = memoize(is_nsfw)


def heuristic_maker(item_id):
    """Grabs signals about a given comment and outputs a guess as to safe or not safe"""
    
    ####auth-- let's restructure this later
    reddit = praw.Reddit(client_id=os.environ['CLIENT_ID'],
        client_secret=os.environ['CLIENT_SECRET'],
        user_agent=os.environ['USER_AGENT'])
   
    #### variables & sql fetching ####
    curr_item_id = item_id
    sql = """select subreddit, author, body from items where item_id = :item_id"""
    cursor = db.session.execute(sql, {'item_id': curr_item_id})
    comment_data = cursor.fetchall()
    curr_subreddit = comment_data[0][0]
    author = comment_data[0][1]
    comment_body = comment_data[0][2]
    comment_heuristics = {}


    ####Is the subreddit nsfw####
    sub_nsfw = is_nsfw(reddit, curr_subreddit)

    ####Is author's account new? What's their karma?####
    try:
        u = reddit.redditor(author)
        account_age_days = (time.time() - u.created_utc)/60/60/24
        author_comment_karma = u.comment_karma

    except:
        account_age_days = None
        author_comment_karma = None    

    ####Does comment contain badwords & how many?####
    badwords_list = [w.word for w in BadWord.query.filter(BadWord.language == 'en')]
    matches = {}
    badwords_pattern = r'\b(' + '|'.join(badwords_list) + r')\b'
    res = re.findall(badwords_pattern, comment_body.lower(), re.IGNORECASE)
    if len(res) > 0:
        matches[curr_item_id] = ', '.join(res)
    badword_count = len(matches)
    badwords = matches

    ####What is the subreddit safety score
    safety_information = safety_score_maker()
    for item in safety_information:
        if curr_subreddit in item:
            subreddit_safety_score = item[1]
            break
        else: 
            subreddit_safety_score = None 

    ####Does Bernoulli classifier think safe or not safe
    classifier_ratings = classify_a_comment(comment_body)
    safe_rating = classifier_ratings[0][0]
    unsafe_rating = classifier_ratings[0][1]

    if safe_rating > unsafe_rating:
        clf_safety_higher = True
    elif safe_rating < unsafe_rating:
        clf_safety_higher = False

    comment_heuristics[curr_item_id] = {"sub_nsfw" : sub_nsfw,
                                        "account_age_days" : account_age_days,
                                        "badword_count" : len(matches),
                                        "author_karma" : author_comment_karma,
                                        "s_safety_score" : subreddit_safety_score,
                                        "clf_safe_rating" : safe_rating,
                                        "clf_unsafe_rating" : unsafe_rating,
                                        "clf_safety_higher" : clf_safety_higher
                                        }
    return comment_heuristics


def heuristic_classifier(comment_id):
    """Using data from abusescores table made in heuristic_maker above, predict safety label outcome"""

    ###grab data from abusescores db
    sql = """select item_id, sub_nsfw, account_age, badword_count, author_karma, s_safety_score, clf_safety_higher
            from abusescores
            where item_id = :item_id
            group by 1,2,3,4,5,6,7
            limit 10
            """
    cursor = db.session.execute(sql,
                                {"item_id" : comment_id})
    item = cursor.fetchall()
    
    ###variables from sql result
    for result in item:
        item_id = result[0] 
        sub_nsfw = result[1] 
        account_age = result[2] 
        badwords = result[3] 
        karma = result[4] 
        sscore = result[5] 
        clf_safe = result[6] 

    ###heuristic logic 
    if clf_safe is False and badwords > 0:
        verdict = "not_brand_safe"
    elif sub_nsfw is True and badwords > 0:
        verdict = "not_brand_safe"
    elif sub_nsfw is True and sscore < .85 and clf_safe is False:
        verdict = "not_brand_safe"
    elif sub_nsfw is True and sscore < .6:
        verdict = "not_brand_safe"
    elif account_age > 500 and badwords == 0 and karma > 2000 and sscore > .85 and clf_safe is True:
        verdict = "brand_safe"
    else:
        verdict = "need_more_info"

    return verdict


       

        



    # probs= classifier.feature_log_prob_[1] - classifier.feature_log_prob_[0]
    # print len(probs)

    # features=vectorizer.get_feature_names()
    # print len(features) #as of now can only look at this 

    # sorted(zip(probs,features), reverse=True [:50])

