import scraper
season = 2015
fn_overallgames = scraper.get_overallgames_filename(2015)
season_url = scraper.SEASON_URLS[season]
scraper.scrape_games_csv(season_url, fn_overallgames)