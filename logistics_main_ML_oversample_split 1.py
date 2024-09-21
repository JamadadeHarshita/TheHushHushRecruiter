import sqlite3
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import sys

# Set encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

# Function to fetch all records from the SQLite database
def fetch_all_users():
    conn = sqlite3.connect('stackoverflow_users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    all_users = c.fetchall()
    conn.close()
    return all_users

# Function to convert fetched user data to a DataFrame
def fetch_users_to_dataframe():
    users = fetch_all_users()
    columns = ['ID', 'Display Name', 'Reputation', 'Email', 'Upvotes', 'Downvotes', 'Bronze', 'Silver', 'Gold', 'ylabel']
    df = pd.DataFrame(users, columns=columns)
    return df

# Fetch users into a DataFrame
stack_users = fetch_users_to_dataframe()

# Display DataFrame info to verify data loading
print("DataFrame Info:")
print(stack_users.info())
print("\nDataFrame Head:")
print(stack_users.head())

print(stack_users['ylabel'].value_counts())

#separte data into 2 sets : 0 & 1
data_label_0 = stack_users[stack_users['ylabel']==0]
data_label_1 = stack_users[stack_users['ylabel']==1]
print("ylabel 0",data_label_0)
print("ylabel 1",data_label_1)

#splitting ylabel==1 into 5 records for test and train
train_label_1, test_label_1 = train_test_split(data_label_1, test_size=0.5, random_state=42)

#split ylabel==0 normally
train_label_0, test_label_0 = train_test_split(data_label_0, test_size=0.3, random_state=42)

# Concatenate the training and testing datasets back together
xtrain =pd.concat([train_label_0[['Reputation', 'Upvotes', 'Bronze', 'Silver', 'Gold']],
                    train_label_1[['Reputation', 'Upvotes', 'Bronze', 'Silver', 'Gold']]])

ytrain = pd.concat([train_label_0['ylabel'], train_label_1['ylabel']])

xtest = pd.concat([test_label_0[['Reputation', 'Upvotes', 'Bronze', 'Silver', 'Gold']],
                   test_label_1[['Reputation', 'Upvotes', 'Bronze', 'Silver', 'Gold']]])

ytest = pd.concat([test_label_0['ylabel'], test_label_1['ylabel']])

# Checking the splitting of data
print("xtrain:", len(xtrain), " ytrain:", len(ytrain))
print("xtest:", len(xtest), "   ytest:", len(ytest))

# Perform oversampling to balance the training set using SMOTE
smote = SMOTE(random_state=42)
xtrain_sampled, ytrain_sampled = smote.fit_resample(xtrain, ytrain)

#check the  distribution after SMOTE
print("\nAfter SMOTE:")
print(ytrain_sampled.value_counts())

#logistic regression
log_reg = LogisticRegression(max_iter=2000, solver='lbfgs')
log_reg.fit(xtrain_sampled, ytrain_sampled)

# Logistic Regression
# log_reg = LogisticRegression(max_iter=2000, solver='lbfgs')
# log_reg.fit(xtrain, ytrain)

# Prediction on test data
ypred = log_reg.predict(xtest)
ypred_proba = log_reg.predict_proba(xtest)  # Get prediction probabilities

# Confusion Matrix
print("Confusion Matrix:")
print(confusion_matrix(ytest, ypred))

# Classification Report
print("\nClassification Report:")
print(classification_report(ytest, ypred))

#Add predicted labels and probability of class 1 to the test set
xtest = xtest.copy()  # Copy the test set to prevent modifying the original data
xtest['predicted_label'] = ypred
xtest['probability_class_1'] = ypred_proba[:, 1]  # Probability of belonging to class 1

# Sort by probability to identify the best candidates
top_candidates = xtest.sort_values(by='probability_class_1', ascending=False)

# Display top candidates
print("\nTop 10 Candidates:")
print(top_candidates.head(10))

