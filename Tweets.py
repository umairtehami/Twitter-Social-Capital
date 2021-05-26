from Profile import *
from pyrfc3339 import generate, parse
from datetime import *
import pytz
import unicodedata
import csv
from Extraction import *

class Tweets(Extraction):

    def __init__(self, type, days, list, oauth, path, type_attributes, delay = 0):
        super().__init__(list, delay)
        self.path = path
        self.start_date = (datetime.now(timezone.utc).astimezone() - timedelta(days=days)).isoformat()
        self.end_date = datetime.now(timezone.utc).astimezone().isoformat()
        self.oauth = oauth
        self.days = days
        self.type = type
        self.type_attributes = type_attributes
        print(self.type_attributes)

    def get_list_members(self):
        search_url = "https://api.twitter.com/1.1/lists/members.json"
        query_params = {'list_id': self.list.get_list(), 'count':5000}
        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
        return json_response

    def get_full_tweets(self, mencionados):
        ids = ""
        for mencionado in mencionados:
            ids += mencionado
            ids += ","
        search_url = "https://api.twitter.com/1.1/statuses/lookup.json"
        query_params = {"id": ids[:len(ids) - 1]}
        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
        return json_response

    def split_list(self, alist, wanted_parts=1):
        length = len(alist)
        return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts]
                for i in range(wanted_parts)]

    def execute_tweets(self, communication):

        response = self.get_list_members()
        for profile in response["users"]:
            user = Profile(profile["screen_name"], profile["id"], profile["followers_count"], profile["friends_count"], profile["location"],profile["description"], profile["created_at"])
            self.list.add_profile(user)

        member = 0
        name = self.path + "/" + "T (" + self.start_date[:10] + ")(" + self.end_date[:10] + ").csv"
        print(name)
        with open(name, "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(element for element in self.type_attributes)
            while member < len(self.list.profiles):
                user = self.list.get_profile(member)
                print(user.screen_name, self.start_date)
                id_tweets = []
                aux = "from:" + user.screen_name + " -is:reply"
                start = generate((datetime.now(timezone.utc).astimezone() - timedelta(days=self.days, hours=1)).replace(tzinfo=pytz.utc))
                print(start)
                query_params = {'query': aux, 'tweet.fields': 'created_at,author_id,entities','expansions': 'referenced_tweets.id.author_id,entities.mentions.username'}
                if(hasattr(self.oauth,'get_tokens') and callable(self.oauth.get_tokens)):
                    print("OAuth1")
                    search_url = "https://api.twitter.com/2/tweets/search/recent"
                    query_params["max_results"] = 100
                else:
                    print("OAuth2")
                    search_url = "https://api.twitter.com/2/tweets/search/all"
                    query_params["max_results"] = 500
                    query_params["start_time"] = start

                json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                if ("data" in json_response):
                    for tweet in json_response["data"]:
                        if (not "referenced_tweets" in tweet):
                            print("ORIGINAL TWEET")
                            print(tweet["text"])
                            id_tweets.append(tweet["id"])
                        else:
                            if ("quoted" in tweet["referenced_tweets"][0]["type"]):
                                print("RETWEET WITH TEXT")
                                print(tweet["text"])
                                print("----------")
                                id_tweets.append(tweet["id"])
                            if ("retweeted" in tweet["referenced_tweets"][0]["type"]):
                                print("RETWEET")
                                print(tweet["text"])
                                print("----------")
                                id_tweets.append(tweet["id"])
                    if ("next_token" in json_response["meta"]):
                        while json_response["meta"]["next_token"] != 0:
                            query_params['pagination_token'] = json_response["meta"]["next_token"]
                            json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                            for tweet in json_response["data"]:
                                if (not "referenced_tweets" in tweet):
                                    print("ORIGINAL TWEET")
                                    print(tweet["text"])
                                    id_tweets.append(tweet["id"])
                                else:
                                    if ("quoted" in tweet["referenced_tweets"][0]["type"]):
                                        print("RETWEET WITH TEXT")
                                        print(tweet["text"])
                                        print("----------")
                                        id_tweets.append(tweet["id"])
                                    if ("retweeted" in tweet["referenced_tweets"][0]["type"]):
                                        print("RETWEET")
                                        print(tweet["text"])
                                        print("----------")
                                        id_tweets.append(tweet["id"])
                            if (not "next_token" in json_response["meta"]):
                                break
                if (len(id_tweets) > 0):
                    cantidad_listas = (int)(len(id_tweets) / 99)
                    listas = self.split_list(id_tweets, wanted_parts=cantidad_listas + 1)
                    for lista in listas:
                        json_response = self.get_full_tweets(lista)
                        for full_tweet in json_response:
                            row = []
                            for attribute in self.type_attributes:
                                if(attribute == "author"):
                                    row.append(full_tweet["user"]["screen_name"])
                                elif (attribute == "date"):
                                    row.append(full_tweet["created_at"])
                                elif (attribute == "favorites"):
                                    row.append(full_tweet["favorite_count"])
                                elif (attribute == "retweets"):
                                    row.append(full_tweet["retweet_count"])
                                elif (attribute == "number_mentions"):
                                    aux = 0
                                    if ("user_mentions" in full_tweet["entities"]):
                                        for mention in full_tweet["entities"]["user_mentions"]:
                                            aux += 1
                                    row.append(aux)
                                elif (attribute == "location"):
                                    if(full_tweet["place"] == None):
                                        row.append("NA")
                                    else:
                                        row.append(full_tweet["place"]["name"])
                                elif (attribute == "text"):
                                    normal = unicodedata.normalize('NFKD', full_tweet["text"]).encode('ASCII', 'ignore')
                                    utf8string = normal.decode("utf-8")
                                    row.append(utf8string)
                                elif (attribute == "sensitive"):
                                    try:
                                        if ("possibly_sensitive" in full_tweet):
                                            row.append(full_tweet["possibly_sensitive"])
                                        else:
                                            row.append(full_tweet["retweeted_status"]["possibly_sensitive"])
                                    except:
                                        row.append("NA")
                                elif (attribute == "tweet_url"):
                                    aux = "https://twitter.com/" + user.screen_name + "/statuses/" + full_tweet["id_str"]
                                    row.append(aux)
                                elif (attribute == "hashtag"):
                                    aux = ""
                                    for hashtag in full_tweet["entities"]["hashtags"]:
                                        normal = unicodedata.normalize('NFKD', hashtag["text"]).encode('ASCII','ignore')
                                        aux += "#"
                                        utf8string = normal.decode("utf-8")
                                        aux += utf8string
                                        aux += ", "
                                    if (aux == ""):
                                        row.append("NA")
                                    else:
                                        row.append(aux[:len(aux)-2])
                                elif (attribute == "urls"):
                                    aux = ""
                                    if ("urls" in full_tweet["entities"]):
                                        for url in full_tweet["entities"]["urls"]:
                                            aux += url["expanded_url"]
                                            aux += ", "
                                    if (aux == ""):
                                        row.append("NA")
                                    else:
                                        row.append(aux[:len(aux) - 2])
                                elif (attribute == "users_mentioned"):
                                    aux = ""
                                    if("user_mentions" in full_tweet["entities"]):
                                        for mention in full_tweet["entities"]["user_mentions"]:
                                            aux += "@"
                                            aux += mention["screen_name"]
                                            aux += ", "
                                    if (aux == ""):
                                        row.append("NA")
                                    else:
                                        row.append(aux[:len(aux) - 2])
                            writer.writerow(element for element in row)
                progresso = (member + 1) / len(self.list.profiles)
                communication.sig.emit(progresso * 100)
                member += 1
                print("---------------------------------------------")
            print("---------------------------------------------------------------------------------------------------------------------")

        communication.sig.emit(9999)
