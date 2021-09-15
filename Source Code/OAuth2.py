from Authentication import *
import requests
import time as t

# OAuth2 class save all the attributes related to this type of authentication.
class OAuth2(Authentication):

    def __init__(self, name, path, bearer_token):
        super(OAuth2, self).__init__(name, path)
        self.id = 2
        self.name = name
        self.path = path
        self.bearer_token = bearer_token
        self.headers = {"Authorization": "Bearer {}".format(self.bearer_token)}

    # Check if the credentials are valid
    def check_credentials(self):
        s = "https://api.twitter.com/1.1/users/lookup.json"
        params = {"screen_name": "TwitterAPI"}
        response = requests.request("GET", s, headers=self.headers, params=params)
        # Manage response codes
        if(response.status_code == 401):
            print("Wrong credentials, please check and try again")
            return False
        elif(response.status_code == 200):
            print("Correct credentials")
            return True

    # Connect to the Twitter API
    def connect_to_endpoint(self,url, params):
        try:
            response = requests.request("GET", url, headers=self.headers, params=params)
            # Manage response codes
            if response.status_code != 200:
                if (response.status_code == 429):
                    print("Rate limit exceeded, waiting for the new connection")
                    t.sleep(60)
                    return self.connect_to_endpoint(url, params)
                elif (response.status_code == 503):
                    print("The Twitter servers are up, but overloaded with requests. Waiting 5 min and retrying.")
                else:
                    print(response.status_code)
                    print("An unexpected error has occurred. Please close the software and try again")
            else:
                return response.json()
        except:
            # If the connection to the API failed, wait 60s and try again
            t.sleep(60)
            return self.connect_to_endpoint(url, params)