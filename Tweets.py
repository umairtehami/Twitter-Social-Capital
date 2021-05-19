from Profile import *
from Relation import *
import requests
from pyrfc3339 import generate, parse
from datetime import *
import pytz
import time as t
import csv
from Extraction import *

class Tweets(Extraction):

    def __init__(self, type, days, list, bearer_token, path, delay=0):
        super().__init__(list, delay)
        self.path = path
        self.start_date = (datetime.now(timezone.utc).astimezone() - timedelta(days=days)).isoformat()
        self.end_date = datetime.now(timezone.utc).astimezone().isoformat()
        self.bearer_token = bearer_token
        self.days = days
        self.type = type

    """def __init__(self, days, list, consumer_key, consumer_secret, access_token, access_secret_token, path, type = "OAuth1",delay=0):
        super().__init__(list, delay)
        self.path = path
        self.start_date = (datetime.now(timezone.utc).astimezone() - timedelta(days=days)).isoformat()
        self.end_date = datetime.now(timezone.utc).astimezone().isoformat()
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_secret_token = access_secret_token
        self.days = days
        self.type = type"""

    def create_headers(self,bearer_token):
        headers = {"Authorization": "Bearer {}".format(bearer_token)}
        return headers

    def connect_to_endpoint(self,url, headers, params):
        response = requests.request("GET", url, headers=headers, params=params)
        if response.status_code != 200:
            while response.status_code != 200:
                print("Esperando")
                print(response.text)
                t.sleep(60)
                response = requests.request("GET", url, headers=headers, params=params)
        return response.json()

    def get_list_members(self):
        search_url = "https://api.twitter.com/1.1/lists/members.json"
        query_params = {'list_id': self.list.get_list(), 'count':5000}
        headers = self.create_headers(self.bearer_token)
        json_response = self.connect_to_endpoint(search_url, headers, query_params)
        return json_response

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
            writer.writerow(["Empresa","Seguidores","Seguidos","Fecha de publicacion","Texto del tweet","Favoritos del tweet","Retweets del tweet","Hashtags del Tweet","Url's del tweet","Número de usuarios mencionados","Usuarios mencionados"])
            while member < len(self.list.profiles):
                user = self.list.get_profile(member)
                print(user.screen_name, self.start_date)
                str = ""
                search_url = "https://api.twitter.com/2/users/{}/tweets".format(user.id)
                start = generate((datetime.now(timezone.utc).astimezone() - timedelta(days=self.days)).replace(tzinfo=pytz.utc))
                print(start)
                query_params = {"tweet.fields": "created_at,author_id,entities","expansions": "referenced_tweets.id.author_id,entities.mentions.username","max_results": 100, "start_time": start}
                headers = self.create_headers(self.bearer_token)
                json_response = self.connect_to_endpoint(search_url, headers, query_params)
                if ("data" in json_response):
                    for tweet in json_response["data"]:
                        if ("referenced_tweets" in tweet):
                            if(not "replied_to" in tweet["referenced_tweets"][0]["type"]):
                                print(tweet)
                        else:
                            print(tweet)
                    if ("next_token" in json_response["meta"]):
                        while json_response["meta"]["next_token"] != 0:
                            query_params['pagination_token'] = json_response["meta"]["next_token"]
                            headers = self.create_headers(self.bearer_token)
                            json_response = self.connect_to_endpoint(search_url, headers, query_params)
                            for tweet in json_response["data"]:
                                print(tweet)
                                if ("referenced_tweets" in tweet):
                                    if (not "replied_to" in tweet["referenced_tweets"][0]["type"]):
                                        print(tweet)
                                else:
                                    print(tweet)
                            if (not "next_token" in json_response["meta"]):
                                break
                writer.writerow(str)
                progresso = (member + 1) / len(self.list.profiles)
                communication.sig.emit(progresso * 100)
                member += 1
                print("---------------------------------------------")
            print("---------------------------------------------------------------------------------------------------------------------")

        communication.sig.emit(9999)
