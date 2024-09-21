# import sqlite3
# import pandas as pd
# from imblearn.over_sampling import SMOTE
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
# from sklearn.preprocessing import StandardScaler
# import sys
# import pickle

# # Set encoding for stdout
# sys.stdout.reconfigure(encoding='utf-8')

# # Function to fetch all records from the SQLite database
# def fetch_all_users():
#     conn = sqlite3.connect('stackoverflow_users.db')
#     c = conn.cursor()
#     c.execute('SELECT * FROM users')
#     all_users = c.fetchall()
#     conn.close()
#     return all_users

# # Function to convert fetched user data to a DataFrame
# def fetch_users_to_dataframe():
#     users = fetch_all_users()
#     columns = ['ID', 'Display Name', 'Reputation', 'Email', 'Upvotes', 'Downvotes', 'Bronze', 'Silver', 'Gold', 'ylabel']
#     df = pd.DataFrame(users, columns=columns)
#     return df

# # Load and prepare data
# stack_users = fetch_users_to_dataframe()

# # Separate data by class
# data_label_0 = stack_users[stack_users['ylabel'] == 0]
# data_label_1 = stack_users[stack_users['ylabel'] == 1]

# # Split the data into training and testing
# train_label_1, test_label_1 = train_test_split(data_label_1, test_size=0.5, random_state=42)
# train_label_0, test_label_0 = train_test_split(data_label_0, test_size=0.3, random_state=42)

# # Combine the training and testing datasets
# xtrain = pd.concat([train_label_0[['Reputation', 'Upvotes', 'Bronze', 'Silver', 'Gold']],
#                     train_label_1[['Reputation', 'Upvotes', 'Bronze', 'Silver', 'Gold']]])
# ytrain = pd.concat([train_label_0['ylabel'], train_label_1['ylabel']])
# xtest = pd.concat([test_label_0[['Reputation', 'Upvotes', 'Bronze', 'Silver', 'Gold']],
#                    test_label_1[['Reputation', 'Upvotes', 'Bronze', 'Silver', 'Gold']]])
# ytest = pd.concat([test_label_0['ylabel'], test_label_1['ylabel']])

# # Standardize the data
# scaler = StandardScaler()

# xtrain_scaled = scaler.fit_transform(xtrain)  # Fit on training data
# xtest_scaled = scaler.transform(xtest)        # Apply the same transformation to the test data


# # Check class distribution before SMOTE
# print("Class distribution before SMOTE:")
# print(ytrain.value_counts())

# # Apply SMOTE to the training set
# smote = SMOTE(random_state=42)
# xtrain_sampled, ytrain_sampled = smote.fit_resample(xtrain, ytrain)

# # Check class distribution after SMOTE
# print("\nClass distribution after SMOTE:")
# print(pd.Series(ytrain_sampled).value_counts())

# # Train the model
# log_reg = LogisticRegression(max_iter=2000, solver='lbfgs')
# log_reg.fit(xtrain_sampled, ytrain_sampled)

# # Predict on the original test data
# ypred = log_reg.predict(xtest)
# ypred_proba = log_reg.predict_proba(xtest)

# with open('logreg_models.pkl','wb') as model_file:
#     pickle.dump(log_reg, model_file)

# # xpred = log_reg.predict(xtrain_sampled)
# # print("xpred",xpred)

# # ac_xpred = accuracy_score(ytrain_sampled,xpred)
# # print("ac_xpred",ac_xpred)

# # Evaluate the model
# print("\nConfusion Matrix:")
# print(confusion_matrix(ytest, ypred))

# print("\nClassification Report:")
# print(classification_report(ytest, ypred))

# # Add predicted labels and probability of class 1 to the test set
# xtest = xtest.copy()  # Copy the test set to prevent modifying the original data
# xtest['predicted_label'] = ypred
# xtest['probability_class_1'] = ypred_proba[:, 1]  # Probability of belonging to class 1

# # Sort by probability to identify the best candidates
# top_candidates = xtest.sort_values(by='probability_class_1', ascending=False)

# # Display top candidates
# print("\nTop 10 Candidates:")
# print(top_candidates.head(10))