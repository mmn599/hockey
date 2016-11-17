from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
import learning
import pandas as pd
pd.options.display.max_columns = 999

df_2015 = learning.get_base_data(2015)
dftrain, Xtrain, ytrain = learning.prepare_base_data(df_2015, "Goals")
dftest = learning.get_base_data(2014)
dftest = dftest[len(dftest)//2:len(dftest)]

h = .02  # step size in the mesh

names = ["MLP1", "Nearest Neighbors", 
         "Decision Tree", "Random Forest", "Neural Net", "AdaBoost",
         "Naive Bayes"]

classifiers = [
    MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(20, 20), random_state=1),
    KNeighborsClassifier(1),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    MLPClassifier(alpha=1),
    AdaBoostClassifier(),
    GaussianNB()]
    

dftrain, Xtrain, ytrain = learning.prepare_base_data(df_2015, "Goals")
print('Goals')
minscore = 100000
for name, clf in zip(names, classifiers):
    clf.fit(Xtrain, ytrain)
    score = learning.score(dftest, clf_goals=clf)
    if(score<minscore):
        clfgoals = clf
        minscore = score
    print(name + " : " + str(score))
print()

minscore = 100000
dftrain, Xtrain, ytrain = learning.prepare_base_data(df_2015, "Assists")
print('Assists')
for name, clf in zip(names, classifiers):
    clf.fit(Xtrain, ytrain)
    score = learning.score(dftest, clf_assists=clf)
    if(score<minscore):
        clfassists = clf
        minscore = score
    print(name + " : " + str(score))
print()

minscore = 100000
dftrain, Xtrain, ytrain = learning.prepare_base_data(df_2015, "Shots")
print('Shots')
for name, clf in zip(names, classifiers):
    clf.fit(Xtrain, ytrain)
    score = learning.score(dftest, clf_shots=clf)
    if(score<minscore):
        clfshots = clf
        minscore = score
    print(name + " : " + str(score))
print()

minscore = 100000
dftrain, Xtrain, ytrain = learning.prepare_base_data(df_2015, "Blocks")
print('Blocks')
for name, clf in zip(names, classifiers):
    clf.fit(Xtrain, ytrain)
    score = learning.score(dftest, clf_blocks=clf)
    if(score<minscore):
        clfblocks = clf
        minscore = score
    print(name + " : " + str(score))
print()

print(clfgoals)
print(clfassists)
print(clfshots)
print(clfblocks)

score = learning.score(dftest, clfgoals, clfassists, clfshots, clfblocks)
