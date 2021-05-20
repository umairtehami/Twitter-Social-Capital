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

    def create_headers(self):
        headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
        return headers

    def connect_to_endpoint(self,url, headers, params):
        response = requests.request("GET", url, headers=headers, params=params)
        if response.status_code != 200:
            while response.status_code != 200:
                print("Esperando")
                print(response.text)
                t.sleep(60)
                response = requests.request("GET", url, headers=headers, params=params)
        return response.json()

    def connect_to_endpoint2(self,url, headers):
        response = requests.request("GET", url, headers=headers)
        if response.status_code != 200:
            while response.status_code != 200:
                print("Esperando")
                print(response.text)
                t.sleep(60)
                response = requests.request("GET", url, headers=headers)
        return response.json()