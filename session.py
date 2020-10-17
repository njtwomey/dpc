import requests
import json


class Session(object):
    def __init__(self, params_file):
        self.s = requests.session()
        
        login_url = 'https://www.dpchallenge.com/login.php'
        with open(params_file, 'r') as fil:
            login_params = json.load(fil)
        
        self.post(login_url, login_params)
    
    def post(self, post_url, post_params):
        req = self.s.post(post_url, data=post_params)
        return req.text
    
    def get(self, get_url):
        req = self.s.get(get_url)
        return req.text
