import pandas as pd
from sklearn.externals import joblib
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler 
import numpy as np
from tqdm import tqdm

MISC_COLS = ['GameNum', 'GameName', 'Player', 'DateTimestamp', 'Num', 'GNum']

def clean_data(df, nthresh=20, gthresh=10, misccols=MISC_COLS):
    df = df[df.Num >= nthresh]
    df = df[df.GNum >= gthresh]
    df = df.fillna(0)
    return df


def scale_data(df):
    scaler = StandardScaler()
    scaler.fit(df)
    df = pd.DataFrame(scaler.transform(df), columns = df.columns.values)
    return df

def get_base_data(seasons):
    if(type(seasons)==int):
        seasons = [seasons]

    data = []
    for season in seasons:
        fn = str(season) + 'Skaters.p'
        data.append(joblib.load(fn))

    df = pd.concat(data)
    return df


def prepare_base_data(df, output, dropcols=MISC_COLS):
    df = clean_data(df)

    outputs = [x for x in df.columns.values if 'O_' in x]    
    X = df.drop(outputs, 1)
    X = X.drop(dropcols, 1)

    X = scale_data(X)

    if(output == "Goals"):
        y = df['O_Goals']
    elif(output == "Assists"):
        y = df['O_Assists']
    elif(output == "Shots"):
        y = df['O_Shots']
    elif(output == "Blocks"):
        y = df['O_Blocks']
    else:
        raise Exception('Fuck you')

    return df, X, y

# goals, assists, shots, blocks
WEIGHTS = np.array([3, 2, .5, .5])
OCOLS =  ["O_Goals", "O_Assists", "O_Shots", "O_Blocks"]


def getpoints(clf, X, y, weight):
    probs = clf.predict_proba(X)
    e = np.sum(np.array(range(probs.shape[1])) * probs, axis=1)
    epoints = e * weight
    apoints = y * weight
    return epoints, apoints


def score(df, clf_goals=None, clf_assists=None, clf_shots=None, clf_blocks=None):
    timestamps = list(set(list(df['DateTimestamp'])))
    diff = []

    for time in tqdm(timestamps):
        df_day = df[df.DateTimestamp == time]

        df_day, X_goals, y_goals = prepare_base_data(df_day, "Goals")
        df_day, X_assists, y_assists = prepare_base_data(df_day, "Assists")
        df_day, X_shots, y_shots = prepare_base_data(df_day, "Shots")
        df_day, X_blocks, y_blocks = prepare_base_data(df_day, "Blocks")

        expected = np.zeros((len(df_day), 1))
        actual = np.zeros((len(df_day), 1))

        clfs = [clf_goals, clf_assists, clf_shots, clf_blocks]
        Xs = [X_goals, X_assists, X_shots, X_blocks]
        ys = [y_goals, y_assists, y_shots, y_blocks]

        for clf, X, y, weight in zip(clfs, Xs, ys, WEIGHT):
            if(clf):
                epoints, apoints = getpoints(clf, X, y, weight)
                expected += epoints
                actual += apoints

        df_day['Expected'] = expected
        df_day['Actual'] = actual

        df_true_rank = df_day.sort_values('Actual', ascending=False)
        df_our_rank = df_day.sort_values('Expected', ascending=False)
        top = 10
        true = df_true_rank.iloc[0:top].sum()['Actual']
        pred = df_our_rank.iloc[0:top].sum()['Actual']
        diff.append(pred - true)

    abse = np.abs(np.array(diff)) / len(diff)

    return abse
