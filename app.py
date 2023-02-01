from flask import Flask, render_template, url_for, redirect, abort, request, session
from flask_session import Session
from datetime import datetime, date, timedelta
from plots import *
# from hashtag_map import createTopTenHashtagGraph
import db
from users import User
import pickle
import os
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


app.static_folder = 'static'
routes_analysis = ("trend-analysis","influencer-analysis","benchmark-analysis","test","google-index")
routes_doc = ("guidance","methodology")


def load_user(email_address):
	data = db.users_collection.find_one({"email": email_address})
	if data:
		return User(data['email'], data['password'], data['firstname'], data['lastname'])
	else:
		return None

def transfrom_timerange(timerange):
	toDate = str((datetime.utcnow()-timedelta(days=3)).date())
	if timerange == "past-week":
		fromDate = str((datetime.utcnow()-timedelta(days=7+3)).date())
	elif timerange == "past-month":
		fromDate = str((datetime.utcnow()-timedelta(days=30+3)).date())
	elif timerange == "past-year":
		fromDate = str((datetime.utcnow()-timedelta(days=360+3)).date())
	return fromDate, toDate


def init_setting():
	keyword = "stopasianhate"
	defaultFromDate = "2021-06-07"
	defaultToDate = "2021-06-10"
	sample = True
	step2 = False
	return keyword, defaultFromDate, defaultToDate, sample, step2

def sample_case():
	path = "static/init"
	tweetCount = pickle.load(open(path+"/tweetCount.p",'rb'))
	toptweets = pickle.load(open(path+"/toptweets.p",'rb'))
	hashtags = pickle.load(open(path+"/hashtags.p",'rb'))
	emojis = pickle.load(open(path+"/emojis.p",'rb'))
	domains = pickle.load(open(path+"/domains.p",'rb'))
	urls = pickle.load(open(path+"/urls.p",'rb'))
	mentions = pickle.load(open(path+"/mentions.p",'rb'))
	wordcloud = pickle.load(open(path+"/wordcloud.p",'rb'))
	dhahstags = pickle.load(open(path+"/dhashtags.p",'rb'))
	trends = pickle.load(open(path+"/trends.p",'rb'))
	nx = pickle.load(open(path+"/nx.p",'rb'))
	return tweetCount, toptweets, hashtags, emojis, domains, urls, mentions, wordcloud, dhahstags, trends, nx


@app.route("/")
def home():	
	return redirect("/login", code=302)


@app.route("/init")
def init():
	keyword, fromDate, toDate, sample, step2 = init_setting()
	path = "static/init"
	for f in os.listdir(path):
		os.remove(os.path.join(path, f))
	hashtagList = generate_list("hashtags",keyword,fromDate,toDate)
	pickle.dump(counts(keyword,fromDate,toDate),open(path+"/tweetCount.p",'wb'))
	pickle.dump(top_count(keyword,fromDate,toDate,3,type="urls"),open(path+"/toptweets.p",'wb'))
	pickle.dump(plot_count_v(hashtagList),open(path+"/hashtags.p",'wb'))
	pickle.dump(plot_count_h(generate_list("emojis",keyword,fromDate,toDate)),open(path+"/emojis.p",'wb'))
	pickle.dump(plot_count_h(generate_list("urlDomains",keyword,fromDate,toDate)),open(path+"/domains.p",'wb'))
	pickle.dump(plot_count_h(generate_list("urls",keyword,fromDate,toDate)),open(path+"/urls.p",'wb'))
	pickle.dump(plot_count_h(generate_list("mentions",keyword,fromDate,toDate)),open(path+"/mentions.p",'wb'))
	pickle.dump(plot_wordcloud(top_count(keyword,fromDate,toDate,0.1,type="tweets")),open(path+"/wordcloud.p",'wb'))
	pickle.dump(plot_bar_chart_race("hashtags", keyword, fromDate, toDate),open(path+"/dhashtags.p",'wb'))
	pickle.dump(plot_topical_trend("favoriteCount", keyword, fromDate, toDate),open(path+"/trends.p",'wb'))
	pickle.dump(plot_hashtag_nx(hashtagList, keyword),open(path+"/nx.p",'wb'))
	return redirect("/login", code=302)


### Login Management
@app.route("/login", methods=['GET', 'POST'])
def login():
	error = None
	if session.get("email"):
		return redirect("dashboard")
	else:
		if request.method == 'POST':
			email = request.form['Email']
			password = request.form['Password']
			user = load_user(email)
			if user and User.check_password(password, user.password):
				session["email"] = user.email
				session["firstname"] = user.firstname
				session["lastname"] = user.lastname
				return redirect("dashboard")
			else:
				error = "Invalid email or password"
		return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session["email"] = None
    return redirect("/login")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
	error = None
	if request.method == 'POST':
		firstname = request.form['FirstName']
		lastname = request.form['LastName']
		email = request.form['Email']
		orgname = request.form['OrgName']
		password = request.form['Password']
		document = {
			"email": email,
			"password": password,
			"firstname": firstname,
			"lastname": lastname,
			"orgname": orgname
		}
		check_user = load_user(email)
		if not check_user:
			db.users_collection.insert_one(document)
			session["email"] = email
			session["firstname"] = firstname
			session["lastname"] = lastname
			return redirect("dashboard")
		else:
			error = "This email address has signed up."
	return render_template("signup.html", error=error)


### Dashboard
@app.route("/dashboard")
def welcome():
	if session.get("email"): # check if the user is still in the session
		firstname = session.get("firstname")
		lastname = session.get("lastname")
		return render_template("welcome.html", 
								route="Welcome!", 
								firstname=firstname,
								lastname=lastname)
	else:
		return redirect("/")

@app.route("/dashboard/<route>", methods=['GET', 'POST'])
def dashboard(route):
	if session.get("email"): # check if the user is still in the session
		firstname = session.get("firstname")
		lastname = session.get("lastname")
		if route in routes_doc:
			route_clean = " ".join([word.capitalize() for word in route.split("-")])
			return render_template(route+".html",
								   route=route_clean, 
								   fistname=firstname,
								   lastname=lastname)
		elif route in routes_analysis:
			route_clean = " ".join([word.capitalize() for word in route.split("-")])
			plot_jsons = []
			if route == "trend-analysis":
				stopDate = str((datetime.utcnow()-timedelta(days=3)).date())
				startDate = str((datetime.utcnow()-timedelta(days=365)).date())
				keyword, fromDate, toDate, sample, step2 = init_setting()
				tweetCount, topTweet, plotHashtag, plotEmoji, plotDomain, plotUrl, plotMention, plotWordCloud, plotBarRace, plotTrend, plotNx = sample_case()
				error = ""

				if request.method == 'POST':
					print(counts(keyword,fromDate,toDate))
					keyword = request.form['keyword-selector']
					timerange = request.form['timerange-selector']
					sample = False
					step2 = True
					if timerange == "customized-time":
						fromDate = request.form['from-date']
						toDate = request.form['to-date']
					else:
						fromDate, toDate = transfrom_timerange(timerange)

					# input validation
					if counts(keyword,fromDate,toDate) < 100:
						error = "Not enough data in the database to form a solid report."
					if error:
						keyword, fromDate, toDate, sample, step2 = init_setting()
					else:
						hashtagList = generate_list("hashtags",keyword,fromDate,toDate)

						tweetCount = counts(keyword,fromDate,toDate)
						topTweet = top_count(keyword,fromDate,toDate,3,type="urls")
						plotHashtag = plot_count_v(hashtagList)
						plotEmoji = plot_count_h(generate_list("emojis",keyword,fromDate,toDate))
						plotDomain = plot_count_h(generate_list("urlDomains",keyword,fromDate,toDate))
						plotUrl = plot_count_h(generate_list("urls",keyword,fromDate,toDate))
						plotMention = plot_count_h(generate_list("mentions",keyword,fromDate,toDate))
						plotWordCloud = plot_wordcloud(top_count(keyword,fromDate,toDate,0.3,type="tweets"))
						plotBarRace = plot_bar_chart_race("hashtags", keyword, fromDate, toDate)
						plotTrend = plot_topical_trend("favoriteCount", keyword, fromDate, toDate)
						plotNx = plot_hashtag_nx(hashtagList, keyword)
						
				input_values = [["stopasianhate", "humanrights"],startDate,stopDate,error,step2]
				intro = [tweetCount,keyword,fromDate,toDate,sample]
				
				return render_template(route+".html", 
										route=route_clean, 
										firstname=firstname, 
										lastname=lastname,
										input_values=input_values,
										intro = intro,
										topTweet = topTweet,
										plotHashtag = plotHashtag,
										plotEmoji = plotEmoji,
										plotDomain = plotDomain,
										plotUrl = plotUrl,
										plotMention = plotMention,
										plotWordCloud = plotWordCloud,
										plotBarRace = plotBarRace,
										plotTrend = plotTrend,
										plotNx = plotNx,
										)
			
			elif route == "influencer-analysis":
				path = "static/init"
				nx = pickle.load(open(path+"/nx.p",'rb'))
				return render_template(route+".html", 
									   route=route_clean, 
									   nx=nx)
			
			else:
				return render_template(route+".html", route=route_clean)
		else:
			abort(404)
	else:
		return redirect("/")

@app.route('/users/password_reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
	if request.method == 'POST':
		session['email']


	# Do something
	elif request.method == 'GET':
		return


def change_password():
	return

if __name__ == "__main__":
	app.run(debug=True)