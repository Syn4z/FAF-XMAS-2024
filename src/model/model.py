import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse import hstack


df = pd.read_csv("../data/santas_logistics.csv")

# Fill NaN values for text columns with empty strings
df['Good_Deed'] = df['Good_Deed'].fillna('')
df['Bad_Deed'] = df['Bad_Deed'].fillna('')

# Vectorize Good_Deed and Bad_Deed columns
vectorizer = TfidfVectorizer(stop_words='english')
good_deeds_vectors = vectorizer.fit_transform(df['Good_Deed'])
bad_deeds_vectors = vectorizer.fit_transform(df['Bad_Deed'])

# Combine numerical features with vectorized text features
numerical_features = df[['School_Grades', 'Listened_To_Parents']].fillna(0)
scaler = MinMaxScaler()
numerical_features_scaled = scaler.fit_transform(numerical_features)

all_features = hstack([good_deeds_vectors, bad_deeds_vectors, numerical_features_scaled])

# Perform clustering (e.g., KMeans with 3 clusters)
kmeans = KMeans(n_clusters=3, random_state=42)
df['Cluster'] = kmeans.fit_predict(all_features)

# Analyze clusters and calculate Goodness_Score
cluster_stats = df.groupby('Cluster').agg({
    'School_Grades': 'mean',
    'Listened_To_Parents': 'mean',
    'Good_Deed': 'count',
    'Bad_Deed': 'count'
}).reset_index()

# Custom Goodness Score formula (adjust weights as needed)
cluster_stats['Goodness_Score'] = (
    cluster_stats['School_Grades'] * 0.5 +  # Weight for grades
    cluster_stats['Listened_To_Parents'] * 0.3 +  # Weight for listening to parents
    cluster_stats['Good_Deed'] -  # Positive influence
    cluster_stats['Bad_Deed']  # Negative influence
)

# Rank clusters based on the goodness score
cluster_stats = cluster_stats.sort_values('Goodness_Score', ascending=False)
cluster_rank = {cluster: rank for rank, cluster in enumerate(cluster_stats['Cluster'], start=1)}

# Map rankings back to the original dataframe
df['Goodness_Rank'] = df['Cluster'].map(cluster_rank)

# Display results
# Save only the required columns to a new CSV
df[['Child_ID', 'Name', 'Goodness_Rank']].to_csv("kids_sorted_ranks.csv", index=False)

print("Results saved to 'kids_sorted_ranks.csv'.")
