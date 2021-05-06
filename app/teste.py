import requests
import json

URL_BASE = "https://api.stackexchange.com/2.2/"
KEY = "&key=4rU2hllG6ydwRrC23RuHjA(("
response = requests.get(str(URL_BASE+"sites?filter=!0UswhECapWD7hCVaIajGi9K2I"+KEY))

print(type(response))
print(type(response.json().items()))
print(response.json().items())

#loads = str(response.json())
#print(type(loads))
                       
#print(json.dumps(response.json(), indent=4))

'''

sites_as_dict
sites_as_str


'''