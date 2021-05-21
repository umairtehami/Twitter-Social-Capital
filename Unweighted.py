from Profile import *
import time as t
from Relation import *
from pyrfc3339 import generate, parse
import pytz
from datetime import *
import csv
from Extraction import *

class Unweighted(Extraction):

    def __init__(self, type, list, oauth, path, type_weigth, delay=0):
        super().__init__(list, delay)
        self.type = type
        self.path = path
        self.oauth = oauth
        self.type_weigth = type_weigth
        self.start_date = (datetime.now(timezone.utc).astimezone() - timedelta(days=7)).isoformat()
        self.end_date = datetime.now(timezone.utc).astimezone().isoformat()

    def get_list_members(self):
        search_url = "https://api.twitter.com/1.1/lists/members.json"
        query_params = {'list_id': self.list.get_list(), 'count':5000}
        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
        return json_response

    def get_followers(self, user):
        search_url = "https://api.twitter.com/1.1/followers/ids.json"
        relations = []
        query_params = {'screen_name': user.screen_name, 'count': 5000}
        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
        print(json_response)
        if(json_response != "error"):
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
                    json_response = self.oauth.connect_to_endpoint(search_url, query_params)
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
        else:
            return "error"

    def referenced_author(self,id, includes):
        for include in includes:
            if(include["id"] == id):
                return include["author_id"]

    def id_mentioned(self, username, includes):
        for user in includes:
            if(user["username"] == username):
                return user["id"]

    def get_friends(self, user):
        search_url = "https://api.twitter.com/1.1/friends/ids.json"
        relations = []
        query_params = {'screen_name': user.screen_name, 'count': 5000}
        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
        print(json_response)
        if (json_response != "error"):
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
                    json_response = self.oauth.connect_to_endpoint(search_url, query_params)
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
        else:
            return "error"

    def execute_followers(self, communication):

        print("execute_followers")
        response = self.get_list_members()

        for profile in response["users"]:
            user = Profile(profile["screen_name"], profile["id"], profile["followers_count"], profile["friends_count"],profile["location"], profile["description"], profile["created_at"])
            self.list.add_profile(user)

        relations = []
        member = 0
        while member < len(self.list.profiles):
            user = self.list.get_profile(member)
            print(user.screen_name)
            followers = self.get_followers(user)
            friends = self.get_friends(user)
            relations += (followers + friends)
            print(len(friends), len(followers))
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

    def execute_followers_weighted(self, communication):

        print("execute_followers_weighted")
        response = self.get_list_members()

        for profile in response["users"]:
            user = Profile(profile["screen_name"], profile["id"], profile["followers_count"], profile["friends_count"],profile["location"], profile["description"], profile["created_at"])
            self.list.add_profile(user)

        relations = []
        member = 0
        while member < len(self.list.profiles):
            user = self.list.get_profile(member)
            print(user.screen_name)
            followers = self.get_followers(user)
            friends = self.get_friends(user)
            relations += (followers + friends)
            print(len(friends), len(followers))
            search_url = "https://api.twitter.com/2/tweets/search/recent"
            if ("M" in self.type_weigth):
                print("M")
                # Mentions --------------------------------------------------------------------------------- A -> B
                aux = "@" + user.screen_name + " -is:reply -is:retweet"
                query_params = {'query': aux, 'tweet.fields': 'created_at,author_id,in_reply_to_user_id','max_results': 100}
                json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                if ("data" in json_response):
                    for mencionador in json_response["data"]:
                        print(mencionador["text"])
                        print("----------")
                        if (not self.list.existing_profile(mencionador["author_id"])):
                            relation = Relation(mencionador["author_id"], user.screen_name, 50, "ha mencionado a")
                            relation.existing_and_upgrade_relation(relations)
                    if ("next_token" in json_response["meta"]):
                        while json_response["meta"]["next_token"] != 0:
                            query_params['next_token'] = json_response["meta"]["next_token"]
                            json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                            for mencionador in json_response["data"]:
                                print(mencionador["text"])
                                print("----------")
                                if (not self.list.existing_profile(mencionador["author_id"])):
                                    relation = Relation(mencionador["author_id"], user.screen_name, 50, "ha mencionado a")
                                    relation.existing_and_upgrade_relation(relations)
                            if (not "next_token" in json_response["meta"]):
                                break
            if ("RP" in self.type_weigth):
                print("RP")
                # Replies --------------------------------------------------------------------------------- A -> B
                aux = "to:" + user.screen_name + " is:reply -is:retweet"
                query_params = {'query': aux,'tweet.fields': 'created_at,author_id,in_reply_to_user_id,referenced_tweets','max_results': 100}
                json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                if ("data" in json_response):
                    for respuesta in json_response["data"]:
                        if ("referenced_tweets" in respuesta):
                            if (respuesta["referenced_tweets"][0]["type"] == "replied_to"):
                                print(respuesta["text"])
                                print("----------")
                                if (not self.list.existing_profile(respuesta["author_id"])):
                                    relation = Relation(respuesta["author_id"], user.screen_name, 50, "ha mencionado a")
                                    relation.existing_and_upgrade_relation(relations)
                    if ("next_token" in json_response["meta"]):
                        while json_response["meta"]["next_token"] != 0:
                            query_params['next_token'] = json_response["meta"]["next_token"]
                            json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                            for respuesta in json_response["data"]:
                                if ("referenced_tweets" in respuesta):
                                    if (respuesta["referenced_tweets"][0]["type"] == "replied_to"):
                                        print(respuesta["text"])
                                        print("----------")
                                        if (not self.list.existing_profile(respuesta["author_id"])):
                                            relation = Relation(respuesta["author_id"], user.screen_name, 50,"ha mencionado a")
                                            relation.existing_and_upgrade_relation(relations)
                            if (not "next_token" in json_response["meta"]):
                                break
            if ("RT" in self.type_weigth):
                print("RT")
                # Retweets --------------------------------------------------------------------------------- A -> B
                aux = "retweets_of:" + user.screen_name
                query_params = {'query': aux,'tweet.fields': 'created_at,author_id,in_reply_to_user_id,referenced_tweets','max_results': 100}
                json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                if ("data" in json_response):
                    for respuesta in json_response["data"]:
                        print(respuesta["text"])
                        print("----------")
                        if (not self.list.existing_profile(respuesta["author_id"])):
                            relation = Relation(respuesta["author_id"], user.screen_name, 50, "ha mencionado a")
                            relation.existing_and_upgrade_relation(relations)
                    if ("next_token" in json_response["meta"]):
                        while json_response["meta"]["next_token"] != 0:
                            query_params['next_token'] = json_response["meta"]["next_token"]
                            json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                            for respuesta in json_response["data"]:
                                print(respuesta["text"])
                                print("----------")
                                if (not self.list.existing_profile(respuesta["author_id"])):
                                    relation = Relation(respuesta["author_id"], user.screen_name, 50, "ha mencionado a")
                                    relation.existing_and_upgrade_relation(relations)
                            if (not "next_token" in json_response["meta"]):
                                break
            # User timeline - -------------------------------------------------------------------------------- B -> A
            search_url = "https://api.twitter.com/2/users/{}/tweets".format(user.id)
            start = generate((datetime.now(timezone.utc).astimezone() - timedelta(days=7)).replace(tzinfo=pytz.utc))
            print(start)
            query_params = {"tweet.fields": "created_at,author_id,entities","expansions": "referenced_tweets.id.author_id,entities.mentions.username","max_results": 100, "start_time": start}
            json_response = self.oauth.connect_to_endpoint(search_url, query_params)
            if ("data" in json_response):
                for tweet in json_response["data"]:
                    if(not "referenced_tweets" in tweet):
                        if ("M" in self.type_weigth):
                            print("ORIGINAL TWEET")
                            if ("entities" in tweet):
                                if ("mentions" in tweet["entities"]):
                                    print(tweet["text"])
                                    print("----------")
                                    for mention in tweet["entities"]["mentions"]:
                                        print(mention["username"])
                                        id = self.id_mentioned(mention["username"],json_response["includes"]["users"])
                                        name = self.list.existing_profile_name(id)
                                        if(name != ""):
                                            if(name != user.screen_name):
                                                relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                                relation.existing_and_upgrade_relation(relations)
                                        else:
                                            relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                            relation.existing_and_upgrade_relation(relations)
                    else:
                        if ("RP" in self.type_weigth):
                            if("replied_to" in tweet["referenced_tweets"][0]["type"]):
                                print("REPLIED TO")
                                print(tweet["text"])
                                print("----------")
                                a = self.referenced_author(tweet["referenced_tweets"][0]["id"], json_response["includes"]["tweets"])
                                name = self.list.existing_profile_name(a)
                                if (name != ""):
                                    if (name != user.screen_name):
                                        relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                        relation.existing_and_upgrade_relation(relations)
                                else:
                                    relation = Relation(user.screen_name, a, 50, "ha mencionado a")
                                    relation.existing_and_upgrade_relation(relations)
                        if ("RT" in self.type_weigth):
                            if("quoted" in tweet["referenced_tweets"][0]["type"]):
                                print("RETWEET WITH TEXT")
                                print(tweet["text"])
                                print("----------")
                                a = self.referenced_author(tweet["referenced_tweets"][0]["id"],json_response["includes"]["tweets"])
                                name = self.list.existing_profile_name(a)
                                if (name != ""):
                                    if (name != user.screen_name):
                                        relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                        relation.existing_and_upgrade_relation(relations)
                                else:
                                    relation = Relation(user.screen_name, a, 50, "ha mencionado a")
                                    relation.existing_and_upgrade_relation(relations)
                                if ("entities" in tweet):
                                    if ("mentions" in tweet["entities"]):
                                        for mention in tweet["entities"]["mentions"]:
                                            print(mention["username"])
                                            id = self.id_mentioned(mention["username"],json_response["includes"]["users"])
                                            name = self.list.existing_profile_name(id)
                                            if (name != ""):
                                                if (name != user.screen_name):
                                                    relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                                    relation.existing_and_upgrade_relation(relations)
                                            else:
                                                relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                                relation.existing_and_upgrade_relation(relations)
                            if("retweeted" in tweet["referenced_tweets"][0]["type"]):
                                print("RETWEET")
                                print(tweet["text"])
                                print("----------")
                                a = self.referenced_author(tweet["referenced_tweets"][0]["id"],json_response["includes"]["tweets"])
                                name = self.list.existing_profile_name(a)
                                if (name != ""):
                                    if (name != user.screen_name):
                                        relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                        relation.existing_and_upgrade_relation(relations)
                                else:
                                    relation = Relation(user.screen_name, a, 50, "ha mencionado a")
                                    relation.existing_and_upgrade_relation(relations)
                if ("next_token" in json_response["meta"]):
                    while json_response["meta"]["next_token"] != 0:
                        query_params['pagination_token'] = json_response["meta"]["next_token"]
                        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                        for tweet in json_response["data"]:
                            if (not "referenced_tweets" in tweet):
                                if ("M" in self.type_weigth):
                                    print("ORIGINAL TWEET")
                                    if ("entities" in tweet):
                                        if ("mentions" in tweet["entities"]):
                                            print(tweet["text"])
                                            print("----------")
                                            for mention in tweet["entities"]["mentions"]:
                                                print(mention["username"])
                                                id = self.id_mentioned(mention["username"],json_response["includes"]["users"])
                                                name = self.list.existing_profile_name(id)
                                                if (name != ""):
                                                    if (name != user.screen_name):
                                                        relation = Relation(user.screen_name, name, 50,"ha mencionado a")
                                                        relation.existing_and_upgrade_relation(relations)
                                                else:
                                                    relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                                    relation.existing_and_upgrade_relation(relations)
                            else:
                                if ("RP" in self.type_weigth):
                                    if ("replied_to" in tweet["referenced_tweets"][0]["type"]):
                                        print("REPLIED TO")
                                        print(tweet["text"])
                                        print("----------")
                                        a = self.referenced_author(tweet["referenced_tweets"][0]["id"],json_response["includes"]["tweets"])
                                        name = self.list.existing_profile_name(a)
                                        if (name != ""):
                                            if (name != user.screen_name):
                                                relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                                relation.existing_and_upgrade_relation(relations)
                                        else:
                                            relation = Relation(user.screen_name, a, 50, "ha mencionado a")
                                            relation.existing_and_upgrade_relation(relations)
                                if ("RT" in self.type_weigth):
                                    if ("quoted" in tweet["referenced_tweets"][0]["type"]):
                                        print("RETWEET WITH TEXT")
                                        print(tweet["text"])
                                        print("----------")
                                        a = self.referenced_author(tweet["referenced_tweets"][0]["id"],json_response["includes"]["tweets"])
                                        name = self.list.existing_profile_name(a)
                                        if (name != ""):
                                            if (name != user.screen_name):
                                                relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                                relation.existing_and_upgrade_relation(relations)
                                        else:
                                            relation = Relation(user.screen_name, a, 50, "ha mencionado a")
                                            relation.existing_and_upgrade_relation(relations)
                                        if ("entities" in tweet):
                                            if ("mentions" in tweet["entities"]):
                                                for mention in tweet["entities"]["mentions"]:
                                                    print(mention["username"])
                                                    id = self.id_mentioned(mention["username"],json_response["includes"]["users"])
                                                    name = self.list.existing_profile_name(id)
                                                    if (name != ""):
                                                        if (name != user.screen_name):
                                                            relation = Relation(user.screen_name, name, 50,
                                                                                "ha mencionado a")
                                                            relation.existing_and_upgrade_relation(relations)
                                                    else:
                                                        relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                                        relation.existing_and_upgrade_relation(relations)
                                    if ("retweeted" in tweet["referenced_tweets"][0]["type"]):
                                        print("RETWEET")
                                        print(tweet["text"])
                                        print("----------")
                                        a = self.referenced_author(tweet["referenced_tweets"][0]["id"],json_response["includes"]["tweets"])
                                        name = self.list.existing_profile_name(a)
                                        if (name != ""):
                                            if (name != user.screen_name):
                                                relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                                relation.existing_and_upgrade_relation(relations)
                                        else:
                                            relation = Relation(user.screen_name, a, 50, "ha mencionado a")
                                            relation.existing_and_upgrade_relation(relations)
                        if (not "next_token" in json_response["meta"]):
                            break
            progresso = (member + 1) / len(self.list.profiles)
            communication.sig.emit(progresso * 100)
            member += 1
            print("---------------------------------------------")
        print("---------------------------------------------------------------------------------------------------------------------")
        stra = ""
        if ("M" in self.type_weigth):
            stra += "M,"
        if ("RP" in self.type_weigth):
            stra += "RP,"
        if ("RT" in self.type_weigth):
            stra += "RT"
        name = self.path + "/" + "F WY " + stra + " (" + self.start_date[:10] + ")(" + self.end_date[:10] + ").csv"
        with open(name, "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(["Source", "Target", "Weight", "Label", "Type", "Start date", "End date"])
            for relation in relations:
                writer.writerow([relation.source, relation.target, relation.weight, relation.label, relation.type, self.start_date,self.end_date])

        communication.sig.emit(9999)

    def get_mentions(self, id, includes):
        for mention in includes["users"]:
            if(mention["id"] == id):
                return mention["username"]

    def execute_mentions(self, communication):

        print("execute_mentions")
        response = self.get_list_members()

        for profile in response["users"]:
            user = Profile(profile["screen_name"], profile["id"], profile["followers_count"], profile["friends_count"],profile["location"], profile["description"], profile["created_at"])
            self.list.add_profile(user)

        relations = []
        member = 0
        while member < len(self.list.profiles):
            user = self.list.get_profile(member)
            print(user.screen_name)
            search_url = "https://api.twitter.com/2/tweets/search/recent"
            print("M")
            # Mentions --------------------------------------------------------------------------------- A -> B
            aux = "@" + user.screen_name + " -is:reply -is:retweet"
            query_params = {'query': aux, 'tweet.fields': 'created_at,author_id,in_reply_to_user_id','expansions': 'author_id', 'user.fields': 'username', 'max_results': 100}
            json_response = self.oauth.connect_to_endpoint(search_url, query_params)
            if ("data" in json_response):
                for mencionador in json_response["data"]:
                    print(mencionador["author_id"])
                    if (not self.list.existing_profile(mencionador["author_id"])):
                        relation = Relation(mencionador["author_id"], user.screen_name, 50, "ha mencionado a")
                        if (not relation.existing_relation(relations)):
                            relations.append(relation)
                if ("next_token" in json_response["meta"]):
                    while json_response["meta"]["next_token"] != 0:
                        query_params['next_token'] = json_response["meta"]["next_token"]
                        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                        for mencionador in json_response["data"]:
                            print(mencionador["author_id"])
                            if (not self.list.existing_profile(mencionador["author_id"])):
                                relation = Relation(mencionador["author_id"], user.screen_name, 50, "ha mencionado a")
                                if (not relation.existing_relation(relations)):
                                    relations.append(relation)
                        if (not "next_token" in json_response["meta"]):
                            break
            # User timeline - -------------------------------------------------------------------------------- B -> A
            search_url = "https://api.twitter.com/2/users/{}/tweets".format(user.id)
            start = generate((datetime.now(timezone.utc).astimezone() - timedelta(days=7)).replace(tzinfo=pytz.utc))
            print(start)
            query_params = {"tweet.fields": "created_at,author_id,entities","expansions": "referenced_tweets.id.author_id,entities.mentions.username","max_results": 100, "start_time": start}
            json_response = self.oauth.connect_to_endpoint(search_url, query_params)
            if ("data" in json_response):
                for tweet in json_response["data"]:
                    if (not "referenced_tweets" in tweet):
                        print("ORIGINAL TWEET")
                        if ("entities" in tweet):
                            if ("mentions" in tweet["entities"]):
                                print(tweet["text"])
                                print("----------")
                                for mention in tweet["entities"]["mentions"]:
                                    print(mention["username"])
                                    id = self.id_mentioned(mention["username"], json_response["includes"]["users"])
                                    name = self.list.existing_profile_name(id)
                                    if (name != ""):
                                        if (name != user.screen_name):
                                            relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                            if (not relation.existing_relation(relations)):
                                                relations.append(relation)
                                    else:
                                        relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                        if (not relation.existing_relation(relations)):
                                            relations.append(relation)
                    else:
                        if ("quoted" in tweet["referenced_tweets"][0]["type"]):
                            print("RETWEET WITH TEXT")
                            print(tweet["text"])
                            print("----------")
                            a = self.referenced_author(tweet["referenced_tweets"][0]["id"],json_response["includes"]["tweets"])
                            name = self.list.existing_profile_name(a)
                            if (name != ""):
                                if (name != user.screen_name):
                                    relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                    if (not relation.existing_relation(relations)):
                                        relations.append(relation)
                            else:
                                relation = Relation(user.screen_name, a, 50, "ha mencionado a")
                                if (not relation.existing_relation(relations)):
                                    relations.append(relation)
                            if ("entities" in tweet):
                                if ("mentions" in tweet["entities"]):
                                    for mention in tweet["entities"]["mentions"]:
                                        print(mention["username"])
                                        id = self.id_mentioned(mention["username"], json_response["includes"]["users"])
                                        name = self.list.existing_profile_name(id)
                                        if (name != ""):
                                            if (name != user.screen_name):
                                                relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                                if (not relation.existing_relation(relations)):
                                                    relations.append(relation)
                                        else:
                                            relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                            if (not relation.existing_relation(relations)):
                                                relations.append(relation)
                if ("next_token" in json_response["meta"]):
                    while json_response["meta"]["next_token"] != 0:
                        query_params['pagination_token'] = json_response["meta"]["next_token"]
                        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                        for tweet in json_response["data"]:
                            if (not "referenced_tweets" in tweet):
                                print("ORIGINAL TWEET")
                                if ("entities" in tweet):
                                    if ("mentions" in tweet["entities"]):
                                        print(tweet["text"])
                                        print("----------")
                                        for mention in tweet["entities"]["mentions"]:
                                            print(mention["username"])
                                            id = self.id_mentioned(mention["username"],json_response["includes"]["users"])
                                            name = self.list.existing_profile_name(id)
                                            if (name != ""):
                                                if (name != user.screen_name):
                                                    relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                                    if (not relation.existing_relation(relations)):
                                                        relations.append(relation)
                                            else:
                                                relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                                if (not relation.existing_relation(relations)):
                                                    relations.append(relation)
                            else:
                                if ("quoted" in tweet["referenced_tweets"][0]["type"]):
                                    print("RETWEET WITH TEXT")
                                    print(tweet["text"])
                                    print("----------")
                                    a = self.referenced_author(tweet["referenced_tweets"][0]["id"],json_response["includes"]["tweets"])
                                    name = self.list.existing_profile_name(a)
                                    if (name != ""):
                                        if (name != user.screen_name):
                                            relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                            if (not relation.existing_relation(relations)):
                                                relations.append(relation)
                                    else:
                                        relation = Relation(user.screen_name, a, 50, "ha mencionado a")
                                        if (not relation.existing_relation(relations)):
                                            relations.append(relation)
                                    if ("entities" in tweet):
                                        if ("mentions" in tweet["entities"]):
                                            for mention in tweet["entities"]["mentions"]:
                                                print(mention["username"])
                                                id = self.id_mentioned(mention["username"],json_response["includes"]["users"])
                                                name = self.list.existing_profile_name(id)
                                                if (name != ""):
                                                    if (name != user.screen_name):
                                                        relation = Relation(user.screen_name, name, 50,"ha mencionado a")
                                                        if (not relation.existing_relation(relations)):
                                                            relations.append(relation)
                                                else:
                                                    relation = Relation(user.screen_name, id, 50, "ha mencionado a")
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

    def execute_mentions_weigthed(self, communication):

        response = self.get_list_members()
        print("execute_mentions_weighted")
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
            json_response = self.oauth.connect_to_endpoint(search_url, query_params)
            if ("data" in json_response):
                for mencionador in json_response["data"]:
                    print(mencionador["author_id"])
                    if (not self.list.existing_profile(mencionador["author_id"])):
                        relation = Relation(mencionador["author_id"], user.screen_name, 50, "ha mencionado a")
                        if (relation.existing_and_upgrade_relation(relations)):
                            pass
                        else:
                            relations.append(relation)
                if ("next_token" in json_response["meta"]):
                    while json_response["meta"]["next_token"] != 0:
                        query_params['next_token'] = json_response["meta"]["next_token"]
                        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                        for mencionador in json_response["data"]:
                            print(mencionador["author_id"])
                            if (not self.list.existing_profile(mencionador["author_id"])):
                                relation = Relation(mencionador["author_id"], user.screen_name, 50, "ha mencionado a")
                                if (relation.existing_and_upgrade_relation(relations)):
                                    pass
                                else:
                                    relations.append(relation)
                        if (not "next_token" in json_response["meta"]):
                            break
            # User timeline - -------------------------------------------------------------------------------- B -> A
            search_url = "https://api.twitter.com/2/users/{}/tweets".format(user.id)
            start = generate((datetime.now(timezone.utc).astimezone() - timedelta(days=7)).replace(tzinfo=pytz.utc))
            print(start)
            query_params = {"tweet.fields": "created_at,author_id,entities","expansions": "referenced_tweets.id.author_id,entities.mentions.username","max_results": 100, "start_time": start}
            json_response = self.oauth.connect_to_endpoint(search_url, query_params)
            if ("data" in json_response):
                for tweet in json_response["data"]:
                    if (not "referenced_tweets" in tweet):
                        print("ORIGINAL TWEET")
                        if ("entities" in tweet):
                            if ("mentions" in tweet["entities"]):
                                print(tweet["text"])
                                print("----------")
                                for mention in tweet["entities"]["mentions"]:
                                    print(mention["username"])
                                    id = self.id_mentioned(mention["username"], json_response["includes"]["users"])
                                    name = self.list.existing_profile_name(id)
                                    if (name != ""):
                                        if (name != user.screen_name):
                                            relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                            if (relation.existing_and_upgrade_relation(relations)):
                                                pass
                                            else:
                                                relations.append(relation)
                                    else:
                                        relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                        if (relation.existing_and_upgrade_relation(relations)):
                                            pass
                                        else:
                                            relations.append(relation)
                    else:
                        if ("quoted" in tweet["referenced_tweets"][0]["type"]):
                            print("RETWEET WITH TEXT")
                            print(tweet["text"])
                            print("----------")
                            a = self.referenced_author(tweet["referenced_tweets"][0]["id"],json_response["includes"]["tweets"])
                            name = self.list.existing_profile_name(a)
                            if (name != ""):
                                if (name != user.screen_name):
                                    relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                    if (relation.existing_and_upgrade_relation(relations)):
                                        pass
                                    else:
                                        relations.append(relation)
                            else:
                                relation = Relation(user.screen_name, a, 50, "ha mencionado a")
                                if (relation.existing_and_upgrade_relation(relations)):
                                    pass
                                else:
                                    relations.append(relation)
                            if ("entities" in tweet):
                                if ("mentions" in tweet["entities"]):
                                    for mention in tweet["entities"]["mentions"]:
                                        print(mention["username"])
                                        id = self.id_mentioned(mention["username"],json_response["includes"]["users"])
                                        name = self.list.existing_profile_name(id)
                                        if (name != ""):
                                            if (name != user.screen_name):
                                                relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                                if (relation.existing_and_upgrade_relation(relations)):
                                                    pass
                                                else:
                                                    relations.append(relation)
                                        else:
                                            relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                            if (relation.existing_and_upgrade_relation(relations)):
                                                pass
                                            else:
                                                relations.append(relation)
                if ("next_token" in json_response["meta"]):
                    while json_response["meta"]["next_token"] != 0:
                        query_params['pagination_token'] = json_response["meta"]["next_token"]
                        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                        for tweet in json_response["data"]:
                            if (not "referenced_tweets" in tweet):
                                print("ORIGINAL TWEET")
                                if ("entities" in tweet):
                                    if ("mentions" in tweet["entities"]):
                                        print(tweet["text"])
                                        print("----------")
                                        for mention in tweet["entities"]["mentions"]:
                                            print(mention["username"])
                                            id = self.id_mentioned(mention["username"],
                                                                   json_response["includes"]["users"])
                                            name = self.list.existing_profile_name(id)
                                            if (name != ""):
                                                if (name != user.screen_name):
                                                    relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                                    if (relation.existing_and_upgrade_relation(relations)):
                                                        pass
                                                    else:
                                                        relations.append(relation)
                                            else:
                                                relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                                if (relation.existing_and_upgrade_relation(relations)):
                                                    pass
                                                else:
                                                    relations.append(relation)
                            else:
                                if ("quoted" in tweet["referenced_tweets"][0]["type"]):
                                    print("RETWEET WITH TEXT")
                                    print(tweet["text"])
                                    print("----------")
                                    a = self.referenced_author(tweet["referenced_tweets"][0]["id"],
                                                               json_response["includes"]["tweets"])
                                    name = self.list.existing_profile_name(a)
                                    if (name != ""):
                                        if (name != user.screen_name):
                                            relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                            if (relation.existing_and_upgrade_relation(relations)):
                                                pass
                                            else:
                                                relations.append(relation)
                                    else:
                                        relation = Relation(user.screen_name, a, 50, "ha mencionado a")
                                        if (relation.existing_and_upgrade_relation(relations)):
                                            pass
                                        else:
                                            relations.append(relation)
                                    if ("entities" in tweet):
                                        if ("mentions" in tweet["entities"]):
                                            for mention in tweet["entities"]["mentions"]:
                                                print(mention["username"])
                                                id = self.id_mentioned(mention["username"],
                                                                       json_response["includes"]["users"])
                                                name = self.list.existing_profile_name(id)
                                                if (name != ""):
                                                    if (name != user.screen_name):
                                                        relation = Relation(user.screen_name, name, 50,
                                                                            "ha mencionado a")
                                                        if (relation.existing_and_upgrade_relation(relations)):
                                                            pass
                                                        else:
                                                            relations.append(relation)
                                                else:
                                                    relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                                    if (relation.existing_and_upgrade_relation(relations)):
                                                        pass
                                                    else:
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
        name = self.path + "/" + "M WY (" + self.start_date[:10] + ")(" + self.end_date[:10] + ").csv"
        print(name)
        with open(name, "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(["Source", "Target", "Weight", "Label", "Type"])
            for relation in relations:
                writer.writerow([relation.source, relation.target, relation.weight, relation.label, relation.type])

        communication.sig.emit(9999)