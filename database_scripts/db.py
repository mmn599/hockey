import sqlalchemy
import datetime
import pandas as pd
import numpy as np

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
	print(goals)
	return goals.sum()
	
def get_player_goals_scored_in_past_games(engine, playername, game_number):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['G'].as_matrix()
	goals = goals[0:game_number]
	print(goals)
	return goals.sum()
	
def get_player_short_handed_goals_scored_in_season(engine, playername):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['SH'].as_matrix()
	print(goals)
	return goals.sum()
	
def get_player_short_handed_goals_scored_in_past_games(engine, playername, game_number):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['SH'].as_matrix()
	goals = goals[0:game_number]
	print(goals)
	return goals.sum()
	
def get_player_even_handed_goals_scored_in_season(engine, playername):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['EV'].as_matrix()
	print(goals)
	return goals.sum()
	
def get_player_even_handed_goals_scored_in_past_games(engine, playername, game_number):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['EV'].as_matrix()
	goals = goals[0:game_number]
	print(goals)
	return goals.sum()

def get_player_power_play_goals_scored_in_season(engine, playername):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['PP'].as_matrix()
	print(goals)
	return goals.sum()
	
def get_player_power_play_goals_scored_in_past_games(engine, playername, game_number):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	goals = games['PP'].as_matrix()
	goals = goals[0:game_number]
	print(goals)
	return goals.sum()
	
def get_player_assists_in_season(engine, playername):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	assists = games['A'].as_matrix()
	print(assists)
	return assists.sum()
	
def get_player_assists_in_past_games(engine, playername, game_number):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	assists = games['A'].as_matrix()
	assists = assists[0:game_number]
	print(assists)
	return assists.sum()

def get_player_plus_minus_in_season(engine, playername):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	plus_minus = games['+/-'].as_matrix()
	print(plus_minus)
	return plus_minus.sum()
	
def get_player_plus_minus_in_past_games(engine, playername, game_number):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	print(games.columns.values)
	plus_minus = games['+/-'].as_matrix()
	plus_minus = plus_minus[0:game_number]
	print(plus_minus)
	return plus_minus.sum()

def get_player_shots_in_season(engine, playername):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	shots = games['S'].as_matrix()
	print(shots)
	return shots.sum()
	
def get_player_shots_in_past_games(engine, playername, game_number):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	print(games.columns.values)
	shots = games['S'].as_matrix()
	shots = shots[0:game_number]
	print(shots)
	return shots.sum()

def get_player_shot_percentage_in_season(engine, playername):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	shots = games['S'].as_matrix()
	total_shots = shots.sum()
	goals = games['G'].as_matrix()
	total_goals = goals.sum()
	return (total_goals / total_shots) * 100
	
def get_player_shot_percentage_in_past_games(engine, playername, game_number):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	print(games.columns.values)
	shots = games['S'].as_matrix()
	shots = shots[0:game_number]
	total_shots = shots.sum()
	goals = games['G'].as_matrix()
	goals = goals[0:game_number]
	total_goals = goals.sum()
	return (total_goals / total_shots) * 100
	
def get_player_toi_in_season(engine, playername):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	toi = games['TOI'].as_matrix()
	total_toi_in_seconds = 0
	for x in toi:
		digits = x.split(":")
		#in the highly unlikely event that the TOI is over an hour..
		if (len(digits) == 3):
			hours = digits[0]
			minutes = digits[1]
			seconds = digits[2]
			total_toi_in_seconds = total_toi_in_seconds + (int(hours) * 60 * 60)
		else:
			minutes = digits[0]
			seconds = digits[1]
		total_toi_in_seconds = total_toi_in_seconds + (int(minutes) * 60)
		total_toi_in_seconds = total_toi_in_seconds + int(seconds)
	return total_toi_in_seconds

def get_player_toi_in_past_games(engine, playername, game_number):
	season_end = datetime.datetime(2016, 10, 12)
	season_start = datetime.datetime(2015, 10, 7)
	games = get_playergames_in_daterange(engine, playername, season_start, season_end)
	toi = games['TOI'].as_matrix()
	toi = toi[0:game_number]
	total_toi_in_seconds = 0
	for x in toi:
		digits = x.split(":")
		#in the highly unlikely event that the TOI is over an hour..
		if (len(digits) == 3):
			hours = digits[0]
			minutes = digits[1]
			seconds = digits[2]
			total_toi_in_seconds = total_toi_in_seconds + (int(hours) * 60 * 60)
		else:
			minutes = digits[0]
			seconds = digits[1]
		total_toi_in_seconds = total_toi_in_seconds + (int(minutes) * 60)
		total_toi_in_seconds = total_toi_in_seconds + int(seconds)
	return total_toi_in_seconds

def get_opposing_skaters(engine, playergame):
    if(playergame.Home):
        team = 1
    else:
        team = 0
    sql_query = 'SELECT * from ' + TABLE_SKATERGAME + ' WHERE ' + " GameName == \'" + str(playergame.GameName) + "\' AND Home == \'" + str(team) + "\';"
    playergames = pd.read_sql_query(sql_query, engine)
    print(playergames)


DB_NAME = "../test.db"

engine = get_engine(DB_NAME)

result = get_player_toi_in_past_games(engine, 'Mikael Backlund', 10)
print(result)
