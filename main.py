from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

from time import sleep

import re



class WsFbref:
    def __init__(self):
        self.driver = Chrome()
        self.driver.implicitly_wait(0.5)

        self.url_base = "https://fbref.com"
        self.url_camp = f"{self.url_base}/en/comps/9/Premier-League-Stats"

    def retorna_info_time(self, informacoes_desejadas: list = ['times', 'codes', 'links']):
        self.driver.get(self.url_camp)
        
        links_times = self.driver.find_elements(By.XPATH, "//td[@data-stat='team']")

        times, links, codes = list(), list(), list()

        for link in links_times:
            tag = link.find_element(By.TAG_NAME, 'a')
            
            time = tag.text
            link = tag.get_attribute('href')

            code = link.split('/')[-2]
            print(link)
            times.append(time)
            links.append(link)
            codes.append(code)

        # tava vindo informações repetidas, não sei o por que, para resolver
        # peguei apenas os 20 primeiros elementos, pois o campeonato só tem 20 times
        times = times[:20]
        links = links[:len(times)]
        codes = codes[:len(times)]

        dados = {
            'times':times,
            'links':links,
            'codes':codes
        }
       
        dados_escolhidos = {}

        if len(informacoes_desejadas) == 1:
            return dados[informacoes_desejadas[0]]
        
        for info in informacoes_desejadas:
            dados_escolhidos[info] = dados[info]
        return dados_escolhidos



if __name__ == '__main__':
    obj = WsFbref()
    info = obj.retorna_info_time(informacoes_desejadas=['codes'])
    print(info)

   