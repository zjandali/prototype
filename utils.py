"""
preprocess-twitter.py

python preprocess-twitter.py "Some random text with #hashtags, @mentions and http://t.co/kdjfkdjf (links). :)"

Script for preprocessing tweets by Romain Paulus
with small modifications by Jeffrey Pennington
with translation to Python by Motoki Wu

Translation of Ruby script to create features for GloVe vectors for Twitter data.
http://nlp.stanford.edu/projects/glove/preprocess-twitter.rb
"""
import regex as re
import tweepy

FLAGS = re.MULTILINE | re.DOTALL


def aggregateUpper(hashtag_list):
    hashtag_list_copy = hashtag_list
    length = [len(i) for i in hashtag_list_copy]
    if length[0]==0:
        hashtag_list_copy.pop(0)
        length.pop(0) 
    change = True
    try:
        while change:
            pos = length.index(1)
            if length[pos+1]==1:
                hashtag_list_copy[pos] = hashtag_list_copy[pos]+hashtag_list_copy[pos+1]
                hashtag_list_copy.pop(pos+1)
                length.pop(pos+1)
                change = True
            else:
                change = False
    except:
        pass
    return hashtag_list_copy

def hashtag(text):
    text = text.group()
    hashtag_body = text[1:]
    if hashtag_body.isupper():
        result = " {} ".format(hashtag_body.lower())
    else:
        result = " ".join(["<hashtag>"] + aggregateUpper(re.split(r"(?=[A-Z])", hashtag_body, flags=FLAGS)))  # add aggregateUpper Function
    return result
    
def allcaps(text):
    text = text.group()
    return text.lower() + " <allcaps>"

def tokenize(text):
    # Different regex parts for smiley faces
    eyes = r"[8:=;]"
    nose = r"['`\-]?"

    # function so code less repetitive
    def re_sub(pattern, repl):
        return re.sub(pattern, repl, text, flags=FLAGS)

    text = re_sub(r"https?:\/\/\S+\b|www\.(\w+\.)+\S*", "<url>")
    text = re_sub(r"@\w+", '<user>')
    # text = re_sub(r"{}{}[)dD]+|[)dD]+{}{}".format(eyes, nose, nose, eyes), "<smile>")
    # text = re_sub(r"{}{}p+".format(eyes, nose), "<lolface>")
    # text = re_sub(r"{}{}\(+|\)+{}{}".format(eyes, nose, nose, eyes), "<sadface>")
    # text = re_sub(r"{}{}[\/|l*]".format(eyes, nose), "<neutralface>")
    text = re_sub(r"/"," / ")
    # text = re_sub(r"<3","<heart>")
   # text = re_sub(r"[-+]?[.\d]*[\d]+[:,.\d]*", "<number>") # defunction number
    text = re_sub(r"#\S+", hashtag)
    text = re_sub(r"([!?.]){2,}", r"\1 <repeat>")
    text = re_sub(r"\b(\S*?)(.)\2{2,}\b", r"\1\2 <elong>")

    ## -- I just don't understand why the Ruby script adds <allcaps> to everything so I limited the selection.
    # text = re_sub(r"([^a-z0-9()<>'`\-]){2,}", allcaps)
    # text = re_sub(r"([A-Z]){2,}", allcaps)   # defunction <allcap>

    return text.lower()

def get_keys():
    keys = {}
    with open("apikeys.txt") as f:
        api_key = f.read().split("\n")
    keys['consumer key'] = api_key[0]
    keys['consumer secret'] = api_key[1]
    keys['access token'] = api_key[2]
    keys['access token secret'] = api_key[3]
    return keys



def domain(url):
    pattern = r"https?://([\w.-]+)/?"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return

def initialize_api():
    keys = get_keys()
    auth = tweepy.OAuthHandler(keys['consumer key'], keys['consumer secret'])
    auth.set_access_token(keys['access token'], keys['access token secret'])
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return api

