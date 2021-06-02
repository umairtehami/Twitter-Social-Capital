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

    def connect_to_endpoint(self,url, params):
        try:
            response = requests.request("GET", url, headers=self.headers, params=params)
            if response.status_code != 200:
                print(response.text)
                if (response.status_code == 401):
                    print("Wrong credentials")
                    exit()
                else:
                    print("Waiting 60s and restarting conection")
                    t.sleep(60)
                    return self.connect_to_endpoint(url, params)
            else:
                return response.json()
        except:
            t.sleep(60)
            return self.connect_to_endpoint(url, params)