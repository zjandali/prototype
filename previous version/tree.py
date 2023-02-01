import networkx as nx
import demoji
from db import db, collection



class Tweet_Node:
    def __init__(self, tweet):
        self.hashtags, self.mentions, self.urls, self.urlDomains, self.emojis = [], [], [], [], []
        self.tweetID = tweet.id_str
        self.userID = tweet.user.id_str
        self.screenName = tweet.user.screen_name
        self.text = tweet.full_text
        self.time = tweet.created_at
        self.emojis.extend(demoji.findall(self.text).keys())
        self.text2 = demoji.replace(self.text, '')
        try:
            self.isoLanguage = tweet.metadata["iso_language_code"]
        except:
            self.isoLanguage = None
        self.favoriteCount = tweet.favorite_count
        self.retweetCount = tweet.retweet_count
        self.location = tweet.user.location
        try:
            self.isoLanguage = tweet.metadata["iso_language_code"]
        except:
            self.isoLanguage = None
        self.favoriteCount = tweet.favorite_count
        self.retweetCount = tweet.retweet_count
        if tweet.place:
            self.placeName = tweet.place.full_name  # Place of the post that is tagged with
            self.placeCountry = tweet.place.country_code
        else:
            self.placeName = None
            self.placeCountry = None
        self.followersCount = tweet.user.followers_count
        hashtags_tweepy = tweet.entities['hashtags']
        mentions_tweepy = tweet.entities['user_mentions']
        urls_tweepy = tweet.entities['urls']
        for hashtag in hashtags_tweepy:
            self.hashtags.append(hashtag['text'].lower())
        for user in mentions_tweepy:
            self.mentions.append(user['screen_name'])
        for url in urls_tweepy:
            self.urls.append(url['expanded_url'].lower())
            self.urlDomains.append(self.domain(url['expanded_url'].lower()))
        self.document = {
            "time": self.time,
            "tweetID": self.tweetID,
            "userID": self.userID,
            "screenName": self.screenName,
            "text": self.text,
            "emojis": self.emojis,
            "textPrep": "i dont have access to this func",
            "isoLanguage": self.isoLanguage,
            "favoriteCount": self.favoriteCount,
            "retweetCount": self.retweetCount,
            "location": self.location,
            "placeName": self.placeName,
            "placeCountry": self.placeCountry,
            "followersCount": self.followersCount,
            "hashtags": self.hashtags,
            "mentions": self.mentions,
            "urls": self.urls,
            "urlDomains": self.urlDomains
        }
        self.collection = db[collection]
        self.collection.insert_one(self.document)


