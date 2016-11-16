import pandas as pd
from sklearn.externals import joblib
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler 



DROPCOLS = ['GameNum', 'GameName', 'Player', 'DateTimestamp', 'Num']


def get_data(seasons, output, nthresh=20, gthresh=10, dropcols=DROPCOLS):

    if(type(seasons)==int):
        seasons = [seasons]

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
    scaler = StandardScaler()
    scaler.fit(X)
    X = scaler.transform(X)

    if(output == "Goals"):
        y = df['O_Goals']
        y[y > 0] = 1
    elif(output == "Assists"):
        y = df['O_Assists']
    else:
        raise Exception('Fuck you')

    return X, y


def visualize(clf, X_test, y_test):
    y_prob = clf.predict_proba(X_test)
    y_pred = clf.predict(X_test)
    fpr, tpr, _ = roc_curve(y_test, y_prob[:,1])
    plt.plot(fpr, tpr)
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC')
    plt.show()
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
