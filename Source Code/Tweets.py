from Profile import *
from pyrfc3339 import generate, parse
from datetime import *
import pytz
import unicodedata
import csv
import json
from Extraction import *

#Tweets class is a type of extraction. It takes the responsability to retrieve all the tweets and attributes in the date interval specified by user.
class Tweets(Extraction):

    def __init__(self, type, end_date, start_date, list, oauth, path, type_attributes, delay = 0):
        super().__init__(list, delay)
        self.path = path
        self.start_date = start_date
        self.end_date = end_date
        self.oauth = oauth
        self.type = type
        self.type_attributes = type_attributes

    # Return all the profiles in the specified list
    def get_list_members(self):
        search_url = "https://api.twitter.com/1.1/lists/members.json"
        query_params = {'list_id': self.list.get_list(), 'count':5000}
        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
        return json_response

    # Get full tweets instead of truncated tweets
    def get_full_tweets(self, mencionados):
        ids = ""
        for mencionado in mencionados:
            ids += mencionado
            ids += ","
        search_url = "https://api.twitter.com/1.1/statuses/lookup.json"
        query_params = {"id": ids[:len(ids) - 1]}
        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
        return json_response

    # Split the list in "wanted_parts" parts
    def split_list(self, alist, wanted_parts=1):
        length = len(alist)
        return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts]
                for i in range(wanted_parts)]

    # Remove points in string
    def remove_points(self, s):
        aux = ""
        for letter in s:
            if(letter == ":"):
                aux += "_"
            else:
                aux += letter
        return aux

    # Execute the extraction
    def execute_tweets(self, communication):

        print("EXECUTE TWEETS")
        print("--------------------------------------------------------------------------------------")
        print("Retrieving list members...")
        # Get all the profiles in the list ID specified
        response = self.get_list_members()
        print("List members are the following:")
        for profile in response["users"]:
            user = Profile(profile["screen_name"], profile["id"], profile["followers_count"], profile["friends_count"], profile["location"],profile["description"], profile["created_at"])
            self.list.add_profile(user)
            print(user.screen_name)
        print("Time interval: ", self.start_date, " to ", self.end_date)
        print("--------------------------------------------------------------------------------------")
        member = 0
        now = datetime.now()
        dt_string = now.strftime("%H:%M:%S")
        aux = self.remove_points(dt_string)
        name = self.path + "/" + "T (" + self.start_date[:10] + "-" + aux + ")(" + self.end_date[:10] + "-" + aux + ").csv"
        # Create a .csv file with "name" name in the current project path.
        with open(name, "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(element for element in self.type_attributes)
            while member < len(self.list.profiles):
                # Iterate all the members in the list and retrieve their Tweets
                user = self.list.get_profile(member)
                print("Retrieving Tweets of: ", user.screen_name)
                id_tweets = []
                aux = "from:" + user.screen_name + " -is:reply"
                query_params = {'query': aux, 'tweet.fields': 'created_at,author_id,entities','expansions': 'referenced_tweets.id.author_id,entities.mentions.username'}
                # Check if credentials are OAuth1 or OAuth2
                if(hasattr(self.oauth,'get_tokens') and callable(self.oauth.get_tokens)):
                    search_url = "https://api.twitter.com/2/tweets/search/recent"
                    query_params["max_results"] = 100
                else:
                    search_url = "https://api.twitter.com/2/tweets/search/all"
                    query_params["max_results"] = 500
                    query_params["start_time"] = self.start_date
                    query_params["end_time"] = self.end_date

                # Connect to the API
                json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                if ("data" in json_response):
                    for tweet in json_response["data"]:
                        if (not "referenced_tweets" in tweet):
                            id_tweets.append(tweet["id"])
                        else:
                            if ("quoted" in tweet["referenced_tweets"][0]["type"]):
                                id_tweets.append(tweet["id"])
                            if ("retweeted" in tweet["referenced_tweets"][0]["type"]):
                                id_tweets.append(tweet["id"])
                    if ("next_token" in json_response["meta"]):
                        # Obtain the token to acces the next data page if exists
                        while json_response["meta"]["next_token"] != 0:
                            query_params['next_token'] = json_response["meta"]["next_token"]
                            json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                            if ("data" in json_response):
                                for tweet in json_response["data"]:
                                    if (not "referenced_tweets" in tweet):
                                        id_tweets.append(tweet["id"])
                                    else:
                                        if ("quoted" in tweet["referenced_tweets"][0]["type"]):
                                            id_tweets.append(tweet["id"])
                                        if ("retweeted" in tweet["referenced_tweets"][0]["type"]):
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
                                elif(attribute == "user_description"):
                                    normal = unicodedata.normalize('NFKD', full_tweet["user"]["description"]).encode('ASCII', 'ignore')
                                    utf8string = normal.decode("utf-8")
                                    row.append(utf8string)
                                elif(attribute == "user_followers"):
                                    row.append(full_tweet["user"]["followers_count"])
                                elif (attribute == "user_followees"):
                                    row.append(full_tweet["user"]["friends_count"])
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
                            # Write row for each Tweet retrieved
                            writer.writerow(element for element in row)
                progresso = (member + 1) / len(self.list.profiles)
                # Communicate progress to Feedback window
                communication.sig.emit(progresso * 100)
                # Move to next member
                member += 1
                print("---------------------------------------------")
            print("---------------------------------------------------------------------------------------------------------------------")
        print("Saving the extraction into: ", name)
        # Communicate to Feedback the extraction finish
        communication.sig.emit(9999)
