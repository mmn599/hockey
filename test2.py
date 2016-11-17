import features
from sklearn.externals import joblib

X = features.get_skater_data(season=2014)
joblib.dump(X, '2014Skaters.p')