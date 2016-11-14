import scraper
import pandas as pd
from tqdm import tqdm


def get_past(df_all, timestamp):
    return df_all[df_all.DateTimestamp < timestamp]


def get_player(df_all, player):
    return df_all[df_all.Player == player]


def clean_skater_data(df_skaters):
    df_skaters = df_skaters.drop('URL', 1)
    toi = df_skaters.TOI
    numtoi = []
    for t in toi:
        n = t.split(":")
        time = int(n[0]) * 60 + int(n[1])
        numtoi.append(time)
    df_skaters.TOI = numtoi
    return df_skaters


def get_teammates(pg, df_skaters):
    df = df_skaters[df_skaters.GameName == pg.GameName]
    df = df[df.Home == pg.Home]
    df = df[df.Player != pg.Player]
    return list(df.Player)


def get_opponents(pg, df_skaters):
    df = df_skaters[df_skaters.GameName == pg.GameName]
    df = df[df.Home != pg.Home]
    return list(df.Player)


def get_skater_data(season=2015, output="Goals"):
    df_skaters = scraper.get_raw_skatergames_df(season)
    df_skaters = clean_skater_data(df_skaters)
    df_goalies = scraper.get_raw_goaliegames_df(season)

    col = ['TS', 'TS_Goals', 'TS_Assists', 'TS_PlusMinus', 'TS_SoG',
           'TS_Shot%', 'TS_ATOI', 'TM_Goals', 'TM_Shots', 'Opp_GA',
           'Opp_SA', 'Opp_SV%']
    X = pd.DataFrame(columns=col)
    y = pd.DataFrame(columns=['Goals'])

    ###
    # df_skaters = get_player(df_skaters, df_skaters.iloc[0].Player)
    ###

    for index in tqdm(range(len(df_skaters))):
        cur = df_skaters.iloc[index]
        timestamp = cur.DateTimestamp

        # All past playergames
        df_past = get_past(df_skaters, timestamp)

        # Season stats for target player
        df_past_t = get_player(df_past, cur.Player)
        drops = ['Player', 'Player.1', 'Home', 'Team', 'GameName', 'S%']
        df_past_t = df_past_t.drop(drops, 1)
        num = len(df_past_t)

        df_t_sums = df_past_t.sum(axis=0)

        # Average goals scored in past games
        t_goals = df_t_sums['G'] / num

        # Average assists scored in past season
        t_assists = df_t_sums['A'] / num

        # Plus minus
        t_plus_minus = df_t_sums['+/-']

        # Shots taken
        t_shots = df_t_sums['S'] / num

        # Shooting percentage
        if(t_shots > 0):
            t_shoot_percentage = t_goals / t_shots
        else:
            t_shoot_percentage = 0

        # ATOI
        t_atoi = df_t_sums['TOI'] / (index + 1)

        # Target team season stats
        teammates = get_teammates(cur, df_skaters)
        tm_goalspergame = 0
        tm_shotspergame = 0
        for teammate in teammates:
            df_tm_past = get_player(df_past, teammate)
            df_tm_past = df_tm_past.drop(drops, 1)
            sums = df_tm_past.sum(axis=0)
            tm_goalspergame += sums['G']
            tm_shotspergame += sums['S']
        tm_goalspergame = tm_goalspergame / num
        tm_shotspergame = tm_shotspergame / num

        df = df_goalies[df_goalies.GameName == cur.GameName]
        opp_goalie = list(df[df.Home != cur.Home].Player)[0]

        df_past_goalie = get_past(df_goalies, timestamp)
        df_opp_goalie = df_past_goalie[df_past_goalie.Player == opp_goalie]
        g_num = len(df_opp_goalie)

        opp_goalies_sums = df_opp_goalie.sum(axis=0)

        # Goals against
        opp_ga = opp_goalies_sums['GA'] / g_num
        # Shots against
        opp_sa = opp_goalies_sums['SA'] / g_num
        # Goalie save percentage
        opp_svpercentage = opp_ga / opp_sa

        cur_features = [cur.Player, t_goals, t_assists, t_plus_minus,
                        t_shots, t_shoot_percentage, t_atoi, tm_goalspergame,
                        tm_shotspergame, opp_ga, opp_sa, opp_svpercentage]
        X.loc[index] = cur_features
        y.loc[index] = cur.G

    return X, y
