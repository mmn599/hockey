import learning
import pandas as pd
from IPython.core import display as ICD
from sklearn.externals import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler 
from sklearn.ensemble import AdaBoostClassifier
import pandas as pd

df_2015 = learning.get_base_data(2015)
dftrain, Xtrain, ytrain = learning.prepare_base_data(df_2015, "Goals")
dftest = learning.get_base_data(2014)

clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(20, 20), random_state=1)
clf.fit(Xtrain, ytrain)

ret = learning.score(dftest, clf)
print(ret)