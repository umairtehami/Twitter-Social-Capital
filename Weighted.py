from Profile import *
from Relation import *
from pyrfc3339 import generate
from datetime import *
import pytz
import time as t
import csv
from Extraction import *

class Weighted(Extraction):
    
    def __init__(self, type, days, list, oauth, path, type_wheigt, delay = 0):
        super().__init__(list, delay)
        self.type = type
        self.path = path
        self.start_date = (datetime.now(timezone.utc).astimezone() - timedelta(days=days)).isoformat()
        self.end_date = datetime.now(timezone.utc).astimezone().isoformat()
        self.oauth = oauth
        self.days = days
        self.type_weigth = type_wheigt

    def get_list_members(self):
        search_url = "https://api.twitter.com/1.1/lists/members.json"
        query_params = {'list_id': self.list.get_list(), 'count':5000}
        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
        return json_response

    def split_list(self, alist, wanted_parts=1):
        length = len(alist)
        return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts]
                for i in range(wanted_parts)]

    def referenced_author(self,id, includes):
        for include in includes:
            if(include["id"] == id):
                return include["author_id"]

    def id_mentioned(self, username, includes):
        for user in includes:
            if(user["username"] == username):
                return user["id"]

    def get_followers(self,user):
        search_url = "https://api.twitter.com/1.1/followers/ids.json"
        relations = []

        query_params = {'screen_name': user.screen_name, 'count': 5000}
        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
        if("ids" in json_response):
            for id in json_response["ids"]:
                name = self.list.existing_profile_name(id)
                if (name != ""):
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
                        relation = Relation(name, user.screen_name, 50, "es seguidor de")
                        relations.append(relation)
                    else:
                        relation = Relation(id, user.screen_name, 50, "es seguidor de")
                        relations.append(relation)
        return relations

    def get_friends(self,user):
        search_url = "https://api.twitter.com/1.1/friends/ids.json"
        relations = []

        query_params = {'screen_name': user.screen_name, 'count': 5000}
        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
        if ("ids" in json_response):
            for id in json_response["ids"]:
                name = self.list.existing_profile_name(id)
                if (name != ""):
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
                        relation = Relation(user.screen_name, name, 50, "es seguidor de")
                        relations.append(relation)
                    else:
                        relation = Relation(user.screen_name, id, 50, "es seguidor de")
                        relations.append(relation)
        return relations

    def execute_followers_weighted(self, communication):

        print("EXECUTE FOLLOWERS WEIGHTED")
        print("--------------------------------------------------------------------------------------")
        response = self.get_list_members()
        for profile in response["users"]:
            user = Profile(profile["screen_name"], profile["id"], profile["followers_count"], profile["friends_count"], profile["location"],profile["description"], profile["created_at"])
            self.list.add_profile(user)

        relations = []
        member = 0
        while member < len(self.list.profiles):
            user = self.list.get_profile(member)
            print(user.screen_name)
            followers = self.get_followers(user)
            friends = self.get_friends(user)
            relations += (followers + friends)
            print("seguidos: ",len(friends), "seguidores: ", len(followers))
            if ("M" in self.type_weigth):
                # Mentions --------------------------------------------------------------------------------- A -> B
                aux = "@" + user.screen_name + " -is:reply -is:retweet"
                query_params = {'query': aux, 'tweet.fields': 'created_at,author_id,in_reply_to_user_id'}
                if (hasattr(self.oauth, 'get_tokens') and callable(self.oauth.get_tokens)):
                    search_url = "https://api.twitter.com/2/tweets/search/recent"
                    query_params["max_results"] = 100
                else:
                    search_url = "https://api.twitter.com/2/tweets/search/all"
                    query_params["max_results"] = 500
                    query_params["start_time"] = self.start_date
                json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                if ("data" in json_response):
                    for mencionador in json_response["data"]:
                        if (not self.list.existing_profile(mencionador["author_id"])):
                            relation = Relation(mencionador["author_id"], user.screen_name, 50, "ha mencionado a")
                            relation.existing_and_upgrade_relation(relations)
                    if ("next_token" in json_response["meta"]):
                        while json_response["meta"]["next_token"] != 0:
                            query_params['next_token'] = json_response["meta"]["next_token"]
                            json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                            for mencionador in json_response["data"]:
                                if (not self.list.existing_profile(mencionador["author_id"])):
                                    relation = Relation(mencionador["author_id"], user.screen_name, 50,
                                                        "ha mencionado a")
                                    relation.existing_and_upgrade_relation(relations)
                            if (not "next_token" in json_response["meta"]):
                                break
            if ("RP" in self.type_weigth):
                # Replies --------------------------------------------------------------------------------- A -> B
                aux = "to:" + user.screen_name + " is:reply -is:retweet"
                query_params = {'query': aux,
                                'tweet.fields': 'created_at,author_id,in_reply_to_user_id,referenced_tweets'}
                if (hasattr(self.oauth, 'get_tokens') and callable(self.oauth.get_tokens)):
                    search_url = "https://api.twitter.com/2/tweets/search/recent"
                    query_params["max_results"] = 100
                else:
                    search_url = "https://api.twitter.com/2/tweets/search/all"
                    query_params["max_results"] = 500
                    query_params["start_time"] = self.start_date
                json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                if ("data" in json_response):
                    for respuesta in json_response["data"]:
                        if ("referenced_tweets" in respuesta):
                            if (respuesta["referenced_tweets"][0]["type"] == "replied_to"):
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
                                        if (not self.list.existing_profile(respuesta["author_id"])):
                                            relation = Relation(respuesta["author_id"], user.screen_name, 50,
                                                                "ha mencionado a")
                                            relation.existing_and_upgrade_relation(relations)
                            if (not "next_token" in json_response["meta"]):
                                break
            if ("RT" in self.type_weigth):
                # Retweets --------------------------------------------------------------------------------- A -> B
                aux = "retweets_of:" + user.screen_name
                query_params = {'query': aux,
                                'tweet.fields': 'created_at,author_id,in_reply_to_user_id,referenced_tweets'}
                if (hasattr(self.oauth, 'get_tokens') and callable(self.oauth.get_tokens)):
                    search_url = "https://api.twitter.com/2/tweets/search/recent"
                    query_params["max_results"] = 100
                else:
                    search_url = "https://api.twitter.com/2/tweets/search/all"
                    query_params["max_results"] = 500
                    query_params["start_time"] = self.start_date
                json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                if ("data" in json_response):
                    for respuesta in json_response["data"]:
                        if (not self.list.existing_profile(respuesta["author_id"])):
                            relation = Relation(respuesta["author_id"], user.screen_name, 50, "ha mencionado a")
                            relation.existing_and_upgrade_relation(relations)
                    if ("next_token" in json_response["meta"]):
                        while json_response["meta"]["next_token"] != 0:
                            query_params['next_token'] = json_response["meta"]["next_token"]
                            json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                            for respuesta in json_response["data"]:
                                if (not self.list.existing_profile(respuesta["author_id"])):
                                    relation = Relation(respuesta["author_id"], user.screen_name, 50, "ha mencionado a")
                                    relation.existing_and_upgrade_relation(relations)
                            if (not "next_token" in json_response["meta"]):
                                break
            # User timeline - -------------------------------------------------------------------------------- B -> A
            search_url = "https://api.twitter.com/2/users/{}/tweets".format(user.id)
            start = generate((datetime.now(timezone.utc).astimezone() - timedelta(days=self.days)).replace(tzinfo=pytz.utc))
            query_params = {"tweet.fields": "created_at,author_id,entities",
                            "expansions": "referenced_tweets.id.author_id,entities.mentions.username",
                            "max_results": 100, "start_time": start}
            json_response = self.oauth.connect_to_endpoint(search_url, query_params)
            if ("data" in json_response):
                for tweet in json_response["data"]:
                    if (not "referenced_tweets" in tweet):
                        if ("M" in self.type_weigth):
                            if ("entities" in tweet):
                                if ("mentions" in tweet["entities"]):
                                    for mention in tweet["entities"]["mentions"]:
                                        id = self.id_mentioned(mention["username"], json_response["includes"]["users"])
                                        name = self.list.existing_profile_name(id)
                                        if (name != ""):
                                            if (name != user.screen_name):
                                                relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                                relation.existing_and_upgrade_relation(relations)
                                        else:
                                            relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                            relation.existing_and_upgrade_relation(relations)
                    else:
                        if ("RP" in self.type_weigth):
                            if ("replied_to" in tweet["referenced_tweets"][0]["type"]):
                                a = self.referenced_author(tweet["referenced_tweets"][0]["id"],
                                                           json_response["includes"]["tweets"])
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
                                a = self.referenced_author(tweet["referenced_tweets"][0]["id"],
                                                           json_response["includes"]["tweets"])
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
                                            id = self.id_mentioned(mention["username"],
                                                                   json_response["includes"]["users"])
                                            name = self.list.existing_profile_name(id)
                                            if (name != ""):
                                                if (name != user.screen_name):
                                                    relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                                    relation.existing_and_upgrade_relation(relations)
                                            else:
                                                relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                                relation.existing_and_upgrade_relation(relations)
                            if ("retweeted" in tweet["referenced_tweets"][0]["type"]):
                                a = self.referenced_author(tweet["referenced_tweets"][0]["id"],
                                                           json_response["includes"]["tweets"])
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
                                    if ("entities" in tweet):
                                        if ("mentions" in tweet["entities"]):
                                            for mention in tweet["entities"]["mentions"]:
                                                id = self.id_mentioned(mention["username"],
                                                                       json_response["includes"]["users"])
                                                name = self.list.existing_profile_name(id)
                                                if (name != ""):
                                                    if (name != user.screen_name):
                                                        relation = Relation(user.screen_name, name, 50,
                                                                            "ha mencionado a")
                                                        relation.existing_and_upgrade_relation(relations)
                                                else:
                                                    relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                                    relation.existing_and_upgrade_relation(relations)
                            else:
                                if ("RP" in self.type_weigth):
                                    if ("replied_to" in tweet["referenced_tweets"][0]["type"]):
                                        a = self.referenced_author(tweet["referenced_tweets"][0]["id"],
                                                                   json_response["includes"]["tweets"])
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
                                        a = self.referenced_author(tweet["referenced_tweets"][0]["id"],
                                                                   json_response["includes"]["tweets"])
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
                                                    id = self.id_mentioned(mention["username"],
                                                                           json_response["includes"]["users"])
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
                                        a = self.referenced_author(tweet["referenced_tweets"][0]["id"],
                                                                   json_response["includes"]["tweets"])
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
        stra = ""
        if("M" in self.type_weigth):
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
                writer.writerow([relation.source, relation.target, relation.weight, relation.label, relation.type, self.start_date, self.end_date])

        communication.sig.emit(9999)

    def execute_mentions_weighted(self, communication):

        print("EXECUTE MENTIONS WEIGHTED")
        print("--------------------------------------------------------------------------------------")
        response = self.get_list_members()
        for profile in response["users"]:
            user = Profile(profile["screen_name"], profile["id"], profile["followers_count"], profile["friends_count"], profile["location"],profile["description"], profile["created_at"])
            self.list.add_profile(user)

        relations = []
        member = 0
        while member < len(self.list.profiles):
            user = self.list.get_profile(member)
            print(user.screen_name)
            #Mentions --------------------------------------------------------------------------------- A -> B
            aux = "@" + user.screen_name + " -is:reply -is:retweet"
            query_params = {'query': aux, 'tweet.fields': 'created_at,author_id,in_reply_to_user_id', 'expansions': 'author_id'}
            if (hasattr(self.oauth, 'get_tokens') and callable(self.oauth.get_tokens)):
                search_url = "https://api.twitter.com/2/tweets/search/recent"
                query_params["max_results"] = 100
            else:
                search_url = "https://api.twitter.com/2/tweets/search/all"
                query_params["max_results"] = 500
                query_params["start_time"] = self.start_date
            json_response = self.oauth.connect_to_endpoint(search_url, query_params)
            if ("data" in json_response):
                for mencionador in json_response["data"]:
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
            start = generate((datetime.now(timezone.utc).astimezone() - timedelta(days=self.days)).replace(tzinfo=pytz.utc))
            query_params = {"tweet.fields": "created_at,author_id,entities","expansions":"referenced_tweets.id.author_id,entities.mentions.username","max_results": 100, "start_time": start}
            json_response = self.oauth.connect_to_endpoint(search_url, query_params)
            if ("data" in json_response):
                for tweet in json_response["data"]:
                    if (not "referenced_tweets" in tweet):
                        if ("entities" in tweet):
                            if ("mentions" in tweet["entities"]):
                                for mention in tweet["entities"]["mentions"]:
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
                if ("next_token" in json_response["meta"]):
                    while json_response["meta"]["next_token"] != 0:
                        query_params['pagination_token'] = json_response["meta"]["next_token"]
                        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                        for tweet in json_response["data"]:
                            if (not "referenced_tweets" in tweet):
                                if ("entities" in tweet):
                                    if ("mentions" in tweet["entities"]):
                                        for mention in tweet["entities"]["mentions"]:
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
                            else:
                                if ("quoted" in tweet["referenced_tweets"][0]["type"]):
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
                                                id = self.id_mentioned(mention["username"],json_response["includes"]["users"])
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
        name = self.path + "/" + "M WY (" + self.start_date[:10] + ")(" + self.end_date[:10] + ").csv"
        with open(name, "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(["Source", "Target", "Weight", "Label", "Type", "Start date", "End date"])
            for relation in relations:
                writer.writerow([relation.source, relation.target, relation.weight, relation.label, relation.type, self.start_date, self.end_date])

        communication.sig.emit(9999)
