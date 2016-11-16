import pandas as pd
from sklearn.externals import joblib


DROPCOLS = ['GameNum', 'GameName', 'Player', 'DateTimestamp', 'Num']


def get_training_data(seasons, output, nthresh=20, gthresh=10, dropcols=DROPCOLS):

    data = []
    for season in seasons:
        fn = str(season) + 'Skaters.p'
        data.append(joblib.load(fn))

    df = pd.concat(data)

    df = df[df.Num >= nthresh]
    df = df[df.GNum >= gthresh]
    df = df.fillna(0)
    df = df.drop(dropcols, 1)

    outputs = [x for x in df.columns.values if 'O_' in x]    
    X = df.drop(outputs, 1)

    if(output == "Goals"):
        y = df['O_Goals']
    elif(output == "Assists"):
        y = df['O_Assists']
    else:
        raise Exception('Fuck you')

    return X, y