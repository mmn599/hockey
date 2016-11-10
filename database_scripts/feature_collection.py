import db 
import tqdm

def build_featureset_skater_goals(playergames):
    
    X = []
    y = []

    for playergame in tqdm(playergames):
          
          t_season_goals = db.get_player_season_goals
          t_recent_goals = db.get_player_recent_goals
          t_sh_goals = db.get_player_sh_goals

