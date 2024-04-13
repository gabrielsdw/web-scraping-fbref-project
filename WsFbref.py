from selenium.webdriver import  Edge
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from time import sleep
import pandas as pd
import re
import os
from bs4 import BeautifulSoup




class WsFbref:
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
        
        self.edge_driver_path = './driver/msedgedriver.exe'
        
        self.edge_service = Service(self.edge_driver_path)

        self.edge_options = Options()
        self.edge_options.add_argument(f'user-agent={self.user_agent}')
        
        self.driver = Edge(service=self.edge_service, options=self.edge_options)
        self.driver.implicitly_wait(3.5)

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
            tags_campeonatos_partidas = self.driver.find_elements(By.XPATH, '//td[@data-stat="comp"]')
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
            for camp, data, link in zip(dados[time]['campeonatos'][:2], dados[time]['datas'][:2], dados[time]['links'][:2]):
                self.driver.get(link)

                homeTeam, awayTeam = self.retorna_home_e_away()
                
                fthg, ftag = self.retorna_gols_home_e_away_team()
               
                tabelas_home, tabelas_away = self.retorna_tabela_home_e_away()

                cabecalhos = self.retorna_cabecalhos_tabela()
                print(cabecalhos)
                sub_cabecalhos = self.retorna_sub_cabecalhos_tabelas(tabelas_home)
                print(sub_cabecalhos)     
                variaveis = self.retorna_variaveis_todas_tabelas(tabelas_home)
                print(variaveis)

              
    def retorna_variaveis_todas_tabelas(self, tabelas):
        variaveis = []
                
        for tabela in tabelas:
            thread =  tabela.find_element(By.TAG_NAME, 'thead')
            
            trs = thread.find_elements(By.TAG_NAME, 'tr')
            tr = trs[-1]
            
            soup_ths = BeautifulSoup(tr.get_attribute('outerHTML'), 'html.parser')
            ths = soup_ths.find_all('th', attrs={'scope':'col'})
            
            for th in ths:
                th = str(th.get_text())
                if th.lower() not in ['', '#', 'player', 'nation', 'min', 'pos', 'age']:
                    variaveis.append(th.upper())
        return variaveis
    

    def retorna_sub_cabecalhos_tabelas(self, tabelas):
        sub_cabecalhos = {}
        for tabela in tabelas:
                thread =  tabela.find_element(By.TAG_NAME, 'thead')
                
                trs = thread.find_elements(By.TAG_NAME, 'tr')

                tr_over_header = trs[0]
                soup_tr_over_header = BeautifulSoup(tr_over_header.get_attribute('outerHTML'), 'html.parser')
                ths_over_header = soup_tr_over_header.find_all('th')[1:]
                
                
                for th in ths_over_header:
                    if str(th.get_text()) != '':
                        sub_cabecalhos[str(th.get_text()).upper()] = int(th['colspan'])
                        
        return sub_cabecalhos
            

    def retorna_cabecalhos_tabela(self):
        cabecalhos = []
        try:
            div_cabecalhos = self.driver.find_element(By.XPATH, '//div[@class="filter switcher"]')
            soup_cabecalhos = BeautifulSoup(div_cabecalhos.get_attribute('outerHTML'), 'html.parser')
            cabecalhos = soup_cabecalhos.find_all('a', attrs={'class':'sr_preset'})
            cabecalhos = [str(item.get_text()).upper() for item in cabecalhos]
        except:
            pass   
        return cabecalhos

    def retorna_tabela_home_e_away(self):        
        divs = self.driver.find_elements(By.XPATH, '//div[@class="table_wrapper tabbed"]')
        
        # tava vindo outra tabela da mesma classe que eu não quis pegar pois nao são os dados almejados
        divs = divs[:2]
        div_home, div_away = divs
        
        tabelas_home = div_home.find_elements(By.TAG_NAME, 'table')                
        tabelas_away = div_away.find_elements(By.TAG_NAME, 'table')

        return tabelas_home, tabelas_away 
        

    def retorna_home_e_away(self):
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
    
    dados = obj.retorna_partidas_por_time(info['times'][:1], info['links'][:1])

    obj.retorna_estatisticas_por_time(info['times'][:1], dados)
   


