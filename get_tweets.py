from utils import initialize_api
from db import searchCountry, query, since, until, collection, db, user_collection, tranform_users, tranform_tweets
import tweepy
from datetime import datetime, timedelta



def collect():
    if place_id:
        q = query + f" since:{since} until:{until}" + " -filter:retweets AND -filter:replies" + f" AND place:{place_id}"
        print(f"Start Collecting Query: {q}")
    else:
        q = query + f" since:{since} until:{until}" + " -filter:retweets AND -filter:replies"
        print(f"Start Collecting Query: {q}")

    count_ = 0
    new_tweet_count = 0
    new_tweet_found = False
    new_user_found = False
    new_user_count = 0
    print(f"Time of now: {datetime.now()}")

    for tweet in tweepy.Cursor(api.search, q=q, lang="en", tweet_mode="extended").items(30):
        count_ += 1
        if count_ % 100 == 0:
            print(f"Have collecte {count_} tweets! - {datetime.now()}")
        # check if this tweet is already in the database
        if db[collection].find_one({"tweetID": tweet.id_str}):
            continue
        else:
            new_tweet_count += 1
            new_tweet_found = True
            userID = tranform_tweets(tweet, collection)
            # check if this user is already in the database
            if db[user_collection].find_one({"userID": userID}):
                continue
            else:
                new_user_count += 1
                new_user_found = True
                tranform_users(tweet, user_collection)
                # Users' tweets: Only scrape at most 100 tweets or the tweets within 6 months (180 days)
                for tweet in tweepy.Cursor(api.user_timeline, id=userID, tweet_mode='extended').items(100):
                    created = tweet.created_at
                    if (created < datetime.now() - timedelta(days=180)) or (
                    db[collection].find_one({"tweetID": tweet.id_str})):
                        break
                    else:
                        tranform_tweets(tweet, collection)
    if new_tweet_found == False and new_user_found == False:
        print('no new tweets or users found at: ' + str(datetime.now()))
    elif new_tweet_found == True and new_user_found == False:
        print(str(new_tweet_count) + ' new tweets found and no new users found at: ' + str(datetime.now()))
    elif new_tweet_found == True and new_user_found == True:
        print(str(new_tweet_count) + ' new tweets found and ' + str(new_user_count) + ' new users found at: ' + str(
            datetime.now()))
    elif new_tweet_found == False and new_user_found == True:
        print('no new tweets found and ' + str(new_user_count) + ' new users found at: ' + str(datetime.now()))
    else:
        print('tweet query overflow')




def get_url(tweet):
     return 'https://twitter.com/twitter/statuses/' + tweet.id_str






api = initialize_api()
places = api.geo_search(query=searchCountry, granularity='country')
for place in places:
    if place.full_name == searchCountry:
        place_obj = place
        place_id = place.id
print(f"Collect data with keywords {query} from {since} to {until} in {place_obj.name}({place_id})")
print(f"Data collected will be put into collection {collection}")
collect()

if(datetime.now().hour != 8):
    print('script ran at the wrong time')
