import features
import scraper

X, y = features.get_skater_data(2015)

print(X.to_string())