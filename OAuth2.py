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
        response = {}
        try:
            response = requests.request("GET", url, headers=self.headers, params=params)
        except:
            return response
        if response.status_code != 200:
            while response.status_code != 200:
                print("Esperando")
                print(response.text)
                t.sleep(60)
                try:
                    response = requests.request("GET", url, headers=self.headers, params=params)
                except:
                    return response
        return response.json()