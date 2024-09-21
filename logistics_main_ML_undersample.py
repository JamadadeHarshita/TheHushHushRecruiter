# # import sqlite3
# # import pandas as pd
# # from sklearn.model_selection import train_test_split
# # from sklearn.linear_model import LogisticRegression
# # from sklearn.metrics import classification_report, confusion_matrix
# # from sklearn.utils import resample
# # import sys

# # # Set encoding for stdout
# # sys.stdout.reconfigure(encoding='utf-8')

# # # Function to fetch all records from the SQLite database
# # def fetch_all_users():
# #     conn = sqlite3.connect('stackoverflow_users.db')
# #     c = conn.cursor()
# #     c.execute('SELECT * FROM users')
# #     all_users = c.fetchall()
# #     conn.close()
# #     return all_users

# # # Function to convert fetched user data to a DataFrame
# # def fetch_users_to_dataframe():
# #     users = fetch_all_users()
# #     columns = ['ID', 'Display Name', 'Reputation', 'Email', 'Upvotes', 'Downvotes', 'Bronze', 'Silver', 'Gold', 'ylabel']
# #     df = pd.DataFrame(users, columns=columns)
# #     return df

# # # Fetch users into a DataFrame
# # stack_users = fetch_users_to_dataframe()

# # # Display DataFrame info to verify data loading
# # print("DataFrame Info:")
# # print(stack_users.info())
# # print("\nDataFrame Head:")
# # print(stack_users.head())

# # print("\nDistribution of data before Undersampling:")
# # print(stack_users['ylabel'].value_counts())

# # #separate the data into 2 sets, ylabel == 0 and ylabel == 1
# # data_label_0 = stack_users[stack_users['ylabel'] == 0]
# # data_label_1 = stack_users[stack_users['ylabel'] == 1]

# # print("Number of ylabel == 0:", len(data_label_0))
# # print("Number of ylabel == 1:", len(data_label_1))

# # #Undersample 0 to match the number of 1
# # data_label_0_undersampled = resample(data_label_0, replace=False, n_samples=len(data_label_1), random_state=42)

# # #combineing the undersampled 0 data with the 1 data
# # undersampled_data = pd.concat([data_label_0_undersampled, data_label_1])

# # print("\nDistribution of data after Undersampling:")
# # print(undersampled_data['ylabel'].value_counts())

# # #splitting the data
# # x = undersampled_data[['Reputation', 'Upvotes', 'Bronze', 'Silver', 'Gold']]
# # y = undersampled_data['ylabel']

# # # Verify the size of the combined data
# # print("\nTotal samples after undersampling:", len(x))

# # # Split the undersampled data into training and test sets
# # xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.3, random_state=42)

# # #verifying the lenth of test and train 
# # print("xtrain size:", len(xtrain))
# # print("xtest size:", len(xtest))    
# # print("ytrain size:", len(ytrain))  
# # print("ytest size:", len(ytest))    

# # #checking the distribution of data in test sets.
# # print("\nClass Distribution in Training Set:")
# # print(ytrain.value_counts())
# # print("Class Distribution in Test Set:")
# # print(ytest.value_counts())

# # log_reg = LogisticRegression(max_iter=2000, solver='lbfgs')
# # log_reg.fit(xtrain, ytrain)

# # #prediction on testing data
# # ypred = log_reg.predict(xtest)
# # ypred_proba = log_reg.predict_proba(xtest)  # Get prediction probabilities

# # # Confusion Matrix
# # print("Confusion Matrix:")
# # print(confusion_matrix(ytest, ypred))

# # # Classification Report
# # print("\nClassification Report:")
# # print(classification_report(ytest, ypred))

# # # Add predicted labels and probability of class 1 to the test set
# # xtest = xtest.copy()  # Copy the test set to prevent modifying the original data
# # xtest['predicted_label'] = ypred
# # xtest['probability_class_1'] = ypred_proba[:, 1]  # Probability of belonging to class 1

# # # Sort by probability to identify the best candidates
# # top_candidates = xtest.sort_values(by='probability_class_1', ascending=False)

# # # Display top candidates
# # print("\nTop 5 Candidates:")
# # print(top_candidates.head(5))

# import sqlite3
# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import classification_report, confusion_matrix
# from sklearn.utils import resample
# import sys
# # from store_selected_candidates import store_top_candidates_to_db
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

# # Fetch users into a DataFrame
# stack_users = fetch_users_to_dataframe()

# # Display DataFrame info to verify data loading
# print("DataFrame Info:")
# print(stack_users.info())
# print("\nDataFrame Head:")
# print(stack_users.head())

# print("\nDistribution of data before Undersampling:")
# print(stack_users['ylabel'].value_counts())

# # Separate the data into 2 sets, ylabel == 0 and ylabel == 1
# data_label_0 = stack_users[stack_users['ylabel'] == 0]
# data_label_1 = stack_users[stack_users['ylabel'] == 1]

# # Undersample 0 to match the number of 1
# data_label_0_undersampled = resample(data_label_0, replace=False, n_samples=len(data_label_1), random_state=42)

# # Combine the undersampled 0 data with the 1 data
# undersampled_data = pd.concat([data_label_0_undersampled, data_label_1])

# print("\nDistribution of data after Undersampling:")
# print(undersampled_data['ylabel'].value_counts())

# # Splitting the data
# x = undersampled_data[['Reputation', 'Upvotes', 'Bronze', 'Silver', 'Gold']]
# y = undersampled_data['ylabel']

# # Verify the size of the combined data
# print("\nTotal samples after undersampling:", len(x))

# # Split the undersampled data into training and test sets
# xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.3, random_state=42)

# # Verify the length of test and train
# print("xtrain size:", len(xtrain))
# print("xtest size:", len(xtest))
# print("ytrain size:", len(ytrain))
# print("ytest size:", len(ytest))

# # Checking the distribution of data in test sets
# print("\nClass Distribution in Training Set:")
# print(ytrain.value_counts())
# print("Class Distribution in Test Set:")
# print(ytest.value_counts())

# log_reg = LogisticRegression(max_iter=2000, solver='lbfgs')
# log_reg.fit(xtrain, ytrain)

# # Prediction on testing data
# ypred = log_reg.predict(xtest)
# ypred_proba = log_reg.predict_proba(xtest)  # Get prediction probabilities

# # Save the model to a pkl file
# with open('logreg_model.pkl', 'wb') as model_file:
#     pickle.dump(log_reg, model_file)

# # Confusion Matrix
# print("Confusion Matrix:")
# print(confusion_matrix(ytest, ypred))

# # Classification Report
# print("\nClassification Report:")
# print(classification_report(ytest, ypred))

# # Add predicted labels and probability of class 1 to the test set
# xtest = xtest.copy()  # Copy the test set to prevent modifying the original data
# xtest['predicted_label'] = ypred
# xtest['probability_class_1'] = ypred_proba[:, 1]  # Probability of belonging to class 1

# # Sort by probability to identify the best candidates
# top_candidates = xtest.sort_values(by='probability_class_1', ascending=False)

# # Display top candidates
# print("\nTop 5 Candidates:")
# print(top_candidates.head(5))

