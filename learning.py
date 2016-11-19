import pandas as pd
from sklearn.externals import joblib
from sklearn.preprocessing import StandardScaler 
import numpy as np

MISC_COLS = ['GameNum', 'GameName', 'Player', 'DateTimestamp', 'Num', 'GNum']

def clean_data(df, nthresh=30, gthresh=20, misccols=MISC_COLS):
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


def prepare_base_data(df, output, dropcols=MISC_COLS, scale=True, ft=None):
    df = clean_data(df)

    outputs = [x for x in df.columns.values if 'O_' in x]    
    X = df.drop(outputs, 1)
    X = X.drop(dropcols, 1)

    if(scale):
        X = scale_data(X)

    if(ft):
        X = ft.transform(X)

    if(output == "Goals"):
        y = df['O_Goals']
    elif(output == "Assists"):
        y = df['O_Assists']
    elif(output == "Shots"):
        y = df['O_Shots']
    elif(output == "Blocks"):
        y = df['O_Blocks']
    elif(output == "FPoints"):
        y = df['O_FPoints']
    else:
        raise Exception('Fuck you')

    return df, X, y

# goals, assists, shots, blocks
WEIGHTS = np.array([3, 2, .5, .5])
 
def getexppoints(model, X, y, weight):
    prob = getattr(model, "predict_prob", None)
    if prob and callable(prob):
        probs = model.predict_proba(X)
        ypred = np.sum(np.array(range(probs.shape[1])) * probs, axis=1)
    else:
        ypred = model.predict(X)
    # e = np.sum(np.array(range(probs.shape[1])) * probs, axis=1)
    epoints = ypred * weight
    apoints = y * weight
    return epoints.reshape(-1, 1), apoints.reshape(-1, 1)


def getpoints(df):
    ret = df.copy()
    ocols = [x for x in df.columns.values if 'O_' in x]    
    ret['O_FPoints'] = (ret[ocols] * WEIGHTS).sum(axis=1)
    return ret

DEFAULTFEATURES = {"Goals": None, "Assists": None, "Shots": None, "Blocks": None}

def score(df, modelsd, featuresd=DEFAULTFEATURES, softmax=None):
    timestamps = list(set(list(df['DateTimestamp'])))
    diff = []
    trues = []
    preds = []

    for time in timestamps:
        df_day = df[df.DateTimestamp == time]

        gselect = featuresd.get("Goals")
        aselect = featuresd.get("Assists")
        sselect = featuresd.get("Shots")
        bselect = featuresd.get("Blocks")

        df_day, X_goals, y_goals = prepare_base_data(df_day, "Goals", ft=gselect)
        df_day, X_assists, y_assists = prepare_base_data(df_day, "Assists", ft=aselect)
        df_day, X_shots, y_shots = prepare_base_data(df_day, "Shots", ft=sselect)
        df_day, X_blocks, y_blocks = prepare_base_data(df_day, "Blocks", ft=bselect)

        expected = np.zeros((len(df_day), 1))
        actual = np.zeros((len(df_day), 1))

        models = [modelsd.get("Goals"), modelsd.get("Assists"), 
                  modelsd.get("Shots"), modelsd.get("Blocks")]
        Xs = [X_goals, X_assists, X_shots, X_blocks]
        ys = [y_goals, y_assists, y_shots, y_blocks]

        exps = np.zeros((len(df_day), 4))

        i = 0
        for model, X, y, weight in zip(models, Xs, ys, WEIGHTS):
            if(model):
                epoints, apoints = getexppoints(model, X, y, weight)
                exps[:, i] = epoints.T
                expected += epoints
                actual += apoints

        df_day['Actual'] = actual
        if(softmax):
            df_day['Expected'] = softmax.predict(exps)
        else:
            df_day['Expected'] = expected

        df_true_rank = df_day.sort_values('Actual', ascending=False)
        df_our_rank = df_day.sort_values('Expected', ascending=False)
        top = 10
        true = df_true_rank.iloc[0:top].sum()['Actual']
        pred = df_our_rank.iloc[0:top].sum()['Actual']
        trues.append(true)
        preds.append(pred)
        diff.append(pred - true)

    abse = np.sum(np.abs(np.array(diff))) / len(diff)

    return trues, preds, abse
