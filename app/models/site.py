class Site():
    def __init__(self, site_item):
        self.site = {
            "api_parameter": site_item["related_sites"][0]["api_site_parameter"],
            "url": site_item["related_sites"][0]["site_url"],
            "name": site_item["name"],
            "audience": site_item["audience"],
            "launch_date": site_item["launch_date"],
            "high_resolution_icon_url": site_item["high_resolution_icon_url"],
            "favicon_url": site_item["favicon_url"],
            "icon_url": site_item["icon_url"],
            "logo_url": site_item["logo_url"]
        }
        
    def get_as_json(self):
        return self.__dict__