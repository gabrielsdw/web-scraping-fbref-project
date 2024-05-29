from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from unidecode import unidecode
from decorators import timer
from bd import Db

class WsFbref:
    def __init__(self, url_camp: str = None, db: Db = None, notes: bool = False):
        path_driver = r'./driver/msedgedriver.exe'
        service = Service(executable_path=path_driver)

        self.driver = webdriver.Edge(service=service)
        self.driver.implicitly_wait(3.5)

        self.url_camp = url_camp

        self.db = db

        self.notes = notes


    def retorna_info_time(self):
        self.driver.get(self.url_camp)
        
        links_times = self.driver.find_elements(By.XPATH, "//td[@data-stat='team']")
        
        times, links, codes = list(), list(), list()

        for link in links_times:
            tag = link.find_element(By.TAG_NAME, 'a')
            
            time = str(tag.text)
            link = tag.get_attribute('href')

            code = link.split('/')[-2]
            
            times.append(time)
            links.append(link)
            codes.append(code)

        # tava vindo informações repetidas, não sei o por que, para resolver
        # peguei apenas os 20 primeiros elementos, pois o campeonato só tem 20 times ou menos
        times = times[:20]
        links = links[:len(times)]
        codes = codes[:len(times)]

        dados = {
            'times':times,
            'links':links,
            'codes':codes
        }
        return dados
    

    def retorna_tempos_dos_gols(self, home_or_away):
        div_gols = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        div_gols = div_gols.find('div', attrs={'class':'event', 'id':'a' if home_or_away.lower()== 'home' else 'b'})
        div_gols = div_gols.find_all('div', attrs={'class':''})
        
        for div in div_gols:
            if not (div.find('div', attrs={'class':'event_icon goal'}) or  
                    div.find('div', attrs={'class':'event_icon penalty_goal'}) or  
                    div.find('div', attrs={'class':'event_icon own_goal'})):
                #print(div.find('div').prettify())
                div_gols.remove(div)
        
        gols_full_time = [str(item.get_text()).split('·')[1].strip() for item in div_gols]
        
        gols_first_time = []
        gols_second_time = []

        for gol in gols_full_time:
            if (str(gol[0]).isnumeric() and str(gol[1]).isnumeric()):
                tempo_gol = int(gol[0] + gol[1])
            else:
                tempo_gol = int('0' + gol[0])

            if tempo_gol <= 45:
                gols_first_time.append(gol)
            else:
                gols_second_time.append(gol)
        
        return gols_full_time, gols_first_time, gols_second_time
        

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
    
    
    def retorna_estatisticas_por_time(self, times, dados, save_csv = False):
        for time in times:
            print(time)
            dados_partidas_time = []
            for camp, data, link in zip(dados[time]['campeonatos'][:], dados[time]['datas'][:], dados[time]['links'][:]):
                self.driver.get(link)
                print(link)
                
                homeTeam, awayTeam = self.retorna_home_e_away()
                
                gols_home_full_time, gols_home_first_time, gols_home_second_time = self.retorna_tempos_dos_gols('home')
                gols_away_full_time, gols_away_first_time, gols_away_second_time = self.retorna_tempos_dos_gols('away')
                
                qtd_gols_home_full_time, qtd_gols_home_first_time, qtd_gols_home_second_time = len(gols_home_full_time), len(gols_home_first_time), len(gols_home_second_time)
                qtd_gols_away_full_time, qtd_gols_away_first_time, qtd_gols_away_second_time = len(gols_away_full_time), len(gols_away_first_time), len(gols_away_second_time)

                """
                print('Home')
                print(gols_home_full_time, gols_home_first_time, gols_home_second_time)
                print(qtd_gols_home_full_time, qtd_gols_home_first_time, qtd_gols_home_second_time)
                print('Away')
                print(gols_away_full_time, gols_away_first_time, gols_away_second_time)
                print(qtd_gols_away_full_time, qtd_gols_away_first_time, qtd_gols_away_second_time)
                """

                tabelas_home, tabelas_away = self.retorna_tabela_home_e_away()

                createdAt = str(datetime.now().date())
                
                nomes_valores_base = ['CreatedAt', 'Link', 'Camp', 'Date', 'HomeTeam', 'AwayTeam', 'NumberGolsFullTime-H', 'NumberGolsFirstTime-H', 'NumberGoalsSecondTime-H' ,'FullTimeGoals-H', 'FirstTimeGoals-H', 'SecondTimeGoals-H', 'NumberGoalsFullTime-A', 'NumberGoalsFirstTime-A', 'NumberGoalsSecondTime-A','FullTimeGoals-A', 'FirstTimeGoals-A', 'SecondTimeGoals-A',]
                
                valores_base = [createdAt, link, camp, data, homeTeam, awayTeam, qtd_gols_home_full_time, qtd_gols_home_first_time, qtd_gols_home_second_time, gols_home_full_time, gols_home_first_time, gols_home_second_time, qtd_gols_away_full_time, qtd_gols_away_first_time, qtd_gols_away_second_time, gols_away_full_time, gols_away_first_time, gols_away_second_time]
                
                    
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
                
                dados_partidas_time.append(data)
            
            if self.db is not None:
                self.db.insert_many_db(dados_partidas_time)

            if save_csv:    
                self.retorna_csv_time(time, dados_partidas_time)        
    
                
    def retorna_csv_time(self, time, data):
        lengths = [len(linha.keys()) for linha in data]
        index = lengths.index(max(lengths))
        columns = data[index].keys()

        for item in data:
            for column in columns:
                try:
                    item[column]
                except:
                    item[column] = None
        
        df = pd.DataFrame(data)
        df.to_csv(f'{time}.csv')

    
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


    def retorna_variaveis_todas_tabelas(self, tabelas):
        variaveis = []
        descricoes = []

        for tabela in tabelas:
            thread =  tabela.find_element(By.TAG_NAME, 'thead')
            
            trs = thread.find_elements(By.TAG_NAME, 'tr')
            tr = trs[-1]
            
            soup_ths = BeautifulSoup(tr.get_attribute('outerHTML'), 'html.parser')
            ths = soup_ths.find_all('th', attrs={'scope':'col'})
            
            for desc in ths:
                try:
                    desc = desc['data-tip']
                    desc = desc.split('</strong>')[0].replace('<strong>', '').split('<br>')[0]
                    #print(desc)
                    descricoes.append(desc)
                    
                except Exception as e:
                    descricoes.append(None)
            ths = [th.get_text() for th in ths]
        
            variaveis.append(ths)

        #####
           
        # Código para criar o notes.txt
        if self.notes:
            variaveis_temporarias = []
            for linha in variaveis:
                for variavel in linha:
                    variaveis_temporarias.append(variavel)
            
            variaveis_notes = []
            for variavel, desc in zip(variaveis_temporarias, descricoes):
                if f'{variavel} - {desc}' not in variaveis_notes:
                    variaveis_notes.append(f'{variavel} - {desc}')

            
            with open('notes.txt', 'w+') as file:
                for line in variaveis_notes:
                    file.write(f'{line}\n')
        
        #####

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
        
        for k in dados.keys():
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
        
        return cabecalhos if len(cabecalhos) > 0 else ['SUMMARY']


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
        
        try:
            homeTeam, awayTeam = teams
            return str(unidecode(homeTeam.strip().lower().replace(' ', '_'))), str(unidecode(awayTeam.strip().lower().replace(' ', '_')))
        except:
            return None, None
        
    
    @timer
    def run(self):
        info = self.retorna_info_time()
        dados = self.retorna_partidas_por_time(info['times'][:], info['links'][:])
        self.retorna_estatisticas_por_time(info['times'][:], dados)


    @timer
    def retorna_estatisticas_do_time(self, name_team: str = None, link_team: str = None, save_csv: bool = False) -> None:
        dados = self.retorna_partidas_por_time([name_team,], [link_team,])
        self.retorna_estatisticas_por_time([name_team,], dados, save_csv=save_csv)

        



if __name__ == '__main__':
    db = Db('gabrielsdw', '54321', 'fbref', 'BundesLiga')
    
    obj = WsFbref('https://fbref.com/en/comps/9/Premier-League-Stats')
    # obj.run() para pegar todas as partidas de todos os times de um campeonato
    
    # para pegar as partidas de apenas um time
    obj.retorna_estatisticas_do_time(name_team='Man city', link_team='https://fbref.com/en/squads/b8fd03ef/Manchester-City-Stats', save_csv=True)
     
   