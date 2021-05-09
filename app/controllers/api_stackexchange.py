import requests
import json
class StackExchange():
    def __init__(self):
        self.url_base = "https://api.stackexchange.com/2.2/"
        self.key = "&key=4rU2hllG6ydwRrC23RuHjA(("
        self.page = 1
        self.page_size = 100
        self.current_url = ""
    
    #rota que retorna todos os sites da stackexchage
    def sites(self):
        self.format_url("&filter=!)5Go40vq3hW-*WORcvj5wWMiOVbI") #formata a url para essa rota
        print(self.current_url)
        response = requests.get(self.current_url)
        page_items = response.json()
        all_page_items = []
        all_page_items.append(page_items)
        while page_items["has_more"] == True: #loop para pegar todos os itens da resposta, serve para respostam que tem mais de uma pagina
            self.page += 1
            current_url = self.format_url("&filter=!)5Go40vq3hW-*WORcvj5wWMiOVbI")
            response = requests.get(self.current_url)
            page_items = response.json()
            all_page_items.append(page_items)
            
        return all_page_items
    
    #formatador de rotas
    def format_url(self, params_api):
        self.current_url = f"{self.url_base}sites?page={self.page}&pagesize={self.page_size}{params_api}{self.key}"
    
    """def merge_dict(dict1, dict2):
        dict3 = {**dict1, **dict2}
        for key, value in dict3.items():
            dict3[key] = [value, dict1[key]]
        return dict3"""