from flask_pymongo import pymongo
from datetime import date, timedelta
from utils import get_keys, tokenize, domain
import demoji

admin_name = "manager"
password = open("mongodb_pw.txt", "r").read()
database_name = "test"

mongoDB_connection =\
f"mongodb+srv://{admin_name}:{password}@main.mudjh.mongodb.net/{database_name}?retryWrites=true&w=majority"
client = pymongo.MongoClient(mongoDB_connection)
db = client[database_name]

tweets_collection = pymongo.collection.Collection(db, 'tweets')
users_collection = pymongo.collection.Collection(db, 'users')
accounts_collection = pymongo.collection.Collection(db, 'taccounts')


keys = get_keys()
collection = "tweets"
user_collection = "taccounts"
query = "humanrights"
since = str(date.today() - timedelta(days=3))
until = str(date.today() - timedelta(days=2))
searchCountry = "United States"



def saveToMongo(collection, document):
    col = db[collection]
    col.insert_one(document)

def get_collection():
    return db[collection]


def get_client():
    return client

def add_to_collection(document):
    db[collection].list_indexes(document)


def clearEntireCollection(collection):
    col = db[collection]
    col.delete_many({})

def find_tweet(tweet_id):
    return db[collection].find_one({"tweetID": tweet_id})


def find_user(user_id):
    return db[user_collection].find_one({"tweetID": user_id})



def tranform_tweets(tweet, collection):
    hashtags, mentions, urls, urlDomains, emojis = [], [], [], [], []

    time = tweet.created_at
    tweetID = tweet.id_str
    userID = tweet.user.id_str
    screenName = tweet.user.screen_name
    text = tweet.full_text

    # preprocessing
    emojis.extend(demoji.findall(text).keys())
    text2 = demoji.replace(text, '')
    textPrep = tokenize(text2)

    try:
        isoLanguage = tweet.metadata["iso_language_code"]
    except:
        isoLanguage = None
    favoriteCount = tweet.favorite_count
    retweetCount = tweet.retweet_count
    #   replyCount = tweet.reply_count                      # Premium API Only
    location = tweet.user.location  # Location on the user profile
    if tweet.place:
        placeName = tweet.place.full_name  # Place of the post that is tagged with
        placeCountry = tweet.place.country_code
    else:
        placeName = None
        placeCountry = None
    followersCount = tweet.user.followers_count

    # unwraping
    hashtags_tweepy = tweet.entities['hashtags']
    mentions_tweepy = tweet.entities['user_mentions']
    urls_tweepy = tweet.entities['urls']
    for hashtag in hashtags_tweepy:
        hashtags.append(hashtag['text'].lower())
    for user in mentions_tweepy:
        mentions.append(user['screen_name'])
    for url in urls_tweepy:
        urls.append(url['expanded_url'].lower())
        urlDomains.append(domain(url['expanded_url'].lower()))

    document = {
        "time": time,
        "tweetID": tweetID,
        "userID": userID,
        "screenName": screenName,
        "text": text,
        "emojis": emojis,
        "textPrep": textPrep,
        "isoLanguage": isoLanguage,
        "favoriteCount": favoriteCount,
        "retweetCount": retweetCount,
        "location": location,
        "placeName": placeName,
        "placeCountry": placeCountry,
        "followersCount": followersCount,
        "hashtags": hashtags,
        "mentions": mentions,
        "urls": urls,
        "urlDomains": urlDomains
    }

    saveToMongo(collection, document)
    return userID


def tranform_users(tweet, user_collection):
    userID = tweet.user.id_str
    name = tweet.user.name
    screenName = tweet.user.screen_name
    location = tweet.user.location
    description = tweet.user.description
    following = tweet.user.friends_count
    follower = tweet.user.followers_count
    favorite = tweet.user.favourites_count
    status = tweet.user.statuses_count
    profile_image_url = tweet.user.profile_image_url

    document2 = {
        "userID": userID,
        "name": name,
        "screenName": screenName,
        "location": location,
        "description": description,
        "following": following,
        "follower": follower,
        "favorite": favorite,
        "status": status,
        "profile_image_url": profile_image_url
    }
    saveToMongo(user_collection, document2)


