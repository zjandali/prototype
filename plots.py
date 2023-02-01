import plotly
import plotly.graph_objs as go
import plotly.express as px

import pandas as pd
import numpy as np
import json
from collections import Counter

import db
from datetime import datetime, date, timedelta

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt 

import random
import string
import os

import networkx as nx


### Get data for plotting

def counts(keyword,fromDate,toDate):
    """
    get the total number of tweets requested
    """
    total = db.tweets_collection.find({ 
            "time": {"$gt": datetime.strptime(fromDate,"%Y-%m-%d"), "$lt": datetime.strptime(toDate,"%Y-%m-%d")+timedelta(days=1)},
            "hashtags": {"$in":[keyword]}
            }).count()
    return total

def top_count(keyword,fromDate,toDate,top=3,type="tweets"):
    """
    Return tweets that were liked the most
    - define top: by percentage (top 10%) or by number (top 10)
    - return type: can be url of the tweets or contents
    """

    if top <= 1:
        top2 = int(counts(keyword,fromDate,toDate) * top)
    elif top > 1:
        top2 = top
    
    if type == "urls":
        list_ = [("https://twitter.com/twitter/statuses/"+item["tweetID"],item["screenName"],item["favoriteCount"]) for item in db.tweets_collection.find({
                            "time": {"$gt": datetime.strptime(fromDate,"%Y-%m-%d"), "$lt": datetime.strptime(toDate,"%Y-%m-%d")+timedelta(days=1)},
                            "hashtags": {"$in":[keyword]}
                            }).sort('favoriteCount', -1).limit(top2)]
    elif type == "tweets":
        list_ = [item["textPrep"] for item in db.tweets_collection.find({
                            "time": {"$gt": datetime.strptime(fromDate,"%Y-%m-%d"), "$lt": datetime.strptime(toDate,"%Y-%m-%d")+timedelta(days=1)},
                            "hashtags": {"$in":[keyword]}
                            }).sort('favoriteCount', -1).limit(top2)]
    return list_


def generate_list(column,keyword,fromDate,toDate):
    """
    return a list of hashtags/emojis/urls/domains as requested
    """
    if keyword:
        if column in ["hashtags","emojis","urlDomains","urls","mentions"]:
            list_ = [i for item in db.tweets_collection.find({
                        "time": {"$gt": datetime.strptime(fromDate,"%Y-%m-%d"), "$lt": datetime.strptime(toDate,"%Y-%m-%d")+timedelta(days=1)},
                        "hashtags": {"$in":[keyword]}},
                        {column:1}
                        ) for i in item[column]]
        else:
            list_ = [item[column] for item in db.tweets_collection.find({
                        "time": {"$gt": datetime.strptime(fromDate,"%Y-%m-%d"), "$lt": datetime.strptime(toDate,"%Y-%m-%d")+timedelta(days=1)},
                        "hashtags": {"$in":[keyword]}},
                        {column:1}
                        )]
    else:
        ## we might need to see all the hashtags in db
        list_pre = []
        for item in db.tweets_collection.find({},{column:1}):
            list_pre.extend(item[column])
        list_ = sorted(list(set(list_pre)))

    return list_







### Plotting functions

def plot_count_v(list_, top=10):
    df = pd.DataFrame(Counter(list_),index=[0]).T
    df.columns = ["Counts"]
    df.sort_values("Counts",ascending=False,inplace=True)
    x = df.index[:top]
    y = df["Counts"][:top]
    data = [
        go.Bar(
            x=x,
            y=y,
            marker_color="#2E91E5"
        )
    ]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return [graphJSON, list(df.index[:30]), list(df["Counts"][:30])]

def plot_count_h(list_, top=10):
    df = pd.DataFrame(Counter(list_),index=[0]).T
    df.columns = ["Counts"]
    df.sort_values("Counts",ascending=True,inplace=True)
    y = df.index[-top:]
    x = df["Counts"][-top:]
    data = [
        go.Bar(
            x=x,
            y=y,
            orientation='h',
            marker_color="#2E91E5"
        )
    ]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    results1 = list(df.index[-30:])
    results1.reverse()
    results2 = list(df["Counts"][-30:])
    results2.reverse()
    return [graphJSON, results1, results2]

    

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def update_folder(path):
    list_of_files = os.listdir(path)    
    if len(list_of_files)>10:
        oldest_file = min([os.path.join(path, f) for f in list_of_files], key=os.path.getctime)
        os.remove(oldest_file)
    
def plot_wordcloud(list_, top=30):
    
    text = " ".join(list_)
    
    sys_word = ["hashtag","url","user","repeat","elong","amp"]
    stops = list(STOPWORDS) + sys_word
    
    wordcloud = WordCloud(stopwords=stops,
                          background_color="white",
                          width=3000,height=1500,
                          colormap='copper',
                          collocations=False).generate(text)
    freq = WordCloud(stopwords=stops,
                          background_color="white",
                          width=3000,height=1500,
                          colormap='copper',
                          mask=None,
                          collocations=False).process_text(text)
    freq_sort = sorted(freq.items(), key=lambda x:x[1], reverse=True)
    freq_top = [i[0] for i in freq_sort[:top]]

    
    path = "static/wordcloud"
    filename = f"{get_random_string(8)}.png"
    update_folder(path)
    wordcloud.to_file(os.path.join(path, filename))

    return ["wordcloud/"+filename, freq_top]


def plot_bar_chart_race(column, keyword, fromDate, toDate, top=10):
    fromDate2 = datetime.strptime(fromDate,"%Y-%m-%d")
    toDate2 = datetime.strptime(toDate,"%Y-%m-%d")
    currentDate = fromDate2

    cols = ["date","col","count"]
    df_all = pd.DataFrame(columns=cols)
    while currentDate <= toDate2:
        startDate = str(currentDate.date())
        endDate = str(currentDate.date())
        
        list_ = generate_list(column,keyword,startDate,endDate)
        df = pd.DataFrame(Counter(list_),index=[startDate]).stack().reset_index()
        df.columns = cols
        df = df.sort_values("count",ascending=True).iloc[-top:,:]
        df_all = pd.concat([df_all,df])
            
        currentDate = currentDate+timedelta(days=1)

    fig = px.bar(df_all, 
                 x="count", 
                 y="col", 
                 orientation='h',
                 animation_frame="date",
                 color_discrete_sequence=["#2E91E5"]
                 )
    fig.update_layout(
        autosize=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis={"title":"Counts","automargin":True},
        yaxis={"title":f"{column.capitalize()}","automargin":True},
        title = f"Dynamic Change of {column.capitalize()} from {fromDate} to {toDate}",
        )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def plot_topical_trend(column, keyword, fromDate, toDate):
    fromDate2 = datetime.strptime(fromDate,"%Y-%m-%d")
    toDate2 = datetime.strptime(toDate,"%Y-%m-%d")
    currentDate = fromDate2

    postCount = list()
    likeAvg = list()
    likeMax = list()
    dateList = list()

    while currentDate <= toDate2:
        startDate = str(currentDate.date())
        endDate = str(currentDate.date()+timedelta(days=1))
        
        tweetCount = counts(keyword,startDate,endDate)
        likeList = generate_list(column,keyword,startDate,endDate)
        
        postCount.append(tweetCount)
        likeAvg.append(np.mean(likeList))
        likeMax.append(max(likeList))
        dateList.append(startDate)
        
        currentDate = currentDate+timedelta(days=1)

    data1 = [go.Scatter(x=dateList, y=postCount, line_color='#2E91E5',fill='tozeroy')]
    graphJSON1 = json.dumps(data1, cls=plotly.utils.PlotlyJSONEncoder)

    data2 = [go.Scatter(x=dateList, 
               y=likeAvg, 
               line_color='#2E91E5',
               visible=True),
            go.Scatter(x=dateList, 
               y=likeMax, 
               line_color='#0084b4',
               visible=False)]
    graphJSON2 = json.dumps(data2, cls=plotly.utils.PlotlyJSONEncoder)

    stats = [dateList[postCount.index(max(postCount))],
            max(postCount),
            dateList[likeMax.index(max(likeMax))],
            max(likeMax)]

    return [graphJSON1,graphJSON2,stats]


def plot_hashtag_nx(hashtagList, keyword):

    topHashtags = dict(Counter(hashtagList).most_common(10))

    edgeList = []
    nodeList = []
    nodeList.append(json.dumps({"id":keyword,"label":keyword,"shape":"dot","size":20,"x":250,"y":250}))

    top = 0
    for topHashtag, numTweets in topHashtags.items():
        if topHashtag != keyword:
            top += 1
            if top <= 5:
                group = "top3"
            else:
                group = "nonTop3"
            weight = round(numTweets/topHashtags[keyword],2)

            nodeList.append(json.dumps({"id":topHashtag,"label":topHashtag,"shape":"dot","size":round(weight*20),"group":group}))
            edgeList.append(json.dumps({"from":keyword,"to":topHashtag,"weight":weight,"label":weight}))

    return [json.dumps(nodeList), json.dumps(edgeList)]


