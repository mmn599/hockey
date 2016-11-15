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


def get_team_stats():
    return 0
    # Target team season stats
    # # teammates = get_teammates(cur, df_skaters)
    # # tm_goalspergame = 0
    # # tm_shotspergame = 0
    # # for teammate in teammates:
    # #     df_tm_past = get_player(df_past, teammate)
    # #     df_tm_past = df_tm_past.drop(drops, 1)
    # #     sums = df_tm_past.sum(axis=0)
    # #     tm_goalspergame += sums['G']
    # #     tm_shotspergame += sums['S']
    # tm_goalspergame = tm_goalspergame / num
    # tm_shotspergame = tm_shotspergame / num


def get_skater_data(season=2015, output="Goals"):
    df_skaters = scraper.get_raw_skatergames_df(season)
    df_skaters = clean_skater_data(df_skaters)
    df_skaters = df_skaters.sort_values('GameNum', ascending=True)
    df_goalies = scraper.get_raw_goaliegames_df(season)
    df_goalies = df_goalies.sort_values('GameNum', ascending=True)
    df_overall = scraper.get_raw_overallgames_df(season)
    df_overall = df_overall.sort_values('GameNum')

    col = ['GameName', 'Player', 'DateTimestamp', 'Num',
           'O_Goals', 'O_Assists', 'O_Blocks', 'O_Shorthanded', 'O_Shots',
           'TS_Goals', 'TS_Assists', 'TS_PlusMinus', 'TS_SoG',
           'TS_Shot%', 'TS_ATOI', 'TS_iCF', 'TS_SATF', 'TS_SATA',
           'TS_ZSO', 'TS_HIT', 'TS_BLK',
           'TM_Goals', 'Opp_GA',
           'Opp_SA', 'Opp_SV%']
    X = pd.DataFrame(columns=col)

    for index in tqdm(range(len(df_skaters) // 2, len(df_skaters))):

        cur = df_skaters.iloc[index]
        timestamp = cur.DateTimestamp

        # All past playergames
        df_past = get_past(df_skaters, timestamp)

        # Season stats for target player
        df_past_t = get_player(df_past, cur.Player)
        drops = ['DateTimestamp', 'Player', 'Home',
                 'Team', 'GameName', 'S%']
        df_past_t = df_past_t.drop(drops, 1)
        num = len(df_past_t)
        df_t_sums = df_past_t.sum(axis=0)

        t_goals = df_t_sums['G'] / num
        t_assists = df_t_sums['A'] / num
        t_plus_minus = df_t_sums['+/-']
        t_shots = df_t_sums['S'] / num
        t_iCF = df_t_sums['iCF'] / num
        t_SATF = df_t_sums['SATF'] / num
        t_SATA = df_t_sums['SATA'] / num
        t_ZSO = df_t_sums['ZSO'] / num
        t_hit = df_t_sums['HIT'] / num
        t_blk = df_t_sums['BLK'] / num
        t_atoi = df_t_sums['TOI'] / num
        if(t_shots > 0):
            t_shoot_percentage = t_goals / t_shots
        else:
            t_shoot_percentage = 0

        df_overall_past = get_past(df_overall, timestamp)
        df1 = df_overall_past[df_overall_past.Home == cur.Team]
        goals_home = df1.sum(axis=0)['G.1']
        df2 = df_overall_past[df_overall_past.Visitor == cur.Team]
        goals_away = df2.sum(axis=0)['G']
        tm_goalspergame = (goals_away + goals_home) / (len(df1) + len(df2))

        df = df_goalies[df_goalies.GameName == cur.GameName]
        opp_goalie = list(df[df.Home != cur.Home].Player)[0]

        df_past_goalie = get_past(df_goalies, timestamp)
        df_opp_goalie = df_past_goalie[df_past_goalie.Player == opp_goalie]
        g_num = len(df_opp_goalie)

        opp_goalies_sums = df_opp_goalie.sum(axis=0)
        opp_ga = opp_goalies_sums['GA'] / g_num
        opp_sa = opp_goalies_sums['SA'] / g_num
        opp_svpercentage = opp_ga / opp_sa

        out_goals = cur['G']
        out_assists = cur['A']
        out_blks = cur['BLK']
        out_short = cur['SH'] + cur['A_SH']
        out_shots = cur['S']

        cur_features = [cur.GameName, cur.Player, timestamp, num,
                        out_goals, out_assists, out_blks, out_short, out_shots,
                        t_goals, t_assists, t_plus_minus, t_shots,
                        t_shoot_percentage, t_atoi, t_iCF,
                        t_SATF, t_SATA, t_ZSO, t_hit, t_blk, tm_goalspergame,
                        opp_ga, opp_sa, opp_svpercentage]

        X.loc[index] = cur_features

    return X
