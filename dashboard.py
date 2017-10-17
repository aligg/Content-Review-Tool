"""Helper functions to provide proper data to dashboards"""

from model import (connect_to_db, db, Item, Reviewer, Action, BadWord)
from datetime import (datetime, date)
import numpy

def table1_sql():
    """Grabs data for first table"""

    sql = """
    select date_trunc('day', time_created) as date, count(action_id) as total_reviews
    from actions 
    where time_created > CURRENT_DATE - Interval '1 month'
    group by 1
    order by 1 asc
    """
   
    cursor = db.session.execute(sql)
    datasample = cursor.fetchall()


    return datasample


def get_table1_data():
    """Formats data from sql into nice lists and passes out data dict with attributes for graphs"""

    labels = []
    data = []

    for date, totals in table1_sql():
        labels.append(str(date)[:10])
        data.append(int(totals))

    data_dict = {
        "labels": labels,
        "datasets": [
            {
                "label": "Daily Total Reviews",
                "fill": False,
                "lineTension": 0.5,
                "backgroundColor": "rgba(151,187,205,0.2)",
                "borderColor": "rgba(151,187,205,1)",
                "borderCapStyle": 'butt',
                "borderDash": [],
                "borderDashOffset": 0.0,
                "borderJoinStyle": 'miter',
                "pointBorderColor": "rgba(151,187,205,1)",
                "pointBackgroundColor": "#fff",
                "pointBorderWidth": 1,
                "pointHoverRadius": 5,
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(151,187,205,1)",
                "pointHoverBorderWidth": 2,
                "pointHitRadius": 10,
                "data": data,
                "spanGaps": False}
        ]
    }
    return data_dict


def table2_sql():
    """Grabs data from database for use by agreement rate table"""

    sql = """ select max(time_created) as last_review, item_id, count(item_id) as rev_count, array_agg(reviewer_id), string_agg(label_applied, ', ') 
                from actions
                where time_created > CURRENT_DATE - Interval '1 month'
                group by 2
                having count(item_id) > 1 
                order by 1 desc;

    """
    cursor = db.session.execute(sql)
    datasample = cursor.fetchall()
    
    return datasample


def agreement_rate_by_item():
    """Create dictionary of agreement rate per item_id"""

    
    agreement_rate_data = {}

    for day, item_id, review_count, reviewers, labels in table2_sql():
        labels = str(labels)
        labels= labels.split(', ')

        if len(labels) == 3 and len(set(labels)) == 2:
            agreement_rate = .67
        elif len(labels) == 2 and len(set(labels)) == 2:
            agreement_rate = .5
        elif len(set(labels)) == 1:
            agreement_rate = 1

        agreement_rate_data[item_id] = {"last_review": day,
                            "total_reviews": int(review_count),
                            "reviewers": reviewers,
                            "labels": labels,
                            "agreement_rate": agreement_rate
                            } #agreement_rate_data is now a dictionary w/ data for agreement_rate for each item as well as additional information

    
    return agreement_rate_data


def agreement_rate_maker():
    """Calculate agreement rate daily average and add days and rates and sample size to separate ordered lists"""
    
    
    days = []
    rate = []
    sample = []
    day_and_rates_list = []
    day_and_rates = {}

    #create dictionary with days and list of agreement rates for all items on that day
    for item in agreement_rate_by_item().values():
        if item['last_review'].date() not in day_and_rates.keys():
            day_and_rates[item['last_review'].date()] = [item['agreement_rate']]
        else:
            day_and_rates[item['last_review'].date()].append(item['agreement_rate'])
    
    #unpack dictionary and create a list of tuples so we'll have ordering for the chart
    for date, agreement_rates in day_and_rates.items():
        day_and_rates_list.append((date, agreement_rates))
    day_and_rates_list = sorted(day_and_rates_list)

    #separate items into 3 lists for the table, & finally calculate sample size & agreement rate for the day
    for date, agreement_rates in day_and_rates_list:
        days.append(date) 
        sample.append(len(agreement_rates)) 
        rate.append(numpy.mean(agreement_rates)) 

    days = [str(day) for day in days] 
         
    return (days, rate, sample)

def get_table2_data():
    """Spits out data for the agreements table nicely"""


    data_dict = {
        "labels":  agreement_rate_maker()[0],
        "datasets": [
            {
                "label": "Daily Agreement Rate",
                "fill": False,
                "lineTension": 0.5,
                "backgroundColor": "rgba(151,187,205,0.2)",
                "borderColor": "rgba(151,187,205,1)",
                "borderCapStyle": 'butt',
                "borderDash": [],
                "borderDashOffset": 0.0,
                "borderJoinStyle": 'miter',
                "pointBorderColor": "rgba(151,187,205,1)",
                "pointBackgroundColor": "#fff",
                "pointBorderWidth": 1,
                "pointHoverRadius": 5,
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(151,187,205,1)",
                "pointHoverBorderWidth": 2,
                "pointHitRadius": 10,
                "data": agreement_rate_maker()[1],
                "spanGaps": False}
        ]
    }

    return data_dict

def get_table3_data():
    """queries db and passes clean output to page for a table of reviews per person per week"""


    sql = """ select date_trunc('week', time_created), handle, count(action_id)
                from actions a
                join reviewers b
                on a.reviewer_id = b.reviewer_id
                group by 1,2
                order by 1 desc, 3 desc;
    """
    
    cursor = db.session.execute(sql)
    datasample = cursor.fetchall()
    clean_datasample = []

    for (week, handle, total) in datasample:
        week= str(week)[:10]
        handle = str(handle)
        total = int(total)
        tup = (week, handle, total)
        clean_datasample.append(tup)

    return clean_datasample

def safety_score_maker():
    """ Queries the db for safety data across comments per subreddit and creates a safety score"""

    sql = """
    select subreddit, (total_safe*1.0) as safes, (not_safe*1.0) as not_safes, total_reviews
    from
    (select subreddit, count(action_id) as total_reviews, SUM(case when label_applied = 'brand_safe' THEN 1 END) as total_safe, SUM(case when label_applied = 'not_brand_safe' then 1 END) as not_safe
    from actions a
    join items b
    on a.item_id = b.item_id
    group by 1) a
    where total_reviews > 20
    group by 1,2,3,4
    order by 2 desc;
    """
    cursor = db.session.execute(sql)
    result = cursor.fetchall()
    
    safety_score = 0
    safety_information = []

    for subreddit, safes, not_safes, total in result:
        if safes == None:
            safety_score = 0
        if not_safes == None:
            safety_score = 100
        else:
            safety_score = safes / (safes+not_safes)
        
        new = (subreddit, safety_score, total)
        safety_information.append(new)
    
    safety_information = sorted(safety_information, key=lambda x: x[1])

    return safety_information



    







