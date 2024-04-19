from selenium.webdriver import  Edge
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from time import sleep
import pandas as pd
import re
import os
from bs4 import BeautifulSoup
from random import randint



class WsFbref:
    def __init__(self):
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
        
        edge_driver_path = './driver/msedgedriver.exe'
        
        edge_service = Service(edge_driver_path)

        edge_options = Options()
        edge_options.add_argument(f'user-agent={user_agent}')
        
        self.driver = Edge(service=edge_service, options=edge_options)
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
            print(time)
            for camp, data, link in zip(dados[time]['campeonatos'][:4], dados[time]['datas'][:4], dados[time]['links'][:4]):
                self.driver.get(link)

                homeTeam, awayTeam = self.retorna_home_e_away()
                
                fthg, ftag = self.retorna_gols_home_e_away_team()
               
                tabelas_home, tabelas_away = self.retorna_tabela_home_e_away()
                nomes_valores_base = ['CAMP', 'DATA', 'HomeTeam', 'AwayTeam', 'FTG-H', 'FTG-A']
                valores_base = [camp, data, homeTeam, awayTeam, int(fthg), int(ftag)]
                cabecalhos = self.retorna_cabecalhos_tabela()
                
                sub_cabecalhos_home = self.retorna_sub_cabecalhos_tabelas(tabelas_home)
                variaveis_home = self.retorna_variaveis_todas_tabelas(tabelas_home)
                variaveis_renomeadas_home = self.retorna_variaveis_renomeadas(cabecalhos, sub_cabecalhos_home, variaveis_home, home_or_away='H')

                sub_cabecalhos_away = self.retorna_sub_cabecalhos_tabelas(tabelas_away)
                variaveis_away = self.retorna_variaveis_todas_tabelas(tabelas_away)
                variaveis_renomeadas_away = self.retorna_variaveis_renomeadas(cabecalhos, sub_cabecalhos_away, variaveis_away, home_or_away='A')


                valores_variaveis_home = self.retorna_valores_variaveis(tabelas_home, sub_cabecalhos_home)
                valores_variaveis_away = self.retorna_valores_variaveis(tabelas_away, sub_cabecalhos_away)
                
                variaveis_renomeadas_home.extend(variaveis_renomeadas_away)
                valores_variaveis_home.extend(valores_variaveis_away)

                variaveis = variaveis_renomeadas_home[:]
                valores_variaveis = valores_variaveis_home[:]

                variaveis = nomes_valores_base + variaveis
                valores_variaveis = valores_base + valores_variaveis
                
                data = self.juntar_nomes_variaveis_com_valores(variaveis, valores_variaveis)
                print(data)

    def juntar_nomes_variaveis_com_valores(self, nomes_variaveis, valores_variaveis):
        return {k:v for k, v in zip(nomes_variaveis, valores_variaveis)}
             


    def retorna_valores_variaveis(self, tabelas, sub_cabecalhos):
        valores = []
        for tabela in tabelas:
            tfoot = tabela.find_element(By.TAG_NAME, 'tfoot')
            
            soup_tfoot = BeautifulSoup(tfoot.get_attribute('outerHTML'), 'html.parser')
            tds = soup_tfoot.find_all('td')
            ths = soup_tfoot.find_all('th')
            ths.extend(tds)          
            
            for th in ths:
                try: 
                    valores.append(float(th.get_text()))
                except:
                    valores.append(None)

        intervalos = self.retorna_intervalos_entre_sub_cabecalhos(sub_cabecalhos)

        valores_filtrados = []    
        for sub_cabecalho, (inicio, fim) in intervalos:
            for i in range(inicio, fim):
                if not 'remove' in sub_cabecalho:
                    try:
                        valores_filtrados.append(valores[i])
                    except (IndexError):
                        pass
        return valores_filtrados

            
    def retorna_variaveis_renomeadas(self, cabecalhos, sub_cabecalhos, variaveis, home_or_away):
        
        home_or_away = 'H' if home_or_away.lower()[0] == 'h' else 'A'

        for cabecalho, tabela in list(zip(cabecalhos, sub_cabecalhos.keys())):
            for index, x in enumerate(sub_cabecalhos[tabela]):
                x[0] = f'{cabecalho}-{x[0]}'
                sub_cabecalhos[tabela][index] = x
        
        lista_variaveis = []
        # tirando as variaveis da matriz para um array
        for x in variaveis:
            for variavel in x:
                lista_variaveis.append(variavel)

        variaveis_renomeadas = []

        intervalos = self.retorna_intervalos_entre_sub_cabecalhos(sub_cabecalhos)
        
        for sub_cabecalho, (inicio, fim) in intervalos:
            for i in range(inicio, fim):
                if not 'remove' in sub_cabecalho:
                    try:
                        string = f'{sub_cabecalho}-{lista_variaveis[i]}-{home_or_away}'.replace(' ', '').upper()
                        variaveis_renomeadas.append(string)
                    except (IndexError):
                        pass
        
        return variaveis_renomeadas


    def retorna_strings_abreviadas(self, strings):
        strings_abreviadas = []
        
        for string in strings:
            string.replace(' ', '')
            inicio, meio, fim = string[0], string[round((len(string)/2))], string[-1]
            string = inicio+meio+fim
            strings_abreviadas.append(string)
        return strings_abreviadas
            

    def retorna_variaveis_todas_tabelas(self, tabelas):
        variaveis = []
        
        for tabela in tabelas:
            thread =  tabela.find_element(By.TAG_NAME, 'thead')
            
            trs = thread.find_elements(By.TAG_NAME, 'tr')
            tr = trs[-1]
            
            soup_ths = BeautifulSoup(tr.get_attribute('outerHTML'), 'html.parser')
            ths = soup_ths.find_all('th', attrs={'scope':'col'})
            ths = [th.get_text() for th in ths]
            variaveis.append(ths)
        
        return variaveis


    def retorna_intervalos_entre_sub_cabecalhos(self, sub_cabecalhos):
        l = []
        for k, v in sub_cabecalhos.items():
            for item in v:
                l.append(item)

        keys = [item[0] for item in l]
        values = [item[1] for item in l]
        
        sum = 0
        intervalos = []
        for k, v in zip(keys, values):
            intervalos.append([k, [sum, sum+v]])
            sum += v
        
        return intervalos
    

    def retorna_sub_cabecalhos_tabelas(self, tabelas):
        dados = {}
        
        for index, tabela in enumerate(tabelas, 1):
            sub_cabecalhos = []
            thread =  tabela.find_element(By.TAG_NAME, 'thead')
            
            trs = thread.find_elements(By.TAG_NAME, 'tr')

            tr_over_header = trs[0]
            soup_tr_over_header = BeautifulSoup(tr_over_header.get_attribute('outerHTML'), 'html.parser')
            ths_over_header = soup_tr_over_header.find_all('th')
            
            for th in ths_over_header:
                if str(th.get_text()) == '':
                    try:
                        sub_cabecalhos.append(['Generic', int(th['colspan'])])
                    except (KeyError):
                        sub_cabecalhos.append(['Generic', 1])
                else:
                    try:
                        sub_cabecalhos.append([str(th.get_text()), int(th['colspan'])])
                    except:
                        pass
            dados[f'tabela-{index}'] = sub_cabecalhos
        
        #dados = {k:v[1:] for k, v in dados.items()} 

        for k, v in dados.items():
            dados[k][0][0] = 'remove'
    
        return dados    
    

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
   


