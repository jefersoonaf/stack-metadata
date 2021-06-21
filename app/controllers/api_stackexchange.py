import requests
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API_KEY")
class StackExchange():
    def __init__(self, page_size, max_pages):
        self.url_base = "https://api.stackexchange.com/2.2/"
        self.key = f"&key={API_KEY}"
        self.page = 1
        self.page_size = page_size
        self.max_pages = max_pages if max_pages != None else 100000
        self.current_url = ""
    
    #formatador de rotas
    def format_url(self, params_api):
        self.current_url = f"{self.url_base}{params_api}{self.key}"
    
    #rota que retorna todos os sites da stackexchage
    def sites(self):
        self.format_url(f"sites?page={self.page}&pagesize={self.page_size}&filter=!)5Go40vq3hW-*WORcvj5wWMiOVbI") #formata a url para essa rota
        response = requests.get(self.current_url)
        page_items = response.json()
        all_page_items = []
        all_page_items.append(page_items)
        while page_items["has_more"] == True and self.page < self.max_pages: #loop para pegar todos os itens da resposta, serve para respostam que tem mais de uma pagina
            self.page += 1
            current_url = self.format_url(f"sites?page={self.page}&pagesize={self.page_size}&filter=!)5Go40vq3hW-*WORcvj5wWMiOVbI")
            response = requests.get(self.current_url)
            page_items = response.json()
            all_page_items.append(page_items)
        return all_page_items
    
    def search_advanced(self, title_parameter, site_parameter):
        """self.format_url(f"search/advanced?page={self.page}&pagesize={self.page_size}&order=desc&sort=votes&accepted=True&title={title_parameter}&site={site_parameter}&filter=!)E0fBjq-AsnarVKlARBxRcJDFDX8j60oDmcDl3M9iAJhKYBIq")"""
        self.format_url(f"search/advanced?page={self.page}&pagesize={self.page_size}&order=desc&sort=votes&accepted=True&title={title_parameter}&site={site_parameter}&filter=!1v9wA_b0TvaNe0Jko_zIHaSwt5vMy*VHH.lMAl91lcG.cUUGmu3lkf365mQjY53oS(1")
        """self.format_url(f"search/advanced?page={self.page}&pagesize={self.page_size}&order=desc&sort=votes&accepted=True&title={title_parameter}&site={site_parameter}&filter=!SBpEoG7Z8a5aJlA_l*BbIj*_*YTAdFUkcd4Q53dk_K7tBfHZCox5iskb.DMw4chD")"""
        print(self.current_url)
        response = requests.get(self.current_url)
        page_items = response.json()
        all_page_items = []
        if page_items:
            for item in page_items["items"]:
                all_page_items.append(item)
            while page_items["has_more"] == True and self.page < self.max_pages: #loop para pegar todos os itens da resposta, serve para respostam que tem mais de uma pagina
                self.page += 1
                self.format_url(f"search/advanced?page={self.page}&pagesize={self.page_size}&order=desc&sort=votes&accepted=True&title={title_parameter}&site={site_parameter}&filter=!SBpEoG7Z8a5aJlA_l*BbIj*_*YTAdFUkcd4Q53dk_K7tBfHZCox5iskb.DMw4chD")
                response = requests.get(self.current_url)
                page_items = response.json()
                for item in page_items["items"]:
                    all_page_items.append(item)
        return all_page_items#pegar o resto da divisão por 100

    def question(self):
        pass