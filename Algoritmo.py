
import tweepy
from Profile import *
import time
import csv
import json
from Relation import *
import requests

class Algoritmo:

    def __init__(self,aceess="",OAuth="",CK="",CS="",AT="",AST="",BRT=""):
        self.type_access = aceess
        self.type_OAuth = OAuth
        self.consumer_key = CK
        self.consumer_secret = CS
        self.access_token = AT
        self.access_secret_token = AST
        self.bearer_token = BRT

    def set_type_access(self,new_access):
        self.type_access = new_access

    def set_type_authentication(self,authentication):
        self.type_OAuth = authentication

    def set_consumer_key(self,consumer_key):
        self.consumer_key = consumer_key

    def set_consumer_secret(self,consumer_secret):
        self.consumer_secret = consumer_secret

    def set_access_token(self,access_token):
        self.access_token = access_token

    def set_access_secret_token(self,access_secret_token):
        self.access_secret_token = access_secret_token

    def set_bearer_token(self,bearer_token):
        self.bearer_token = bearer_token

    def get_type_access(self,new_access):
        return self.type_access

    def get_type_authentication(self,authentication):
        return self.type_OAuth

    def get_consumer_key(self,consumer_key):
        return self.consumer_key

    def get_consumer_secret(self,consumer_secret):
        return self.consumer_secret

    def get_access_token(self,access_token):
        return self.access_token

    def get_access_secret_token(self,access_secret_token):
        return self.access_secret_token

    def get_bearer_token(self,bearer_token):
        return self.bearer_token

    def extract_followers_simple(self, communication):

        consumer_key = self.consumer_key
        consumer_secret = self.consumer_secret
        access_token = self.access_token
        access_token_secret = self.access_secret_token

        auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        data = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        members = []
        members_id = []

        id_list = "1371396789639774211"

        for page in tweepy.Cursor(data.list_members, list_id=id_list).items():
            user = Profile(page.screen_name, page.id, page.followers_count, page.friends_count, page.location, page.description, page.created_at)
            members.append(user)
            members_id.append(user.id)


        with open("INTR-FLW-INNOVI2.csv", "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(["Source", "Target", "Weight", "Label", "Type"])
            member = 0
            while member < len(members):
                user = members[member]
                print(user.screen_name)
                for page in tweepy.Cursor(data.followers_ids, user_id=user.id, monitor_rate_limit=True, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=5,retry_delay=5, count=5000).pages():
                    try:
                        for user_id in page:
                            if user_id in members_id:
                                writer.writerow([user_id, members_id[member], "200", "Es seguidor de", "Directed"])
                            else:
                                writer.writerow([str(user_id), user.screen_name, "50", "Es seguidor de", "Directed"])
                            print(str(user_id) + " es seguidor de " + user.screen_name)
                    except tweepy.TweepError as e:
                        print("Going to sleep:", e)
                        time.sleep(60)
                progresso = (member + 1)/len(members)
                communication.sig.emit(progresso*100)
                member += 1
        return "EXTRACTION FINISHED"

    def extract_mentions_simple(self, Lista, communication):

        consumer_key = self.consumer_key
        consumer_secret = self.consumer_secret
        access_token = self.access_token
        access_token_secret = self.access_secret_token

        auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        data = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        members = []
        members_id = []

        id_list = Lista.get_list()

        for page in tweepy.Cursor(data.list_members, list_id=id_list).items():
            user = Profile(page.screen_name, page.id, page.followers_count, page.friends_count, page.location, page.description, page.created_at)
            members.append(user)
            members_id.append(user.id)


        with open("INTR-FLW-INNOVI2.csv", "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(["Source", "Target", "Weight", "Label", "Type"])
            member = 0
            while member < len(members):
                user = members[member]
                print(user.screen_name)
                aux = "@" + str(user.screen_name)
                query = aux + " -filter:retweets"
                for page in tweepy.Cursor(data.search, q=query, tweet_mode="extended", monitor_rate_limit=True,wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=5,retry_delay=5, count=5000).pages():
                    try:
                        for tweet in page:
                            if (str(tweet.in_reply_to_status_id) == "None"):
                                if tweet.user.screen_name in members:
                                    writer.writerow([tweet.user.screen_name, user.screen_name, "200", "Ha mencionado", "Directed"])
                                else:
                                    writer.writerow([tweet.user.screen_name, user.screen_name, "50", "Ha mencionado", "Directed"])
                    except tweepy.TweepError as e:
                        print("Going to sleep:", e)
                        time.sleep(60)
                progresso = (member + 1)/len(members)
                communication.sig.emit(progresso*100)
                member += 1
        return "EXTRACTION FINISHED"

    def create_headers(self,bearer_token):
        headers = {"Authorization": "Bearer {}".format(bearer_token)}
        return headers

    def connect_to_endpoint(self,url, headers, params):
        response = requests.request("GET", url, headers=headers, params=params)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()

    def extract_retweets_simple(self, Lista, communication):

        consumer_key = self.consumer_key
        consumer_secret = self.consumer_secret
        access_token = self.access_token
        access_token_secret = self.access_secret_token

        auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        data = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        members = []
        members_id = []

        id_list = Lista.get_list()

        for page in tweepy.Cursor(data.list_members, list_id=id_list).items():
            user = Profile(page.screen_name, page.id, page.followers_count, page.friends_count, page.location, page.description, page.created_at)
            members.append(user)
            members_id.append(user.id)


        with open("INTR-FLW-INNOVI2.csv", "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(["Source", "Target", "Weight", "Label", "Type"])
            member = 0
            while member < len(members):
                user = members[member]
                print(user.screen_name)
                aux = "@" + str(user.screen_name)
                query = aux
                for page in tweepy.Cursor(data.search, q=query, tweet_mode="extended", monitor_rate_limit=True,wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=5,retry_delay=5, count=5000).pages():
                    try:
                        for tweet in page:
                            if (tweet.full_text[0] == "R" and tweet.full_text[1] == "T" and tweet.full_text[2] == " "):
                                try:
                                    if (tweet.retweeted_status.user.screen_name == user.screen_name):
                                        if tweet.user.screen_name in members:
                                            writer.writerow([tweet.user.screen_name, user.screen_name, "200", "Ha retweeteado a","Directed"])
                                        else:
                                            writer.writerow([tweet.user.screen_name, user.screen_name, "50", "Ha retweeteado a","Directed"])
                                except:
                                    pass
                    except tweepy.TweepError as e:
                        print("Going to sleep:", e)
                        time.sleep(60)
                progresso = (member + 1)/len(members)
                communication.sig.emit(progresso*100)
                member += 1
        return "EXTRACTION FINISHED"

    def extract_mentions_weighted(self, Lista, communication):

        consumer_key = self.consumer_key
        consumer_secret = self.consumer_secret
        access_token = self.access_token
        access_token_secret = self.access_secret_token

        auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        data = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        members = []
        members_id = []

        id_list = Lista.get_list()

        for page in tweepy.Cursor(data.list_members, list_id=id_list).items():
            user = Profile(page.screen_name, page.id, page.followers_count, page.friends_count, page.location, page.description, page.created_at)
            members.append(user)
            members_id.append(user.id)

        relations = []
        member = 0
        while member < 1:
            user = members[member]
            print(user.screen_name)
            for page in tweepy.Cursor(data.followers_ids, user_id=user.id, monitor_rate_limit=True, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=5,retry_delay=5, count=5000).pages():
                try:
                    for user_id in page:
                        relation = Relation(user_id, user.screen_name, "50", "Sigue a","Directed")
                        relations.append(relation)
                except tweepy.TweepError as e:
                    print("Going to sleep:", e)
                    time.sleep(60)
            progresso = (member + 1)/len(members)
            communication.sig.emit(progresso*100)
            member += 1
        print("-----------------------------------------------------")
        member = 0
        while member < 1:
            user = members[member]
            print(user.screen_name)
            bearer_token = "AAAAAAAAAAAAAAAAAAAAAGGjNQEAAAAA%2FC6EztbH3ubeSHLtIuTe1lN%2Bypo%3Da8pm33BznTKNwPLJSLG5MDypgMTbW1TgNtz327bGCP7fiq98Bq"
            search_url = "https://api.twitter.com/2/tweets/search/all"
            query_params = {'query': '(to:CellersBlanch)', 'tweet.fields': 'created_at,author_id', 'max_results': 50}

            headers = self.create_headers(bearer_token)
            json_response = self.connect_to_endpoint(search_url, headers, query_params)
            print(json.dumps(json_response, indent=4, sort_keys=True))

            for rel in relations:
                rel.print_relation()
        return "EXTRACTION FINISHED"