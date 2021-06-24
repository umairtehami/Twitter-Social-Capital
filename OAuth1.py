from Authentication import *
import time as t
from requests_oauthlib import OAuth1Session

class OAuth1(Authentication):

    def __init__(self, name, path, consumer_key, consumer_secret, access_token, access_secret_token, communicate):
        super(OAuth1, self).__init__(name, path)
        self.id = 1
        self.name = name
        self.path = path
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_secret_token = access_secret_token
        self.communicate = communicate
        self.get_tokens()

    def get_tokens(self):
        self.oauth = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_secret_token,
        )

    def check_credentials(self):
        s = "https://api.twitter.com/1.1/users/lookup.json"
        params = {"screen_name": "TwitterAPI"}
        response = self.oauth.get(s, params=params)
        if(response.status_code == 401):
            print("Wrong credentials, please check and try again")
            return False
        elif(response.status_code == 200):
            print("Correct credentials")
            return True

    def connect_to_endpoint(self, s, params):
        try:
            response = self.oauth.get(s, params=params)
            if response.status_code != 200:
                if(response.status_code == 429):
                    print("Rate limit exceeded, waiting")
                    t.sleep(60)
                    return self.connect_to_endpoint(s,params)
                elif(response.status_code == 503):
                    print("The Twitter servers are up, but overloaded with requests. Waiting 5 min and retrying.")
                else:
                    print("An unexpected error has occurred. Please close the software and try again")
            else:
                return response.json()
        except:
            t.sleep(60)
            return self.connect_to_endpoint(s,params)
