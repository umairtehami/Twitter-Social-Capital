from Profile import *
import time as t
from Relation import *
from requests_oauthlib import OAuth1Session
from pyrfc3339 import generate, parse
import pytz
from datetime import *
import csv
from Extraction import *

class Unweighted(Extraction):

    def __init__(self, type, list, consumer_key, consumer_secret, access_token, access_secret_token, path, delay=0):
        super().__init__(list, delay)
        self.type = type
        self.path = path
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_secret_token = access_secret_token


    def connect_to_endpoint(self, oauth, s, params):
        response = oauth.get(s, params=params)
        if response.status_code != 200:
            print(response.status_code)
            while response.status_code != 200:
                print("Esperando 1 min")
                print(response.text)
                t.sleep(60)
                response = oauth.get(s, params=params)
        return response.json()

    def get_list_members(self,oauth):
        search_url = "https://api.twitter.com/1.1/lists/members.json"
        query_params = {'list_id': self.list.get_list(), 'count':5000}
        json_response = self.connect_to_endpoint(oauth, search_url, query_params)
        return json_response

    def get_followers(self, oauth, user):
        search_url = "https://api.twitter.com/1.1/followers/ids.json"
        relations = []
        query_params = {'screen_name': user.screen_name, 'count': 5000}
        json_response = self.connect_to_endpoint(oauth, search_url, query_params)
        if("ids" in json_response):
            for id in json_response["ids"]:
                name = self.list.existing_profile_name(id)
                if(name != ""):
                    print("seguido por " + name)
                    relation = Relation(name, user.screen_name, 50, "es seguidor de")
                    relations.append(relation)
                else:
                    relation = Relation(id, user.screen_name, 50, "es seguidor de")
                    relations.append(relation)
            while json_response["next_cursor"] != 0:
                query_params['cursor'] = json_response["next_cursor"]
                json_response = self.connect_to_endpoint(oauth, search_url, query_params)
                for id in json_response["ids"]:
                    name = self.list.existing_profile_name(id)
                    if (name != ""):
                        print("seguido por " + name)
                        relation = Relation(name, user.screen_name, 50, "es seguidor de")
                        relations.append(relation)
                    else:
                        relation = Relation(id, user.screen_name, 50, "es seguidor de")
                        relations.append(relation)
        return relations

    def get_friends(self, oauth, user):
        search_url = "https://api.twitter.com/1.1/friends/ids.json"
        relations = []
        query_params = {'screen_name': user.screen_name, 'count': 5000}
        json_response = self.connect_to_endpoint(oauth, search_url, query_params)
        if ("ids" in json_response):
            for id in json_response["ids"]:
                name = self.list.existing_profile_name(id)
                if (name != ""):
                    print("seguidor de " + name)
                    relation = Relation(user.screen_name, name, 50, "es seguidor de")
                    relations.append(relation)
                else:
                    relation = Relation(user.screen_name, id, 50, "es seguidor de")
                    relations.append(relation)
            while json_response["next_cursor"] != 0:
                query_params['cursor'] = json_response["next_cursor"]
                json_response = self.connect_to_endpoint(oauth, search_url, query_params)
                for id in json_response["ids"]:
                    name = self.list.existing_profile_name(id)
                    if (name != ""):
                        print("seguidor de " + name)
                        relation = Relation(user.screen_name, name, 50, "es seguidor de")
                        relations.append(relation)
                    else:
                        relation = Relation(user.screen_name, id, 50, "es seguidor de")
                        relations.append(relation)
        return relations

    def execute_followers(self, communication):

        consumer_key = self.consumer_key
        consumer_secret = self.consumer_secret
        access_token = self.access_token
        access_token_secret = self.access_secret_token

        # Make the request
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )

        response = self.get_list_members(oauth)

        for profile in response["users"]:
            user = Profile(profile["screen_name"], profile["id"], profile["followers_count"], profile["friends_count"],profile["location"], profile["description"], profile["created_at"])
            self.list.add_profile(user)

        relations = []
        member = 0
        while member < len(self.list.profiles):
            print("Aaaaaaaaaaaaaaaaaaa")
            user = self.list.get_profile(member)
            print(user.screen_name)
            followers = self.get_followers(oauth,user)
            friends = self.get_friends(oauth,user)
            relations += (followers + friends)
            print(len(friends), len(followers))
            t.sleep(60)
            progresso = (member + 1) / len(self.list.profiles)
            communication.sig.emit(progresso * 100)
            member += 1
            print("---------------------------------------------")

        name = self.path + "/" + "F WN.csv"
        with open(name, "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(["Source", "Target", "Weight", "Label", "Type"])
            for relation in relations:
                writer.writerow([relation.source, relation.target, relation.weight, relation.label, relation.type])

        communication.sig.emit(9999)


    def get_mentions(self, id, includes):
        for mention in includes["users"]:
            if(mention["id"] == id):
                return mention["username"]

    def execute_mentions(self, communication):

        consumer_key = self.consumer_key
        consumer_secret = self.consumer_secret
        access_token = self.access_token
        access_token_secret = self.access_secret_token

        print(self.consumer_key,self.consumer_secret,self.access_token,self.access_secret_token)

        # Make the request
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )

        response = self.get_list_members(oauth)

        for profile in response["users"]:
            user = Profile(profile["screen_name"], profile["id"], profile["followers_count"], profile["friends_count"],profile["location"], profile["description"], profile["created_at"])
            self.list.add_profile(user)

        relations = []
        member = 0
        while member < len(self.list.profiles):
            user = self.list.get_profile(member)
            print(user.screen_name)
            search_url = "https://api.twitter.com/2/tweets/search/recent"
            # Mentions --------------------------------------------------------------------------------- A -> B
            aux = "@" + user.screen_name + " -is:reply -is:retweet"
            query_params = {'query': aux, 'tweet.fields': 'created_at,author_id,in_reply_to_user_id', 'expansions': 'author_id', 'user.fields': 'username', 'max_results': 100}
            json_response = self.connect_to_endpoint(oauth, search_url, query_params)
            if ("data" in json_response):
                for mencionador in json_response["data"]:
                    r = self.get_mentions(mencionador["author_id"],json_response["includes"])
                    if (not self.list.existing_profile(r)):
                        relation = Relation(r, user.screen_name, 50, "ha mencionado a")
                        if (not relation.existing_relation(relations)):
                            relations.append(relation)
                if ("next_token" in json_response["meta"]):
                    while json_response["meta"]["next_token"] != 0:
                        query_params['next_token'] = json_response["meta"]["next_token"]
                        json_response = self.connect_to_endpoint(oauth, search_url, query_params)
                        for mencionador in json_response["data"]:
                            r = self.get_mentions(mencionador["author_id"], json_response["includes"])
                            if (not self.list.existing_profile(r)):
                                relation = Relation(r, user.screen_name, 50, "ha mencionado a")
                                if(not relation.existing_relation(relations)):
                                    relations.append(relation)
                        if (not "next_token" in json_response["meta"]):
                            break
            # User timeline - -------------------------------------------------------------------------------- B -> A
            search_url = "https://api.twitter.com/2/users/{}/tweets".format(user.id)
            start = generate((datetime.now(timezone.utc).astimezone() - timedelta(days=7)).replace(tzinfo=pytz.utc))
            print(start)
            query_params = {"tweet.fields": "created_at,author_id,entities","expansions": "referenced_tweets.id.author_id,entities.mentions.username","max_results": 100, "start_time": start}
            json_response = self.connect_to_endpoint(oauth, search_url, query_params)
            if ("data" in json_response):
                for tweet in json_response["data"]:
                    if(not "referenced_tweets" in tweet):
                        if ("entities" in tweet):
                            if ("mentions" in tweet["entities"]):
                                for mention in tweet["entities"]["mentions"]:
                                    relation = Relation(user.screen_name, mention["username"], 50,"ha mencionado a")
                                    if (not relation.existing_relation(relations)):
                                        relations.append(relation)
                if ("next_token" in json_response["meta"]):
                    while json_response["meta"]["next_token"] != 0:
                        query_params['pagination_token'] = json_response["meta"]["next_token"]
                        json_response = self.connect_to_endpoint(oauth, search_url, query_params)
                        for tweet in json_response["data"]:
                            if (not "referenced_tweets" in tweet):
                                if ("entities" in tweet):
                                    if ("mentions" in tweet["entities"]):
                                        for mention in tweet["entities"]["mentions"]:
                                            relation = Relation(user.screen_name, mention["username"], 50,"ha mencionado a")
                                            if (not relation.existing_relation(relations)):
                                                relations.append(relation)
                        if (not "next_token" in json_response["meta"]):
                            break
            progresso = (member + 1) / len(self.list.profiles)
            communication.sig.emit(progresso * 100)
            member += 1
            print("---------------------------------------------")
        print("---------------------------------------------------------------------------------------------------------------------")
        start = generate((datetime.now(timezone.utc).astimezone() - timedelta(days=7)).replace(tzinfo=pytz.utc))
        end = generate((datetime.now(timezone.utc).astimezone()))
        print(start,end)
        name = self.path + "/" + "M WN (" + start[:10] + ")(" + end[:10] + ").csv"
        print(name)
        with open(name, "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(["Source", "Target", "Weight", "Label", "Type"])
            for relation in relations:
                writer.writerow([relation.source, relation.target, relation.weight, relation.label, relation.type])

        communication.sig.emit(9999)
