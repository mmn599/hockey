import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
import learning
import pandas as pd
from IPython.core import display as ICD
from sklearn.externals import joblib
pd.options.display.max_columns = 999

df_2015 = learning.get_base_data(2015)
dftrain, Xtrain, ytrain = learning.prepare_base_data(df_2015, "Goals")
dftest = learning.get_base_data(2014)
ICD.display(Xtrain)

h = .02  # step size in the mesh

names = ["MLP1", "Nearest Neighbors", "Gaussian Process",
         "Decision Tree", "Random Forest", "Neural Net", "AdaBoost",
         "Naive Bayes", "QDA"]

classifiers = [
    MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(20, 20), random_state=1),
    KNeighborsClassifier(3),
    GaussianProcessClassifier(1.0 * RBF(1.0), warm_start=True),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    MLPClassifier(alpha=1),
    AdaBoostClassifier(),
    GaussianNB(),
    QuadraticDiscriminantAnalysis()]

# iterate over classifiers
for name, clf in zip(names, classifiers):
    clf.fit(Xtrain, ytrain)
    score = learning.score(dftest, clf)
    print(name)
    print(score)