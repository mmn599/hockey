import sqlalchemy
import datetime
import pandas as pd

PLAYER_STATS_FILE = "PlayerStats"
HOME = "Home"
AWAY = "Away"
TABLE_GAMEOVERALL = "GAME_STATS"
TABLE_SKATERGAME = "SKATER_GAME"
TABLE_GOALIEGAME = "GOALIE_GAME"
TABLE_PLAYER = "PLAYER"
TABLE_TEAM = "TEAM"

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


def get_player_goals_scored(engine, playername, date1, date2):
	games = get_playergames_in_daterange(engine, playername, date1, date2)
	goals = games['G'].as_matrix()
	return goals.sum()

def get_opposing_skaters(engine, playergame):
    if(playergame.Home):
        team = 1
    else:
        team = 0
    sql_query = 'SELECT * from ' + TABLE_SKATERGAME + ' WHERE ' + " GameName == \'" + str(playergame.GameName) + "\' AND Home == \'" + str(team) + "\';"
    playergames = pd.read_sql_query(sql_query, engine)
    print(playergames)
