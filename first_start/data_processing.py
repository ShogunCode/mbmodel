from sklearn.decomposition import NMF
from sklearn.cluster import KMeans

# Pre-process the data once it has been uploaded and saved
def preprocess_data(data):
    # Perform any pre-processing 
    return data

# Dimenionality Reduction of the data using NMF
def transform_with_nmf(data, n_components=6):
    model = NMF(n_components=n_components)
    W = model.fit_transform(data)
    H = model.components_
    return W, H

# Apply KMeans clustering to the data
def apply_kmeans(H, n_clusters=7):
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(H)
    return kmeans.labels_, kmeans

