
import sqlite3
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

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
    columns = ['ID', 'Display Name', 'Reputation', 'Email', 'Upvotes', 'Downvotes', 'Bronze', 'Silver', 'Gold','ylabel']
    df = pd.DataFrame(users, columns=columns)
    return df

def add_ylabel_column():
    conn = sqlite3.connect('stackoverflow_users.db')
    c = conn.cursor()

    # Add 'ylabel' column if it doesn't already exist
    try:
        c.execute("ALTER TABLE users ADD COLUMN ylabel INTEGER;")
    except sqlite3.OperationalError:
        # If the column already exists, skip the operation
        print("The 'ylabel' column already exists in the database.")

    conn.commit()
    conn.close()
    

add_ylabel_column()

# Fetch users into a DataFrame
stack_users = fetch_users_to_dataframe()

# Inspect the DataFrame
print("DataFrame Info:")
print(stack_users.info())
print("\nDataFrame Head:")
print(stack_users.head())

print(stack_users.isna().sum()) # check null values
print("duplicates: ",stack_users.duplicated().sum())

#Correlation via Heatmap
# numeric_columns = stack_users.select_dtypes(['int','float'])
# plt.figure(figsize=(10,8))
# sns.heatmap(numeric_columns.corr(),annot=True,cmap='coolwarm')
# plt.show()

x=stack_users[['Reputation','Upvotes','Bronze','Silver','Gold']]
from sklearn.preprocessing import StandardScaler #set similar Units places of all features 
sc=StandardScaler()
x_scaled=sc.fit_transform(x)
print(x_scaled)

#identifying the optimal no.of clusters using ELBOW Method
from sklearn.cluster import KMeans
wcss=[]
for i in range(1,11):
    kmeans = KMeans(n_clusters=i)
    kmeans.fit_predict(x_scaled)
    wcss.append(kmeans.inertia_)
print(wcss)

# plt.plot(range(1,11),wcss,'o--')
# plt.xlabel('No of clusters')
# plt.ylabel('WCSS')
# plt.title('Elbow Method for Optimal Number of Clusters')
# plt.grid()
# plt.show()

kmeans = KMeans(n_clusters=3,random_state=42)
ylabel = kmeans.fit_predict(x_scaled)
stack_users['ylabel']=ylabel
print(stack_users)
print(stack_users['ylabel'].value_counts())

# Save the updated DataFrame back to the database
conn = sqlite3.connect('stackoverflow_users.db')
stack_users.to_sql('users', conn, if_exists='replace', index=False)
conn.close()

#using Dimensionality Reduction for clustering using PCA
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

x=stack_users[['Reputation','Upvotes','Bronze','Silver','Gold']]
print(x)

pca = PCA(n_components=3)
x_pca = pca.fit_transform(x)
print(x_pca)

pca_df = pd.DataFrame(data=x_pca, columns=['PCA1', 'PCA2','PCA3'])
pca_df['Cluster'] = ylabel
print(pca_df)

plt.figure(figsize=(10, 8))
plt.scatter(pca_df[pca_df['Cluster'] == 0]['PCA1'], pca_df[pca_df['Cluster'] == 0]['PCA2'], s=100, c='blue', label='Cluster 0')
plt.scatter(pca_df[pca_df['Cluster'] == 1]['PCA1'], pca_df[pca_df['Cluster'] == 1]['PCA2'],s=100, c='red', label='Cluster 1')
plt.scatter(pca_df[pca_df['Cluster'] == 2]['PCA1'], pca_df[pca_df['Cluster'] == 2]['PCA2'],s=100, c='yellow', label='Cluster 2')

plt.title('Clusters Visualization using PCA')
plt.xlabel('PCA1')
plt.ylabel('PCA2')
plt.legend()
plt.show()

# Summary statistics for each cluster
cluster_0_stats = stack_users[stack_users['ylabel'] == 0].describe()
cluster_1_stats = stack_users[stack_users['ylabel'] == 1].describe()
cluster_2_stats = stack_users[stack_users['ylabel'] == 2].describe()

print("Cluster 0 Stats:\n", cluster_0_stats)
print("Cluster 1 Stats:\n", cluster_1_stats)
print("Cluster 2 Stats:\n", cluster_2_stats)

print("--------------------------------------")

numeric_columns = stack_users.select_dtypes(include='number')

# Compute mean values for each cluster based on numeric columns
cluster_0_means = numeric_columns[stack_users['ylabel'] == 0].mean()
cluster_1_means = numeric_columns[stack_users['ylabel'] == 1].mean()
cluster_2_means = numeric_columns[stack_users['ylabel'] == 2].mean()

print("Cluster 0 Means:\n", cluster_0_means)
print("Cluster 1 Means:\n", cluster_1_means)
print("Cluster 1 Means:\n", cluster_2_means)

print("TOP CANDIDATES")
top_candidates = stack_users[stack_users['ylabel'] == 1]
top_candidates = top_candidates.sort_values(by='Reputation', ascending=False)

top_5_candidates = top_candidates.head(5)
print("Top 5 Candidates:\n", top_5_candidates[['ID','Display Name', 'Reputation', 'Upvotes', 'Bronze', 'Silver', 'Gold','Email','ylabel']])



 