# -*- coding: utf-8 -*-
"""project_550.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZjtXZ5NMI7hKqpY67q1lPHqYKUThQ73I
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
df = pd.read_csv("dataset.csv")

def getUpperLowerLimit(df,colName):
    Q1 = df[colName].quantile(0.25)
    Q3 = df[colName].quantile(0.75)
    IQR = Q3 - Q1
    lowerLimit = Q1-(1.5*IQR)
    upperLimit = Q3+(1.5*IQR)
    return lowerLimit ,upperLimit
df.head()

from google.colab import drive
drive.mount('/content/drive')

df.head()

## Imputing Categorical values with mode
df[['ethnicity','gender','icu_admit_source','icu_stay_type','icu_type','apache_post_operative','arf_apache','gcs_eyes_apache','gcs_motor_apache','gcs_unable_apache','gcs_verbal_apache','intubated_apache','ventilated_apache','aids','cirrhosis','diabetes_mellitus','hepatic_failure','immunosuppression','leukemia','lymphoma','solid_tumor_with_metastasis','apache_3j_bodysystem','apache_2_bodysystem']] = df[['ethnicity','gender','icu_admit_source','icu_stay_type','icu_type','apache_post_operative','arf_apache','gcs_eyes_apache','gcs_motor_apache','gcs_unable_apache','gcs_verbal_apache','intubated_apache','ventilated_apache','aids','cirrhosis','diabetes_mellitus','hepatic_failure','immunosuppression','leukemia','lymphoma','solid_tumor_with_metastasis','apache_3j_bodysystem','apache_2_bodysystem']].fillna(df.mode().iloc[0])
## Imputing Continuous value with mean
df = df.fillna(df.mean())
# dropping 'Unnamed column'
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

#Outlier Treatment for 'weight'
weightBefore = df.weight

wLL ,wUL = getUpperLowerLimit(df,'weight')
df = df.loc[(df['weight']<wUL) & (df['weight']>wLL)]
weightAfter = df.weight

#Boxplot
plt.rcParams["figure.figsize"] = [7.50, 5.50]
plt.rcParams["figure.autolayout"] = True
toPlot = [weightBefore,weightAfter]
plt.boxplot(toPlot,labels = ['Before Outlier Treatment','After Outlier Treatment'])
plt.show()

#Outlier Treatment for 'bmi'
bmiBefore = df.bmi 
bLL ,bUL = getUpperLowerLimit(df,'bmi')
df = df.loc[(df['bmi']<bUL) & (df['bmi']>bLL)]
bmiAfter = df.bmi 

#Boxplot
plt.rcParams["figure.figsize"] = [7.50, 5.50]
plt.rcParams["figure.autolayout"] = True
toPlot = [bmiBefore,bmiAfter]
plt.boxplot(toPlot,labels = ['Before Outlier Treatment','After Outlier Treatment'])
plt.show()

#Analysing the balance of the dataset
temp = df.groupby('hospital_death').count()['patient_id']
toPLot = [temp[0],temp[1]]
lables = ['Survives', 'Does not survive']
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
plt.bar(lables,toPLot)
plt.show()

df.to_csv('new_dataset.csv')

corrMat = df.corr().abs()
corrMat.to_csv('CorrelationMatrix.csv')
print('Variables with lowest correlation with the Target are...')
print(corrMat['hospital_death'].sort_values().head(20))

print('Variables with highest correlation with the Target are...')
print(corrMat['hospital_death'].sort_values(ascending=[False]).head(50))

# Because our dataset is imbalanced, i'm going to remove every other record from the majority class (live)
# Then try again at a third
# then at a fourth
# Compare baseline accuracy with model accuracy
# Okay but first, Seperate by deaths and live so that we can operate on the majority class (live)

deaths = df.loc[df['hospital_death'] == 1]
#deaths.head()
print(len(deaths))

live = df.loc[df['hospital_death'] == 0]
#live.head()
print(len(live))

"""RESAMPLING

"""

# Resample at 50%: Removing half the values of live
# We can redo resampling and keep changing this value to find better results

#print(len(live))
# Divide length of majority class by 2, floor value (no remainder)
# Use this value (half of it) as the value for n in sample
samplehalf = (len(live))//2
#print(samplehalf)

# Randomly sample live for n samples, where n = half the length of original live
live50sample = live.sample(n=samplehalf)
#print(len(live50sample))

# Combine them back together
# df50 IS THE DATAFRAME WHERE WE HAVE SAMPLED AT 50% FOR MAJORITY CLASS!!
frames50 = [deaths, live50sample]
df50 = pd.concat(frames50)
#df.head()
print(len(df50))

# RESAMPLE AT 25%
# Divide length of majority class by 4, floor value (no remainder)
# Use this value (half of it) as the value for n in sample
samplequarter = (len(live))//4

# Randomly sample live for n samples, where n = half the length of original live
live25sample = live.sample(n=samplequarter)
#print(len(live50sample))

# Combine them back together
# df25 IS THE DATAFRAME WHERE WE HAVE SAMPLED AT 25% FOR MAJORITY CLASS!!
frames25 = [deaths, live25sample]
df25 = pd.concat(frames25)
#df.head()
print(len(df25))

# RESAMPLE AT 12.5%
# Divide length of majority class by 8, floor value (no remainder)
# Use this value (half of it) as the value for n in sample
sampleeigth = (len(live))//8

# Randomly sample live for n samples, where n = half the length of original live
live12p5sample = live.sample(n=sampleeigth)

# Combine them back together
# df50 IS THE DATAFRAME WHERE WE HAVE SAMPLED AT 50% FOR MAJORITY CLASS!!
frames12p5 = [deaths, live12p5sample]
df12p5 = pd.concat(frames12p5)
#df.head()
print(len(df12p5))

"""TEST 1: RUN EVERYTHING AT HALF MAJORITY CLASS SAMPLE"""

# sklearn
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from yellowbrick.regressor import ResidualsPlot
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import plot_confusion_matrix
from sklearn.metrics import classification_report

# Need to convert categorical variables to dummy variables so sklearn doesn't freak out about strings
X=pd.get_dummies(df50.loc[:])

 # drop unreleated atrributes
X = X.drop(['encounter_id','aids', 'd1_diasbp_max','patient_id','d1_diasbp_noninvasive_max', 'hospital_id','lymphoma','d1_spo2_max','cirrhosis'\
            ,'arf_apache','hepatic_failure','d1_glucose_min','height','icu_id'], axis=1)

# Create test / train split
X = X.drop(['hospital_death'], axis=1)
y = df50['hospital_death']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=2020)

# Find baseline Accuracy
from sklearn.dummy import DummyClassifier
dummy_classifier = DummyClassifier(strategy='most_frequent')
dummy_classifier.fit(X_train, y_train)
baseline = dummy_classifier.score(X_test, y_test)
print("Baseline Accuracy:", baseline)

# When live (majority class) is halved, baseline accuracy is 84.49%

## Build Models
# Decision Tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import accuracy_score
import numpy as np
from sklearn import tree

Tree = DecisionTreeClassifier(max_depth=6, criterion="gini", random_state=2020)
Tree.fit(X_train,y_train)
ypred = Tree.predict((X_test))

fn = X.columns
cn = y.unique()
plt.figure(figsize = (18, 18))
HeartDecisionTree = tree.plot_tree(Tree, class_names=['died', 'survived'], filled = True)
plt.savefig('Survival50.png')
plt.show()

# Evaluate Dtree
training_pred = Tree.predict(X_train)
acc_training = accuracy_score(training_pred, y_train)
print("Training Accuracy:", acc_training)

ypred = Tree.predict((X_test))
acc_testing = accuracy_score(ypred, y_test)
print("Testing Accuracy: ", acc_testing)

# Find most Important features for Decision tree to predict
#print("Feature Importance:", dt.feature_importances_)
importance=pd.DataFrame(zip(X_train.columns, Tree.feature_importances_))
#print(importance)
importance.nlargest(10, 1)

# random forest, log regression, linear regression
def accuracyCalculator (trainpredictor,testPredictor,trainData,testData):
  trainAccuracy = accuracy_score(trainpredictor, trainData)
  testAccuracy = accuracy_score(testPredictor, testData)
  print("Training Accuracy:", trainAccuracy)
  print("Testing Accuracy:", testAccuracy)
  print((classification_report(y_test, testPredictor)))

#Random Forest Classifier
randomForestclf = RandomForestClassifier(n_estimators=15)
randomForestclf.fit(X_train,y_train)
testPredictor = randomForestclf.predict(X_test)
trainPredictor = randomForestclf.predict(X_train)
accuracyCalculator(trainPredictor,testPredictor ,y_train , y_test)



# Plotting and saving 3 out of the 15 estimators used in Random Forest Classifier
for i in range(1,4):
  varName = 'fig{}'.format(i)
  varName = plt.figure(i,figsize=(18, 18))
  plt.title('Estimator{}'.format(i))
  tree.plot_tree(randomForestclf.estimators_[i],filled = True,impurity=True, rounded=True)
  strName = 'Estimator{}.png'.format(i)
  varName.savefig(strName)
  varName.show()

feature_importances = randomForestclf.feature_importances_
features = X_train.columns
df = pd.DataFrame({'features': features, 'importance': feature_importances})
df = df.sort_values(by='importance', ascending=False)
print(df.iloc[0:10, :])

# Logistic Regression

# import the class
from sklearn.linear_model import LogisticRegression

# instantiate the model (using default parameters)
logReg = LogisticRegression()

# fit the model with data
logReg.fit(X_train, y_train)

# make predictions
y_pred = logReg.predict(X_test)

# evaluate the performance
from sklearn import metrics
cnf_matrix = metrics.confusion_matrix(y_test, y_pred)

print(cnf_matrix)
print('Accuracy:', metrics.accuracy_score(y_test, y_pred))

print(metrics.classification_report(y_pred,y_test))

"""**TEST TWO: OK NOW WE TRY WITH 25% RESAMPLING** **RATE**!! """

# sklearn
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from yellowbrick.regressor import ResidualsPlot
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import plot_confusion_matrix
from sklearn.metrics import classification_report

# Need to convert categorical variables to dummy variables so sklearn doesn't freak out about strings
X=pd.get_dummies(df25.loc[:])


X = X.drop(['encounter_id','aids', 'd1_diasbp_max','patient_id','d1_diasbp_noninvasive_max', 'hospital_id','lymphoma','d1_spo2_max','cirrhosis'\
            ,'arf_apache','hepatic_failure','d1_glucose_min','height','icu_id'], axis=1)

# Create test / train split
X = X.drop(['hospital_death'], axis=1)
y = df25['hospital_death']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=2020)

# Find baseline Accuracy
from sklearn.dummy import DummyClassifier
dummy_classifier = DummyClassifier(strategy='most_frequent')
dummy_classifier.fit(X_train, y_train)
baseline = dummy_classifier.score(X_test, y_test)
print("Baseline Accuracy:", baseline)

# When live (majority class) is QUARTERED, baseline accuracy is 73%

# Decision Tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import accuracy_score
import numpy as np
from sklearn import tree

Tree = DecisionTreeClassifier(max_depth=6, criterion="gini", random_state=2020)
Tree.fit(X_train,y_train)
ypred = Tree.predict((X_test))

fn = X.columns
cn = y.unique()
plt.figure(figsize = (18, 18))
HeartDecisionTree = tree.plot_tree(Tree, class_names=['died', 'survived'], filled = True)
plt.savefig('Survival25.png')
plt.show()

# Evaluate Dtree
training_pred = Tree.predict(X_train)
acc_training = accuracy_score(training_pred, y_train)
print("Training Accuracy:", acc_training)

ypred = Tree.predict((X_test))
acc_testing = accuracy_score(ypred, y_test)
print("Testing Accuracy: ", acc_testing)

# Find most Important features for Decision tree to predict
#print("Feature Importance:", dt.feature_importances_)
importance=pd.DataFrame(zip(X_train.columns, Tree.feature_importances_))
#print(importance)
importance.nlargest(10, 1)

#Random Forest Classifier
randomForestclf = RandomForestClassifier(n_estimators=15)
randomForestclf.fit(X_train,y_train)
testPredictor = randomForestclf.predict(X_test)
trainPredictor = randomForestclf.predict(X_train)
accuracyCalculator(trainPredictor,testPredictor ,y_train , y_test)



# Plotting and saving 3 out of the 15 estimators used in Random Forest Classifier
# for i in range(1,4):
#   varName = 'fig{}'.format(i)
#   varName = plt.figure(i,figsize=(18, 18))
#   plt.title('Estimator{}'.format(i))
#   tree.plot_tree(randomForestclf.estimators_[i],filled = True,impurity=True, rounded=True)
#   strName = 'Estimator{}.png'.format(i)
#   varName.savefig(strName)
#   varName.show()

# What are the most important features for random forest classifier?
feature_importances = randomForestclf.feature_importances_
features = X_train.columns
df = pd.DataFrame({'features': features, 'importance': feature_importances})
df = df.sort_values(by='importance', ascending=False)
print(df.iloc[0:10, :])

# Logistic Regression

# import the class
from sklearn.linear_model import LogisticRegression

# instantiate the model (using default parameters)
logReg = LogisticRegression()

# fit the model with data
logReg.fit(X_train, y_train)

# make predictions
y_pred = logReg.predict(X_test)

# evaluate the performance
from sklearn import metrics
cnf_matrix = metrics.confusion_matrix(y_test, y_pred)

print(cnf_matrix)
print('Accuracy:', metrics.accuracy_score(y_test, y_pred))

"""**TEST 3: OK NOW WE TRY AT 1/8TH OF THE MAJORITY CLASS RESAMPLING**
---


"""

# sklearn
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from yellowbrick.regressor import ResidualsPlot
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import plot_confusion_matrix
from sklearn.metrics import classification_report

# Need to convert categorical variables to dummy variables so sklearn doesn't freak out about strings
X=pd.get_dummies(df12p5.loc[:])

X = X.drop(['encounter_id','aids', 'd1_diasbp_max','patient_id','d1_diasbp_noninvasive_max', 'hospital_id','lymphoma','d1_spo2_max','cirrhosis'\
            ,'arf_apache','hepatic_failure','d1_glucose_min','height','icu_id'], axis=1)

# Create test / train split
X = X.drop(['hospital_death'], axis=1)
y = df12p5['hospital_death']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=2020)

# Find baseline Accuracy
from sklearn.dummy import DummyClassifier
dummy_classifier = DummyClassifier(strategy='most_frequent')
dummy_classifier.fit(X_train, y_train)
baseline = dummy_classifier.score(X_test, y_test)
print("Baseline Accuracy:", baseline)

# When live (majority class) is put at 1/8th, baseline accuracy is 57.29%

# DECISION TREE
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import accuracy_score
import numpy as np
from sklearn import tree

Tree = DecisionTreeClassifier(max_depth=6, criterion="gini", random_state=2020)
Tree.fit(X_train,y_train)
ypred = Tree.predict((X_test))

fn = X.columns
cn = y.unique()
plt.figure(figsize = (18, 18))
HeartDecisionTree = tree.plot_tree(Tree, class_names=['died', 'survived'], filled = True)
plt.savefig('SurvivalEigth.png')
plt.show()

# Evaluate Dtree
training_pred = Tree.predict(X_train)
acc_training = accuracy_score(training_pred, y_train)
print("Training Accuracy:", acc_training)

ypred = Tree.predict((X_test))
acc_testing = accuracy_score(ypred, y_test)
print("Testing Accuracy: ", acc_testing)

# Find most Important features for Decision tree to predict
#print("Feature Importance:", dt.feature_importances_)
importance=pd.DataFrame(zip(X_train.columns, Tree.feature_importances_))
#print(importance)
importance.nlargest(10, 1)

#Random Forest Classifier
randomForestclf = RandomForestClassifier(n_estimators=15)
randomForestclf.fit(X_train,y_train)
testPredictor = randomForestclf.predict(X_test)
trainPredictor = randomForestclf.predict(X_train)
accuracyCalculator(trainPredictor,testPredictor ,y_train , y_test)

#What are the most important features for Random Forest?
feature_importances = randomForestclf.feature_importances_
features = X_train.columns
df = pd.DataFrame({'features': features, 'importance': feature_importances})
df = df.sort_values(by='importance', ascending=False)
print(df.iloc[0:10, :])

# LOG REGRESSION

# fit the model with data
logReg.fit(X_train, y_train)

# make predictions
y_pred = logReg.predict(X_test)

# evaluate the performance
from sklearn import metrics
cnf_matrix = metrics.confusion_matrix(y_test, y_pred)

print(cnf_matrix)
print('Accuracy:', metrics.accuracy_score(y_test, y_pred))