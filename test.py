import scraper

df_skaters, df_goalies = scraper.get_raw_playergames_df(2015)
print(df_goalies.columns.values)
print(df_skaters.columns.values)