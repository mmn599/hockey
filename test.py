import features

print('starting')
X = features.get_skater_data()
X = X['DateTimestamp']
X = list(X[0])
X = X[0]
print(type(X))
