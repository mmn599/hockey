import os
import pandas as pd
import glob
import datetime
from tqdm import tqdm
import urllib.request
from bs4 import BeautifulSoup
import time
import csv
from sklearn.externals import joblib


def get_playerstats_filenames(gamename):
    team1 = gamename + '_' + PLAYER_STATS_FILE + HOME + '.csv'
    team2 = gamename + '_' + PLAYER_STATS_FILE + AWAY + '.csv'
    return team1, team2


def gamefile_to_gamename(gamefile):
    gamename = str(gamefile)
    gamename = gamename.replace('.csv', '')
    gamename = gamename.replace("./Games\\", '')
    return gamename


def get_gamename(season, game):
    return str(season) + "_" + str(game[0])


def to_csv(file_name, headers, rows):
    with open(file_name, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            row_dict = {}
            for i, cell in enumerate(row):
                row_dict[headers[i]] = cell
            writer.writerow(row_dict)


def scrape_games_csv(url, filename):
    print('Building csv file for all overall games...')
    soup = BeautifulSoup(urllib.request.urlopen(url).read(), "lxml")

    tablehead = soup.find('thead')
    tablebody = soup.find('tbody')

    headers = []
    hs = tablehead.find('tr').find_all('th')
    for header in hs:
        text = header.text
        if(text in headers):
            text = text + ".1"
        headers.append(text)
    headers.insert(0, "URL")
    rows = []

    for row in tablebody.find_all('tr'):
        cells = [cell.text for cell in row.find_all(['th', 'td'])]
        url = 'http://www.hockey-reference.com' + \
            row.find('th').find('a')['href']
        cells.insert(0, url)
        rows.append(cells)

    to_csv(filename, headers, rows)


def adv_game_table_to_csv(file_name, adv_table, game):
    gamename = game.GameName

    adv_tablehead = adv_table.find('thead')
    adv_tablebody = adv_table.find('tbody')
    headers = [header.text for header in adv_tablehead.find_all('tr')[
        0].find_all('th')]
    for i, h in enumerate(headers):
        headers[i] = h.replace("%", "")
        headers[i] = h.replace("‑", "")

    headers.append("GameName")

    final_rows = []
    adv_rows = adv_tablebody.find_all('tr', attrs={"class": "ALLAll"})
    for adv_row in adv_rows:
        cells = [cell.text for cell in adv_row.find_all(['th', 'td'])]
        cells.append(gamename)
        final_rows.append(cells)

    to_csv(file_name, headers, final_rows)


def player_game_tables_to_csv(file_name, table, game, home):
    team = game.Home if home else game.Visitor
    timestamp = game.DateTimestamp
    url = game.URL
    gamename = game.GameName
    gamenum = game.GameNum

    tablehead = table.find('thead')
    tablebody = table.find('tbody')

    headers = []
    for header in tablehead.find_all('tr')[1].find_all('th'):
        text = header.text
        if(text in headers):
            text = text + ".1"
        headers.append(text)

    headers.append("URL")
    headers.append("DateTimestamp")
    headers.append("Home")
    headers.append("Team")
    headers.append("GameName")
    headers.append("GameNum")
    headers.pop(0)
    final_rows = []
    rows = tablebody.find_all('tr')
    for row in rows:
        cells = [cell.text for cell in row.find_all(['th', 'td'])]
        cells.append(url)
        cells.append(timestamp)
        cells.append(home)
        cells.append(team)
        cells.append(gamename)
        cells.append(gamenum)
        cells.pop(0)
        final_rows.append(cells)

    to_csv(file_name, headers, final_rows)


def build_playergame_csvs(season, game):
    page = urllib.request.urlopen(game.URL).read()
    page = page.decode('utf-8')
    page = page.replace("<!--", "")
    page = page.replace("-->", "")

    soup = BeautifulSoup(page, "lxml")
    tables = soup.find_all('table', attrs={"class": "sortable"})
    stat_tables = []
    for table in tables:
        if('suppress_csv' not in table.attrs['class']):
            stat_tables.append(table)
    skaters_away = stat_tables[0]
    goalies_away = stat_tables[1]
    skaters_home = stat_tables[2]
    goalies_home = stat_tables[3]
    adv_skaters_away = stat_tables[4]
    adv_skaters_home = stat_tables[5]

    home_skater_csv_name = get_playergame_csvname(
        season, game.GameName, home=True, skater=True)
    away_skater_csv_name = get_playergame_csvname(
        season, game.GameName, home=False, skater=True)

    player_game_tables_to_csv(home_skater_csv_name,
                              skaters_home, game, True)
    player_game_tables_to_csv(away_skater_csv_name,
                              skaters_away, game, False)

    home_goalie_csv_name = get_playergame_csvname(
        season, game.GameName, home=True, skater=False)
    away_goalie_csv_name = get_playergame_csvname(
        season, game.GameName, home=False, skater=False)
    player_game_tables_to_csv(home_goalie_csv_name,
                              goalies_home, game, True)
    player_game_tables_to_csv(away_goalie_csv_name,
                              goalies_away, game, False)

    home_adv_csv_name = get_adv_csvname(season, game.GameName, True)
    adv_game_table_to_csv(home_adv_csv_name, adv_skaters_home, game)
    away_adv_csv_name = get_adv_csvname(season, game.GameName, False)
    adv_game_table_to_csv(away_adv_csv_name, adv_skaters_away, game)

    skater_csvs = [home_skater_csv_name, away_skater_csv_name]
    goalie_csvs = [home_goalie_csv_name, away_goalie_csv_name]

    return skater_csvs, goalie_csvs


def scrape_all_playergame_csvs(season, games):
    print('Scraping and building csv files for all player stats...')
    all_skater_csvs = []
    all_goalie_csvs = []
    for i in tqdm(range(games.shape[0])):
        game = games.iloc[i]
        skater_csvs, goalie_csvs = build_playergame_csvs(season, game)
        all_skater_csvs.extend(skater_csvs)
        all_goalie_csvs.extend(goalie_csvs)
        time.sleep(1)

    return all_skater_csvs, all_goalie_csvs


# Constants
DIR_SKATERS = "Skaters/"
DIR_GOALIES = "Goalies/"
PLAYER_STATS_FILE = "PlayerStats"
ADV_FILE = "ADV"
HOME = "Home"
AWAY = "Away"

DATA_DIR = "data/"

SEASON_URLS = {
    2015: "http://www.hockey-reference.com/leagues/NHL_2016_games.html",
    2014: "http://www.hockey-reference.com/leagues/NHL_2015_games.html"}


def get_season_dir(season):
    return DATA_DIR + str(season) + "/"


def get_skater_dir(season):
    return get_season_dir(season) + DIR_SKATERS


def get_goalie_dir(season):
    return get_season_dir(season) + DIR_GOALIES


def get_overallgames_filename(season):
    return get_season_dir(season) + str(season) + "Games.csv"


def get_all_skater_csvs(season):
    return glob.glob(get_skater_dir(season) + "*.csv")


def get_all_goalie_csvs(season):
    return glob.glob(get_goalie_dir(season) + "*.csv")


def get_p_skatergames_filename(season):
    return get_season_dir(season) + "SkaterGames.p"


def get_p_goaliegames_filename(season):
    return get_season_dir(season) + "GoalieGames.p"


def get_p_overallgames_filename(season):
    return get_season_dir(season) + "OverallGames.p"


def get_playergame_csvname(season, gamename, home, skater):
    team = "HOME" if home else "AWAY"
    player = "SKATER" if skater else "GOALIE"
    if(skater):
        directory = get_skater_dir(season)
    else:
        directory = get_goalie_dir(season)
    return directory + gamename + "_" + team + "_" + player + ".csv"


def get_adv_csvname(season, gamename, home):
    directory = get_skater_dir(season)
    home = "Home" if home else "Away"
    return directory + ADV_FILE + "_" + gamename + "_" + home + ".csv"


def get_raw_overallgames_df(season):

    p_overallgames = get_p_overallgames_filename(season)

    if(os.path.isfile(p_overallgames)):
        return joblib.load(p_overallgames)

    csv_games = get_overallgames_filename(season)
    d_games = pd.read_csv(csv_games)
    gamenames = []
    gamenums = []
    dates = []

    # TODO: get rid of this for loop
    for game in d_games.iterrows():
        gamename = get_gamename(season, game)
        gamenum = game[0]
        gamenums.append(gamenum)
        gamenames.append(gamename)
        dt = datetime.datetime.strptime(game[1][1], '%Y-%m-%d')
        date = int(dt.timestamp())
        dates.append(date)

    d_games['DateTimestamp'] = dates
    d_games['GameName'] = gamenames
    d_games['GameNum'] = gamenums
    d_games = d_games.rename(index=str, columns={"Unnamed: 6": "OT"})
    d_games = d_games.drop('Notes', 1)
    d_games.OT = d_games.OT == "OT"

    joblib.dump(d_games, p_overallgames)

    return d_games


def get_raw_goaliegames_df(season):

    p_goalies = get_p_goaliegames_filename(season)

    if(os.path.isfile(p_goalies)):
        df_goalies = joblib.load(p_goalies)
        return df_goalies

    csvs_all_goalies = get_all_goalie_csvs(season)
    df_goalies = pd.DataFrame()
    goalies = []

    for csv_goalie in csvs_all_goalies:
        d_goalie = pd.read_csv(csv_goalie, encoding="latin_1")
        goalies.append(d_goalie)

    df_goalies = pd.concat(goalies)

    joblib.dump(df_goalies, p_goalies)

    return df_goalies


def get_raw_skatergames_df(season):

    p_skaters = get_p_skatergames_filename(season)

    if(os.path.isfile(p_skaters)):
        df_skaters = joblib.load(p_skaters)
        return df_skaters

    csvs_all_skaters = get_all_skater_csvs(season)

    df_skaters = pd.DataFrame()
    skaters = []
    df_adv_skaters = pd.DataFrame()
    adv_skaters = []

    for csv_skater in csvs_all_skaters:
        d = pd.read_csv(csv_skater, encoding="latin_1")
        if("ADV" in str(csv_skater)):
            adv_skaters.append(d)
        else:
            skaters.append(d)

    df_skaters = pd.concat(skaters)
    df_adv_skaters = pd.concat(adv_skaters)

    columns = {'EV.1': 'A_EV', 'PP.1': 'A_PP', 'SH.1': 'A_SH'}
    df_skaters = df_skaters.rename(columns=columns)

    df = pd.merge(df_skaters, df_adv_skaters, on=['GameName', 'Player'])

    joblib.dump(df, p_skaters)

    return df


def scrape_season(season):
    dir_season = get_season_dir(season)
    dir_goalies = get_goalie_dir(season)
    dir_skaters = get_skater_dir(season)

    if not os.path.exists(dir_season):
        os.makedirs(dir_season)

    if not os.path.exists(dir_goalies):
        os.makedirs(dir_goalies)

    if not os.path.exists(dir_skaters):
        os.makedirs(dir_skaters)

    fn_overallgames = get_overallgames_filename(season)
    season_url = SEASON_URLS[season]

    scrape_games_csv(season_url, fn_overallgames)
    d_overallgames = get_raw_overallgames_df(season)
    scrape_all_playergame_csvs(season, d_overallgames)

    print('Done!')
