from Authentication import *
import requests
import time as t

class OAuth2(Authentication):

    def __init__(self, name, path, bearer_token):
        super(OAuth2, self).__init__(name, path)
        self.id = 2
        self.name = name
        self.path = path
        self.bearer_token = bearer_token
        self.headers = {"Authorization": "Bearer {}".format(self.bearer_token)}

    def check_credentials(self):
        s = "https://api.twitter.com/1.1/users/lookup.json"
        params = {"screen_name": "TwitterAPI"}
        response = requests.request("GET", s, headers=self.headers, params=params)
        if(response.status_code == 401):
            print("Wrong credentials, please check and try again")
            return False
        elif(response.status_code == 200):
            print("Correct credentials")
            return True

    def connect_to_endpoint(self,url, params):
        try:
            response = requests.request("GET", url, headers=self.headers, params=params)
            if response.status_code != 200:
                if (response.status_code == 429):
                    print("Rate limit exceeded, waiting")
                    t.sleep(60)
                    return self.connect_to_endpoint(url, params)
                elif (response.status_code == 503):
                    print("The Twitter servers are up, but overloaded with requests. Waiting 5 min and retrying.")
                else:
                    print("An unexpected error has occurred. Please close the software and try again")
            else:
                return response.json()
        except:
            t.sleep(60)
            return self.connect_to_endpoint(url, params)