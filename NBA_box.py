import re
import time
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

# 得到今日比賽的 URL 連結
def get_today_games_url():
    driver = webdriver.Chrome()
    driver.get('https://watch.nba.com/')
    source = driver.page_source
    time.sleep(2)
    driver.close()
    soup = BeautifulSoup(source,'html.parser')
    content = str(soup.find_all('a',onclick=True))
    pattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    today_games = []
    for game_url in re.findall(pattern,content):
        game_url = game_url.replace("')",'')
        today_games.append(game_url)
    return today_games

# 將 url 拆解成比賽得分、主場數據、客場數據
def url_to_page_source(game_url):
    away = {}
    home = {}
    stat_json = {}
    driver = webdriver.Chrome()
    driver.get(game_url)
    time.sleep(2)
    game_result = driver.page_source
    home_stat_btn = driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[4]/div[2]')
    home_stat_btn.click()
    time.sleep(2)
    home_stat = driver.page_source
    away_stat_btn = driver.find_element_by_xpath('//*[@id="components"]/div[2]/div[2]/div/div[1]/div/div[1]')
    away_stat_btn.click()
    time.sleep(2)
    away_stat = driver.page_source
    driver.close()
    return game_result,home_stat,away_stat

# 將 page_source 抓到的 table 轉成 dataframe
def page_source_to_dataframe(source):
    soup = BeautifulSoup(source,'html.parser')
    html = soup.find(name='div',attrs={"class":"stats-table"})
    stat_df = pd.read_html(str(html))[0]
    for idx in range(1,23):
        stat_df[pd.read_html(str(html))[idx].columns[0]] = pd.read_html(str(html))[idx]
    stat_df.fillna('',inplace=True)
    stat_df.rename(columns={'球員':'Players'},inplace=True)
    stat_df['STARTER'] = stat_df['P'].apply(lambda x:True if x.isalpha() else False)
    players = stat_df['Players'].to_list()
    players.remove('總計')
    players.append('TEAM')
    stat_df['Players'] = players
    stat_df['DNP'] = stat_df['MIN'].apply(lambda x: True if x == '0:00' else False)
    fg = []
    for idx in range(len(stat_df['FGA'].tolist())):
        fg.append(str(stat_df['FGM'].tolist()[idx])+'-'+str(stat_df['FGA'].tolist()[idx]))
    pt3 = []
    for idx in range(len(stat_df['3PA'].tolist())):
        pt3.append(str(stat_df['3PM'].tolist()[idx])+'-'+str(stat_df['3PA'].tolist()[idx]))
    ft = []
    for idx in range(len(stat_df['FTA'].tolist())):
        ft.append(str(stat_df['FTM'].tolist()[idx])+'-'+str(stat_df['FTA'].tolist()[idx]))
    stat_df['FG'] = fg
    stat_df['3PT'] = pt3
    stat_df['FT'] = ft
    stat_df['TO'] = stat_df['TOV'].apply(lambda x:x)
    stat_df = stat_df.loc[:,['Players','MIN','FG','3PT','FT','OREB','DREB','REB','AST','STL','BLK','TO','PF','+/-','PTS','DNP','STARTER']]
    player_name = []
    for name in stat_df['Players'].tolist()[:-1]:
        for letter in name:
            if letter.isupper():
                name = name.replace(letter,' '+letter)
        player_name.append(name)
    player_name.append('TEAM')
    stat_df['Players'] = player_name
    return stat_df

# 將比賽得分、主場數據、客場數據整理成 json 檔後輸出
def page_source_to_json(game_result,home_stat,away_stat):
    away = {}
    home = {}
    stat_json = {}
    soup = BeautifulSoup(game_result,'html.parser')
    team_record = {}
    for team_idx in range(len(soup.find_all(name='div',title=True))):
        team_record[soup.find_all(name='div',attrs={'class':'team-name'})[team_idx].text] = soup.find_all(name='div',attrs={'class':'team-record'})[team_idx].text 
    away_score = pd.read_html(str(soup.find(name='table')))[0].iloc[0].tolist()
    home_score = pd.read_html(str(soup.find(name='table')))[0].iloc[1].tolist()
    away["team"] = away_score[0]
    away['score'] = away_score[1:]
    home["team"] = home_score[0]
    home['score'] = home_score[1:]
    for team_name in team_record.keys():
        if team_name in away_score[0]:
            away['streak'] = team_record[team_name]
    for team_name in team_record.keys():
        if team_name in home_score[0]:
            home['streak'] = team_record[team_name]
    away['players'] = json.loads(pagesource_to_dataframe(away_stat).to_json(orient = 'records'))
    home['players'] = json.loads(pagesource_to_dataframe(home_stat).to_json(orient = 'records'))
    stat_json['away'] = away
    stat_json['home'] = home
    return stat_json