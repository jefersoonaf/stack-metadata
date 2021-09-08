import html
from unidecode import unidecode
class Site():
    def __init__(self, site_item):
        self.site = {
            "api_parameter": site_item["api_site_parameter"],
            "url": site_item["site_url"],
            "name": unidecode(html.unescape(site_item["name"])),            
            "audience": site_item["audience"]
        }        
        print(unidecode(html.unescape(site_item["name"])))
        
    def get_as_json(self):
        return self.__dict__