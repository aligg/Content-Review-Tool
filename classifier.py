from model import (connect_to_db, db)
from dashboard import agreement_rate_by_item
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn import cross_validation
from sklearn import metrics

# from model import (connect_to_db, db, Item, Reviewer, Action, BadWord)


#Goal: Predict whether a comment is safe or not safe with reasonably high precision, maybe 85%?


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

    vectorizer = TfidfVectorizer()

    X = vectorizer.fit_transform(comments)
    Y = np.array(labels)

    print X.shape, Y.shape

   


#transform the data into vectors 

#choose the right classifier and instantiate it

#cross validation using k fold (mitigates overfitting / reduces bias) AND actually do the thing

# calculate precision & recall across k-folds

# Try on one new sample comment

#spot check spammy words

#run classifier on each new comment for review 




########
#more qs -> the big no no of like 'gaming' your training data 

# organize_data()
