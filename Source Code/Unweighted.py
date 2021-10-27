import json

from Profile import *
from Relation import *
from pyrfc3339 import generate, parse
import pytz
from datetime import *
import csv
import os
from Extraction import *

class Unweighted(Extraction):

    def __init__(self, type, end_date, start_date, list, oauth, path,  delay=0):
        super().__init__(list, delay)
        self.type = type
        self.path = path
        self.oauth = oauth
        self.start_date = start_date
        self.end_date = end_date

    # Return all the profiles in the specified list
    def get_list_members(self):
        search_url = "https://api.twitter.com/1.1/lists/members.json"
        query_params = {'list_id': self.list.get_list(), 'count':5000}
        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
        return json_response

    # Return all the followers of the current member
    def get_followers(self, user):
        search_url = "https://api.twitter.com/1.1/followers/ids.json"
        relations = []
        query_params = {'screen_name': user.screen_name, 'count': 5000}
        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
        if(json_response != "error"):
            if("ids" in json_response):
                for id in json_response["ids"]:
                    name = self.list.existing_profile_name(id)
                    if(name != ""):
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
        else:
            return "error"

    # Returns the references author
    def referenced_author(self,id, includes):
        for include in includes:
            if(include["id"] == id):
                return include["author_id"]

    # Returns the user id if username exists in includes array
    def id_mentioned(self, username, includes):
        for user in includes:
            #print(user)
            if(user["username"] == username):
                return user["id"]

    # Return all the friends of the current member
    def get_friends(self, user):
        search_url = "https://api.twitter.com/1.1/friends/ids.json"
        relations = []
        query_params = {'screen_name': user.screen_name, 'count': 5000}
        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
        if (json_response != "error"):
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
        else:
            return "error"

    # Remove points in string
    def remove_points(self, s):
        aux = ""
        for letter in s:
            if(letter == ":"):
                aux += "_"
            else:
                aux += letter
        return aux

    # Execute followers extraction
    def execute_followers(self, communication):

        print("EXECUTE FOLLOWERS")
        print("--------------------------------------------------------------------------------------")
        print("Retrieving list members...")
        # Get all the profiles in the list ID specified
        response = self.get_list_members()
        print("List members are the following:")
        for profile in response["users"]:
            user = Profile(profile["screen_name"], profile["id"], profile["followers_count"], profile["friends_count"],profile["location"], profile["description"], profile["created_at"])
            self.list.add_profile(user)
            print(user.screen_name)
        print("--------------------------------------------------------------------------------------")
        relations = []
        member = 0
        while member < len(self.list.profiles):
            # Iterate all the members in the list and retrieve their followers and followees
            user = self.list.get_profile(member)
            print("Retrieving information of: ",user.screen_name)
            print("Managing followers...")
            followers = self.get_followers(user)
            print("Followers: ", len(followers))
            print("Managing friends...")
            friends = self.get_friends(user)
            print("Following: ", len(friends))
            relations += (followers + friends)
            progresso = (member + 1) / len(self.list.profiles)
            # Communicate progress to Feedback window
            communication.sig.emit(progresso * 100)
            # Move to next member
            member += 1
            print("---------------------------------------------")

        now = datetime.now()
        dt_string = now.strftime("%H:%M:%S")
        aux = self.remove_points(dt_string)
        name = self.path + "/" + "F WN (" + self.start_date[:10] + "-" + aux + ")(" + self.end_date[:10] + "-" + aux + ").csv"
        # Create a .csv file with "name" name in the current project path.
        print("Saving the extraction into: ", name)
        with open(name, "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(["Source", "Target", "Weight", "Label", "Type"])
            for relation in relations:
                # Write row for each relation created
                writer.writerow([relation.source, relation.target, relation.weight, relation.label, relation.type])

        # Communicate to Feedback the extraction finish
        communication.sig.emit(9999)

    # Execute mentions extraction
    def execute_mentions(self, communication):

        print("EXECUTE MENTIONS")
        print("--------------------------------------------------------------------------------------")
        print("Retrieving list members...")
        response = self.get_list_members()
        print("List members are the following:")
        # Get all the profiles in the list ID specified
        for profile in response["users"]:
            user = Profile(profile["screen_name"], profile["id"], profile["followers_count"], profile["friends_count"],profile["location"], profile["description"], profile["created_at"])
            self.list.add_profile(user)
            print(user.screen_name)
        print("Time interval: ", self.start_date, " to ", self.end_date)
        print("--------------------------------------------------------------------------------------")
        relations = []
        member = 0
        #len(self.list.profiles)
        while member < len(self.list.profiles):
            # Iterate all the members in the list and retrieve their mentions
            user = self.list.get_profile(member)
            print("Retrieving information of: ", user.screen_name)
            #search_url = "https://api.twitter.com/2/tweets/search/recent"
            # Mentions --------------------------------------------------------------------------------- A -> B
            # Tweets were the user is mentioned
            print("Finding Tweets were user is mentioned...")
            aux = "@" + user.screen_name + " -is:reply -is:retweet"
            query_params = {'query': aux, 'tweet.fields': 'created_at,author_id,in_reply_to_user_id','expansions': 'author_id', 'user.fields': 'username', 'max_results': 100}
            if (hasattr(self.oauth, 'get_tokens') and callable(self.oauth.get_tokens)):
                search_url = "https://api.twitter.com/2/tweets/search/recent"
                query_params["max_results"] = 100
            else:
                search_url = "https://api.twitter.com/2/tweets/search/all"
                query_params["max_results"] = 500
                query_params["start_time"] = self.start_date
                query_params["end_time"] = self.end_date
            json_response = self.oauth.connect_to_endpoint(search_url, query_params)
            #print(json.dumps(json_response, indent=4))
            if ("data" in json_response):
                for mencionador in json_response["data"]:
                    if (not self.list.existing_profile(mencionador["author_id"])):
                        relation = Relation(mencionador["author_id"], user.screen_name, 50, "ha mencionado a")
                        if (not relation.existing_relation(relations)):
                            relations.append(relation)
                if ("next_token" in json_response["meta"]):
                    # Obtain the token to acces the next data page if exists
                    while json_response["meta"]["next_token"] != 0:
                        query_params['next_token'] = json_response["meta"]["next_token"]
                        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                        for mencionador in json_response["data"]:
                            if (not self.list.existing_profile(mencionador["author_id"])):
                                relation = Relation(mencionador["author_id"], user.screen_name, 50, "ha mencionado a")
                                if (not relation.existing_relation(relations)):
                                    relations.append(relation)
                        if (not "next_token" in json_response["meta"]):
                            break
            # User timeline - -------------------------------------------------------------------------------- B -> A
            # Tweet were the user mention other users
            print("Retriving user tweets...")
            search_url = "https://api.twitter.com/2/users/{}/tweets".format(user.id)
            # start = generate((datetime.now(timezone.utc).astimezone() - timedelta(days=self.days)).replace(tzinfo=pytz.utc))
            query_params = {"tweet.fields": "created_at,author_id,entities",
                            "expansions": "referenced_tweets.id.author_id,entities.mentions.username",
                            "max_results": 100, "start_time": self.start_date, "end_time": self.end_date}
            json_response = self.oauth.connect_to_endpoint(search_url, query_params)
            # print(json.dumps(json_response, indent=4))
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
                                            if (relation.existing_relation(relations)):
                                                pass
                                            else:
                                                relations.append(relation)
                                    else:
                                        relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                        if (relation.existing_relation(relations)):
                                            pass
                                        else:
                                            relations.append(relation)
                    else:
                        if ("quoted" in tweet["referenced_tweets"][0]["type"]):
                            a = self.referenced_author(tweet["referenced_tweets"][0]["id"],
                                                       json_response["includes"]["tweets"])
                            name = self.list.existing_profile_name(a)
                            if (name != ""):
                                if (name != user.screen_name):
                                    relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                    if (relation.existing_relation(relations)):
                                        pass
                                    else:
                                        relations.append(relation)
                            else:
                                relation = Relation(user.screen_name, a, 50, "ha mencionado a")
                                if (relation.existing_relation(relations)):
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
                                                if (relation.existing_relation(relations)):
                                                    pass
                                                else:
                                                    relations.append(relation)
                                        else:
                                            relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                            if (relation.existing_relation(relations)):
                                                pass
                                            else:
                                                relations.append(relation)
                if ("next_token" in json_response["meta"]):
                    while json_response["meta"]["next_token"] != 0:
                        query_params['pagination_token'] = json_response["meta"]["next_token"]
                        json_response = self.oauth.connect_to_endpoint(search_url, query_params)
                        # print(json.dumps(json_response, indent=4))
                        if ("data" in json_response):
                            for tweet in json_response["data"]:
                                if (not "referenced_tweets" in tweet):
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
                                                        if (relation.existing_relation(relations)):
                                                            pass
                                                        else:
                                                            relations.append(relation)
                                                else:
                                                    relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                                    if (relation.existing_relation(relations)):
                                                        pass
                                                    else:
                                                        relations.append(relation)
                                else:
                                    if ("quoted" in tweet["referenced_tweets"][0]["type"]):
                                        a = self.referenced_author(tweet["referenced_tweets"][0]["id"],
                                                                   json_response["includes"]["tweets"])
                                        name = self.list.existing_profile_name(a)
                                        if (name != ""):
                                            if (name != user.screen_name):
                                                relation = Relation(user.screen_name, name, 50, "ha mencionado a")
                                                if (relation.existing_relation(relations)):
                                                    pass
                                                else:
                                                    relations.append(relation)
                                        else:
                                            relation = Relation(user.screen_name, a, 50, "ha mencionado a")
                                            if (relation.existing_relation(relations)):
                                                pass
                                            else:
                                                relations.append(relation)
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
                                                            if (relation.existing_relation(relations)):
                                                                pass
                                                            else:
                                                                relations.append(relation)
                                                    else:
                                                        relation = Relation(user.screen_name, id, 50, "ha mencionado a")
                                                        if (relation.existing_relation(relations)):
                                                            pass
                                                        else:
                                                            relations.append(relation)
                        if (not "next_token" in json_response["meta"]):
                            break
            progresso = (member + 1) / len(self.list.profiles)
            # Communicate to Feedback the extraction finish
            communication.sig.emit(progresso * 100)
            # Move to next member
            member += 1
            print("---------------------------------------------")
        now = datetime.now()
        dt_string = now.strftime("%H:%M:%S")
        aux = self.remove_points(dt_string)
        name = self.path + "/" + "M WN (" + self.start_date[:10] + "-" + aux + ")(" + self.end_date[:10] + "-" + aux + ").csv"
        print("Saving the extraction into: ", name)
        # Create a .csv file with "name" name in the current project path.
        with open(name, "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(["Source", "Target", "Weight", "Label", "Type"])
            for relation in relations:
                # Write row for each relation created
                if(relation.target == None):
                    writer.writerow([relation.source, "@private_account", relation.weight, relation.label, relation.type])
                    relation.print_relation()
                else:
                    writer.writerow([relation.source, relation.target, relation.weight, relation.label, relation.type])

        # Communicate to Feedback the extraction finish
        communication.sig.emit(9999)
