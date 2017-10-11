from model import (connect_to_db, db)
from dashboard import agreement_rate_by_item
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn import cross_validation
from sklearn import metrics
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

    return (X, Y)

    #print X.shape, Y.shape (as of 10/9 shape is (357, 2598) (357,) items in list + unique words I thinK? 

def cross_validate():
    """ instantiate the classifier and cross-validate """


    X = make_vectors()[0]
    Y = make_vectors()[1]


    classifier = BernoulliNB() #instantiate classifier

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

    print 'precision:',np.average(precision), '+/-', np.std(precision) #as of 10/9 13% precision and 4% recall 
    print 'recall:', np.average(recall), '+/-', np.std(recall)


    # probs= classifier.feature_log_prob_[1] - classifier.feature_log_prob_[0]
    # print len(probs)

    # features=vectorizer.get_feature_names()
    # print len(features) #as of now can only look at this 

    # sorted(zip(probs,features), reverse=True [:50])







#### still to do ######
# Try on one new sample comment

#spot check spammy words

#run classifier on each new comment for review 




