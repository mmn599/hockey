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

def get_player_goals_scored_in_season(engine, playername):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['G'].as_matrix()
	return goals.sum()
	
def get_player_goals_scored_in_past_games(engine, playername, game_number):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['G'].as_matrix()
	goals = goals[0:game_number]
	return goals.sum()
	
def get_player_short_handed_goals_scored_in_season(engine, playername):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['SH'].as_matrix()
	return goals.sum()
	
def get_player_short_handed_goals_scored_in_past_games(engine, playername, game_number):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['SH'].as_matrix()
	goals = goals[0:game_number]
	return goals.sum()
	
def get_player_even_handed_goals_scored_in_season(engine, playername):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['EV'].as_matrix()
	return goals.sum()
	
def get_player_even_handed_goals_scored_in_past_games(engine, playername, game_number):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['EV'].as_matrix()
	goals = goals[0:game_number]
	return goals.sum()

def get_player_power_play_goals_scored_in_season(engine, playername):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['PP'].as_matrix()
	return goals.sum()
	
def get_player_power_play_goals_scored_in_past_games(engine, playername, game_number):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['PP'].as_matrix()
	goals = goals[0:game_number]
	return goals.sum()
	
def get_player_assists_in_season(engine, playername):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['A'].as_matrix()
	return goals.sum()
	
def get_player_assists_in_past_games(engine, playername, game_number):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['A'].as_matrix()
	goals = goals[0:game_number]
	return goals.sum()

def get_player_plus_minus_in_season(engine, playername):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['+/-'].as_matrix()
	return goals.sum()
	
def get_player_plus_minus_in_past_games(engine, playername, game_number):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	print(games.columns.values)
	goals = games['+/-'].as_matrix()
	goals = goals[0:game_number]
	return goals.sum()

def get_player_shots_in_season(engine, playername):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['S'].as_matrix()
	return goals.sum()
	
def get_player_shots_in_past_games(engine, playername, game_number):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	print(games.columns.values)
	goals = games['S'].as_matrix()
	goals = goals[0:game_number]
	return goals.sum()

def get_player_shot_percentage_in_season(engine, playername):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['S'].as_matrix()
	total_shots = goals.sum()
	##MAKE SURE THAT THIS IS RETURNING THE NUMBER OF ROWS WITHOUT COUNTING THE HEADER
	total_games = games.shape[0]
	return total_shots / total_games
	
def get_player_shot_percentage_in_past_games(engine, playername, game_number):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	print(games.columns.values)
	goals = games['S'].as_matrix()
	goals = goals[0:game_number]
	total_shots = goals.sum()
	total_games = goals.shape[0]
	return total_shots / total_games

DB_NAME = "../test.db"

engine = get_engine(DB_NAME)

#current date
date2 = datetime.datetime.now()
#date way in the past
date1 = datetime.datetime(2000, 12, 1)
goals = get_player_plus_minus_in_past_games(engine, 'Mikael Backlund', 14)
print(goals)

