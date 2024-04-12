from selenium.webdriver import Chrome, ChromeOptions, Edge, EdgeOptions, Firefox, FirefoxOptions
from selenium.webdriver.common.by import By

from time import sleep

import pandas as pd

import re



class WsFbref:
    def __init__(self):
        self.options = ChromeOptions()
        
        self.driver = Chrome(options=self.options)
        #self.driver.implicitly_wait(2)

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
            tags_campeonatos_partidas = self.driver.find_elements(By.XPATH, '//td[@data-stat="camp"]')
            tags_campeonatos_partidas = tags_campeonatos_partidas[:len(tags_partidas)]
            
            links = []
            datas = []
            campeonatos = []
            
            for tag_campeonato_partida, tag_data_partida, tag_partida in zip(tags_campeonatos_partidas, tags_datas_partidas, tags_partidas):
                if str(tag_partida.text).lower() != 'head-to-head':
                    link_partida = tag_partida.find_element(By.TAG_NAME, 'a')
                    link_partida = link_partida.get_attribute('href')
                    
                    data_partida = str(tag_data_partida.text)

                    campeonato_partida = tag_campeonato_partida.find_element(By.TAG_NAME, 'a')
                    campeonato_partida = str(campeonato_partida.text)


                    campeonatos.append(campeonato_partida)
                    links.append(link_partida)
                    datas.append(data_partida)
                    
            dados[time] = {
                'links': links,
                'datas': datas,
                'campeonatos': campeonatos
            }

        return dados
    
    
    def retorna_estatisticas_por_time(self, times, dados):

        for time in times:
            for camp, data, link in zip(dados[time]['campeonatos'][:5], dados[time]['datas'][:5], dados[time]['links'][:5]):
                self.driver.get(link)

                homeTeam, awayTeam = self.retorna_home_e_away_team()
                
                fthg, ftag = self.retorna_gols_home_e_away_team()

                print(homeTeam, awayTeam, fthg, ftag, data, camp)
                sleep(2.5)


    def retorna_home_e_away_team(self):
        teams = self.driver.find_element(By.TAG_NAME, 'h1')
        teams = str(teams.text)
        teams = teams.split('Match')
        teams = teams[0]
        teams = ''.join(teams)
        teams = teams.split('vs.')
        
        homeTeam, awayTeam = teams
        
        return homeTeam.strip(), awayTeam.strip()
    

    def retorna_gols_home_e_away_team(self):
        scores = self.driver.find_elements(By.XPATH, '//div[@class="score"]')
            
        lista = []

        for score in scores:
            lista.append(str(score.text))

        fthg, ftag, *_ = lista

        return fthg, ftag


       
                
                
            
                    




if __name__ == '__main__':
    obj = WsFbref()
    
    info = obj.retorna_info_time()
    
    dados = obj.retorna_partidas_por_time(info['times'][:2], info['links'][:2])

    obj.retorna_estatisticas_por_time(info['times'][:2], dados)
   