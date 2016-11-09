import sys
import pandas as pd
import sqlalchemy
import glob
from IPython.core import display as ICD
import datetime
from pandas.io import sql
from tqdm import tqdm

PLAYER_STATS_FILE = "PlayerStats"
HOME = "Home"
AWAY = "Away"
TABLE_GAMEOVERALL = "GAME_STATS"
TABLE_SKATERGAME = "SKATER_GAME"
TABLE_GOALIEGAME = "GOALIE_GAME"
TABLE_PLAYER = "PLAYER"
TABLE_TEAM = "TEAM"

def get_playerstats_files(gamename):
    team1 = GAMESDIR + gamename + '_' + PLAYER_STATS_FILE + HOME + '.csv'
    team2 = GAMESDIR + gamename + '_' + PLAYER_STATS_FILE + AWAY + '.csv'
    return team1, team2

def gamefile_to_gamename(gamefile):
    gamename = str(gamefile)
    gamename = gamename.replace('.csv', '')
    gamename = gamename.replace("./Games\\", '')
    return gamename

def append_columns(game, team1, team2):
    d_game['GameName'] = gamename
    d_team1['GameName'] = gamename
    d_team2['GameName'] = gamename
    d_team1['Result'] = TEAM1
    
def get_gamename(season, game):
    return str(season) + "_" + str(game[0])

def build_games_table(db_name, csv_games):  
    print('Building database table for all overall games...')
    engine = get_engine(db_name)
    sql.execute('DROP TABLE IF EXISTS %s' % TABLE_GAMEOVERALL, engine)
    
    d_games = pd.read_csv(csv_games)
    gamenames = []
    dates = []
    
    # TODO: get rid of this for loop
    for game in d_games.iterrows():
        gamename = get_gamename(2015, game)
        gamenames.append(gamename)
        dt = datetime.datetime.strptime(game[1][1], '%Y-%m-%d')
        date = int(dt.timestamp())
        dates.append(date)
    
    d_games['DateTimestamp'] = dates
    d_games['GameName'] = gamenames
    d_games = d_games.rename(index=str, columns={"Unnamed: 6":"OT"})
    d_games = d_games.drop('Notes', 1)
    d_games.OT = d_games.OT=="OT"
    d_games.to_sql(TABLE_GAMEOVERALL, engine, if_exists='replace')
    
    return db_name
    
def build_playergames_table(db_name, all_skater_csvs, all_goalie_csvs):
    print('Building database table for all player game stats...')
    engine = get_engine(db_name)
    sql.execute('DROP TABLE IF EXISTS %s' % TABLE_SKATERGAME, engine)
    sql.execute('DROP TABLE IF EXISTS %s' % TABLE_GOALIEGAME, engine)
    
    engine = get_engine(db_name)
    
    print("Skaters...")
    for skater_csv in tqdm(all_skater_csvs):
        d_skater = pd.read_csv(skater_csv, encoding="latin_1")
        d_skater.to_sql(TABLE_SKATERGAME, engine, if_exists='append')
        
    print("Goalies...")
    for goalie_csv in tqdm(all_goalie_csvs):
        d_goalie = pd.read_csv(goalie_csv, encoding="latin_1")
        d_goalie.to_sql(TABLE_GOALIEGAME, engine, if_exists='append')

def get_engine(db_name):
    return sqlalchemy.create_engine('sqlite:///' + db_name)

def view_database(db_name, table):
    engine = get_engine(db_name)
    d_db = pd.read_sql_table(table, engine)
    ICD.display(d_db)
    
def get_all_games(db_name):
    engine = get_engine(db_name)
    d_games = pd.read_sql_table(TABLE_GAMEOVERALL, engine)
    return d_games
    
def get_game_by_gamename(engine, gamename):
    sql_query = 'SELECT * from ' + TABLE_GAMEOVERALL + ' WHERE GameName == \'' + str(gamename) + '\';'
    game = pd.read_sql_query(sql_query, engine).iloc[0]
    return game

def _get_between_date_sql_query(timestamp1, timestamp2):
    return 'DateTimestamp >= ' + str(timestamp1) + ' AND ' + 'DateTimestamp <= ' + str(timestamp2)

def get_games_in_daterange(engine, date1, date2):
    date1 = int(date1.timestamp())
    date2 = int(date2.timestamp())
    sql_query = 'SELECT * from ' + TABLE_GAMEOVERALL + ' WHERE ' + _get_between_date_sql_query(date1, date2)
    games = pd.read_sql_query(sql_query, engine)
    return games

def get_playergames_in_daterange(engine, playername, date1, date2, skater = True):
    date1 = int(date1.timestamp())
    date2 = int(date2.timestamp())
    sql_query = 'SELECT * from ' + TABLE_SKATERGAME + ' WHERE ' + 'Player == ' + "'" + \
        playername + "'"  + " AND " + _get_between_date_sql_query(date1, date2) + ";" 
    playergames = pd.read_sql_query(sql_query, engine)
    return playergames

import urllib.request
import pandas as pd
from bs4 import BeautifulSoup
import time
import csv

def headers_and_rows_to_csv(file_name, headers, rows):
    with open(file_name, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            row_dict = {}
            for i,cell in enumerate(row):
                row_dict[headers[i]] = cell
            writer.writerow(row_dict)

def build_games_csv(url, file_name):
    print('Building csv file for all overall games...')
    soup = BeautifulSoup(urllib.request.urlopen(url).read(), "lxml")

    tablehead = soup.find('thead')
    tablebody = soup.find('tbody')

    headers = [header.text for header in tablehead.find('tr').find_all('th')]
    headers.insert(0, "URL")
    rows = []

    for row in tablebody.find_all('tr'):
        cells = [cell.text for cell in row.find_all(['th','td'])]
        url = 'http://www.hockey-reference.com' + row.find('th').find('a')['href']
        cells.insert(0, url)
        rows.append(cells)
        
    headers_and_rows_to_csv(file_name, headers, rows)
    
    return file_name
    
def get_playergame_csvname(gamename, home, skater):
    team = "HOME" if home else "AWAY"
    player = "SKATER" if skater else "GOALIE"
    directory = DIR_SKATERS if skater else DIR_GOALIES
    return directory + gamename + "_" + team + "_" + player + ".csv"

def player_game_table_to_csv(file_name, table, game, home):
    team = game.Home if home else game.Visitor
    date = game.Date
    timestamp = game.DateTimestamp
    url = game.URL
    gamename = game.GameName
    
    tablehead = table.find('thead')
    tablebody = table.find('tbody')
    
    headers = [header.text for header in tablehead.find_all('tr')[1].find_all('th')]
    headers.append("URL")
    headers.append("DateTimestamp")
    headers.append("Home")
    headers.append("Team")
    headers.append("GameName")
    headers.pop(0)
    
    rows = []
    for row in tablebody.find_all('tr'):
        cells = [cell.text for cell in row.find_all(['th','td'])]
        cells.append(url)
        cells.append(timestamp)
        cells.append(home)
        cells.append(team)
        cells.append(gamename)
        cells.pop(0)
        rows.append(cells)
        
    headers_and_rows_to_csv(file_name, headers, rows)
        
def build_playergame_csvs(game):
    soup = BeautifulSoup(urllib.request.urlopen(game.URL).read(), "lxml")
    tables = soup.find_all('table')
    table_skaters_away = tables[2]
    table_goalies_away = tables[3]
    table_skaters_home = tables[4]
    table_goalies_home = tables[5]
    
    home_skater_csv_name = get_playergame_csvname(game.GameName, home=True, skater=True)
    away_skater_csv_name = get_playergame_csvname(game.GameName, home=False, skater=True)
    player_game_table_to_csv(home_skater_csv_name, table_skaters_home, game, home=True)
    player_game_table_to_csv(away_skater_csv_name, table_skaters_away, game, home=False)
    
    home_goalie_csv_name = get_playergame_csvname(game.GameName, home=True, skater=False)
    away_goalie_csv_name = get_playergame_csvname(game.GameName, home=False, skater=False)
    player_game_table_to_csv(home_goalie_csv_name, table_goalies_home, game, home=True)
    player_game_table_to_csv(away_goalie_csv_name, table_goalies_away, game, home=False)
    
    skater_csvs = [home_skater_csv_name, away_skater_csv_name]
    goalie_csvs = [table_goalies_home, table_goalies_away]
    
    return skater_csvs, goalie_csvs

def build_all_playergame_csvs(games):
    print('Scraping and building csv files for all player stats...')
    all_skater_csvs = []
    all_goalie_csvs = []
    for i in tqdm(range(games.shape[0])):
        game = games.iloc[i]
        skater_csvs, goalie_csvs = build_playergame_csvs(game)
        all_skater_csvs.extend(skater_csvs)
        all_goalie_csvs.extend(goalie_csvs)
        time.sleep(1)
        
    return all_skater_csvs, all_goalie_csvs


import os
import glob

### Constants ###
DIR_GAMES = "./data/Games/"
DIR_SKATERS = DIR_GAMES + "Skaters/"
DIR_GOALIES = DIR_GAMES + "Goalies/"
FILE_GAMES = DIR_GAMES + "2015Games.csv"
URL_Games_20152016 = "http://www.hockey-reference.com/leagues/NHL_2016_games.html"
DB_NAME = "test.db"

def build_everything(webscrape=False):
    
    if not os.path.exists(DIR_SKATERS):
        os.makedirs(DIR_SKATERS)
        
    if not os.path.exists(DIR_GOALIES):
        os.makedirs(DIR_GOALIES)
    
    if(webscrape):
        csv_games = build_games_csv(URL_Games_20152016, FILE_GAMES)
        db_name = build_games_table(DB_NAME, csv_games)
        d_games = get_all_games(db_name)
        all_skater_csvs, all_goalie_csvs = build_all_playergame_csvs(d_games)
    else:
        print('Collecting csvs...')
        all_skater_csvs = []
        all_goalie_csvs = []
        for name in glob.glob(DIR_SKATERS + "*"):
            all_skater_csvs.append(name)
        for name in glob.glob(DIR_GOALIES + "*"):
            all_goalie_csvs.append(name)
            
    build_playergames_table(DB_NAME, all_skater_csvs, all_goalie_csvs)
    print('Done!')