import requests
import json

class StackExchange():
    def __init__(self):
        self.url_base = "https://api.stackexchange.com/2.2/"
        self.key = "&key=4rU2hllG6ydwRrC23RuHjA(("
    
    def sites(self):
        response = requests.get(f"{self.url_base}sites?filter=!0UswhECapWD7hCVaIajGi9K2I{self.key}")
        return response.json()