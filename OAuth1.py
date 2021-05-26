from Authentication import *
import time as t
from requests_oauthlib import OAuth1Session

class OAuth1(Authentication):

    def __init__(self, name, path, consumer_key, consumer_secret, access_token, access_secret_token):
        super(OAuth1, self).__init__(name, path)
        self.id = 1
        self.name = name
        self.path = path
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_secret_token = access_secret_token
        self.get_tokens()

    def get_tokens(self):
        self.oauth = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_secret_token,
        )

    def connect_to_endpoint(self, s, params):
        response = {}
        try:
            response = self.oauth.get(s, params=params)
        except:
            return response
        if response.status_code != 200:
            print(response.status_code)
            while response.status_code != 200:
                print("Esperando 1 min")
                print(response.text)
                t.sleep(60)
                try:
                    response = self.oauth.get(s, params=params)
                except:
                    return response
        return response.json()