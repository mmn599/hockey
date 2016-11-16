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
        # y.loc[y > 0] = 1
    elif(output == "Assists"):
        y = df['O_Assists']
    else:
        raise Exception('Fuck you')

    return df, X, y


def score(df, clf):
    timestamps = list(df['DateTimestamp'])
    timestamps = list(set(timestamps))
    diff = []
    for time in tqdm(timestamps):
        df_day = df[df.DateTimestamp == time]
        df_day, X, y = prepare_base_data(df_day, "Goals")
        yprob = clf.predict_proba(X)
        expected = np.zeros((len(df_day), 1))
        for i in range(0,yprob.shape[1]):
            probs = yprob[:,i]
            col = str(i)
            df_day[col] = probs
            expected[:,0] = expected[:,0] + (probs * i)
        df_day['E_Goals'] = expected
        df_true_rank = df_day.sort_values('O_Goals')
        df_our_rank = df_day.sort_values('E_Goals')
        top = 10
        true = df_true_rank.iloc[0:top].sum()['O_Goals']
        pred = df_our_rank.iloc[0:top].sum()['O_Goals']
        diff.append(pred - true)
    return diff
