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


    def retorna_info_time(self):
        self.driver.get(self.url_camp)
        
        links_times = self.driver.find_elements(By.XPATH, "//td[@data-stat='team']")

        times, links, codes = list(), list(), list()

        for link in links_times:
            tag = link.find_element(By.TAG_NAME, 'a')
            
            time = tag.text
            link = tag.get_attribute('href')

            code = link.split('/')[-2]
            
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
      
        return dados


    def retorna_partidas_por_time(self, times, links_times):
        dados = {}

        for time, link in zip(times, links_times):
            self.driver.get(link)
            
            
            tags_partidas = self.driver.find_elements(By.XPATH, "//td[@data-stat='match_report']")
            tags_datas_partidas = self.driver.find_elements(By.XPATH, "//th[@data-stat='date' and @class='left ']")
            
            links = []
            datas = []
            
            for tag_data_partida, tag_partida in zip(tags_datas_partidas, tags_partidas):
                if str(tag_partida.text).lower() != 'head-to-head':
                    link_partida = tag_partida.find_element(By.TAG_NAME, 'a')
                    link_partida = link_partida.get_attribute('href')
                    
                    data_partida = str(tag_data_partida.text)
                    
                    links.append(link_partida)
                    datas.append(data_partida)
                 
           
               
             
                    
            dados[time] = {
                'links': links,
                'datas': datas
            }

        return dados
                
            
                    




if __name__ == '__main__':
    obj = WsFbref()
    info = obj.retorna_info_time()
    
    obj.retorna_partidas_por_time(info['times'][:2], info['links'][:2])
   