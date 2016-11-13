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

    headers = [header.text for header in tablehead.find('tr').find_all('th')]
    headers.insert(0, "URL")
    rows = []

    for row in tablebody.find_all('tr'):
        cells = [cell.text for cell in row.find_all(['th', 'td'])]
        url = 'http://www.hockey-reference.com' + \
            row.find('th').find('a')['href']
        cells.insert(0, url)
        rows.append(cells)

    to_csv(filename, headers, rows)


def player_game_tables_to_csv(file_name, table, game, home, adv_table=None):
    team = game.Home if home else game.Visitor
    timestamp = game.DateTimestamp
    url = game.URL
    gamename = game.GameName

    tablehead = table.find('thead')
    tablebody = table.find('tbody')

    headers = [header.text for header in tablehead.find_all('tr')[
        1].find_all('th')]

    if(adv_table):
        adv_tablehead = adv_table.find('thead')
        adv_tablebody = adv_table.find('tbody')
        adv_headers = [header.text for header in adv_tablehead.find_all('tr')[
            0].find_all('th')]
        for i, h in enumerate(adv_headers):
            adv_headers[i] = h.replace("%", "")
            adv_headers[i] = h.replace("‑", "")

        headers.extend(adv_headers)

        headers.append("URL")
        headers.append("DateTimestamp")
        headers.append("Home")
        headers.append("Team")
        headers.append("GameName")
        headers.pop(0)

        final_rows = []
        rows = tablebody.find_all('tr')
        adv_rows = adv_tablebody.find_all('tr', attrs={"class": "ALLAll"})
        for row, adv_row in zip(rows, adv_rows):
            cells = [cell.text for cell in row.find_all(['th', 'td'])]
            adv_cells = [cell.text for cell in adv_row.find_all(['th', 'td'])]
            cells.extend(adv_cells)
            cells.append(url)
            cells.append(timestamp)
            cells.append(home)
            cells.append(team)
            cells.append(gamename)
            cells.pop(0)
            final_rows.append(cells)
    else:
        headers.append("URL")
        headers.append("DateTimestamp")
        headers.append("Home")
        headers.append("Team")
        headers.append("GameName")
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
            cells.pop(0)
            final_rows.append(cells)

    to_csv(file_name, headers, final_rows)


def build_playergame_csvs(season, game):
    page = urllib.request.urlopen(game.URL).read()
    page = page.decode('utf-8')
    page = page.replace("<!--", "")
    page = page.replace("-->", "")

    soup = BeautifulSoup(page, "lxml")
    tables = soup.find_all('table')
    skaters_away = tables[6]
    goalies_away = tables[7]
    skaters_home = tables[8]
    goalies_home = tables[9]
    adv_skaters_home = tables[10]
    adv_skaters_away = tables[11]

    home_skater_csv_name = get_playergame_csvname(
        season, game.GameName, home=True, skater=True)
    away_skater_csv_name = get_playergame_csvname(
        season, game.GameName, home=False, skater=True)

    player_game_tables_to_csv(home_skater_csv_name,
                              skaters_home, game, True, adv_skaters_home)
    player_game_tables_to_csv(away_skater_csv_name,
                              skaters_away, game, False, adv_skaters_away)

    home_goalie_csv_name = get_playergame_csvname(
        season, game.GameName, home=True, skater=False)
    away_goalie_csv_name = get_playergame_csvname(
        season, game.GameName, home=False, skater=False)
    player_game_tables_to_csv(home_goalie_csv_name,
                              goalies_home, game, True)
    player_game_tables_to_csv(away_goalie_csv_name,
                              goalies_away, game, False)

    skater_csvs = [home_skater_csv_name, away_skater_csv_name]
    goalie_csvs = [home_goalie_csv_name, away_goalie_csv_name]

    return skater_csvs, goalie_csvs


def build_all_playergame_csvs(season, games):
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
FILE_GAMES = "2015Games.csv"
PLAYER_STATS_FILE = "PlayerStats"
HOME = "Home"
AWAY = "Away"

DATA_DIR = "data/"

SEASON_URLS = {
    2015: "http://www.hockey-reference.com/leagues/NHL_2016_games.html"}


def get_season_dir(season=2015):
    return DATA_DIR + str(season) + "/"


def get_skater_dir(season=2015):
    return get_season_dir(season) + DIR_SKATERS


def get_goalie_dir(season=2015):
    return get_season_dir(season) + DIR_GOALIES


def get_overallgames_filename(season=2015):
    return get_season_dir(season) + str(season) + "Games.csv"


def get_all_skater_csvs(season=2015):
    return glob.glob(get_skater_dir(season) + "*.csv")


def get_all_goalie_csvs(season=2015):
    return glob.glob(get_goalie_dir(season) + "*.csv")


def get_p_skatergames_filename(season=2015):
    return get_season_dir(season) + "SkaterGames.p"


def get_p_goaliegames_filename(season=2015):
    return get_season_dir(season) + "GoalieGames.p"


def get_p_overallgames_filename(season=2015):
    return get_season_dir(season) + "OverallGames.p"


def get_playergame_csvname(season, gamename, home, skater):
    team = "HOME" if home else "AWAY"
    player = "SKATER" if skater else "GOALIE"
    if(skater):
        directory = get_skater_dir(season)
    else:
        directory = get_goalie_dir(season)
    return directory + gamename + "_" + team + "_" + player + ".csv"


def get_raw_overallgames_df(season):

    p_overallgames = get_p_overallgames_filename(2015)

    if(os.path.isfile(p_overallgames)):
        return joblib.load(p_overallgames)

    csv_games = get_overallgames_filename(season)
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
    d_games = d_games.rename(index=str, columns={"Unnamed: 6": "OT"})
    d_games = d_games.drop('Notes', 1)
    d_games.OT = d_games.OT == "OT"

    joblib.dump(d_games, p_overallgames)

    return d_games


def get_raw_playergames_df(season):

    p_skaters = get_p_skatergames_filename(season)
    p_goalies = get_p_goaliegames_filename(season)

    if(os.path.isfile(p_skaters)):
        df_skaters = joblib.load(p_skaters)
        df_goalies = joblib.load(p_goalies)
        return df_skaters, df_goalies

    csvs_all_skaters = get_all_skater_csvs(season)
    csvs_all_goalies = get_all_goalie_csvs(season)
    df_skaters = pd.DataFrame()
    df_goalies = pd.DataFrame()
    skaters = []
    goalies = []

    for csv_skater, csv_goalie in zip(csvs_all_skaters, csvs_all_goalies):
        d_skater = pd.read_csv(csv_skater, encoding="latin_1")
        skaters.append(d_skater)
        d_goalie = pd.read_csv(csv_goalie, encoding="latin_1")
        goalies.append(d_goalie)

    df_skaters = pd.concat(skaters)
    df_goalies = pd.concat(goalies)

    joblib.dump(df_skaters, p_skaters)
    joblib.dump(df_goalies, p_goalies)

    return df_skaters, df_goalies


def scrape_season(season=2015):
    dir_goalies = get_goalie_dir(season)
    dir_skaters = get_skater_dir(season)

    if not os.path.exists(dir_goalies):
        os.makedirs(DIR_SKATERS)

    if not os.path.exists(dir_skaters):
        os.makedirs(DIR_GOALIES)

    fn_overallgames = get_overallgames_filename(season)
    season_url = SEASON_URLS[season]

    scrape_games_csv(season_url, fn_overallgames)
    d_overallgames = get_raw_overallgames_df(season)[0:1]
    build_all_playergame_csvs(season, d_overallgames)

    print('Done!')
