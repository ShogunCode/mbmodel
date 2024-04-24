import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from io import BytesIO
import base64

def cluster_sample_count(cluster_labels):
    sample_counts = np.bincount(cluster_labels)

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    clusters = np.arange(1, len(sample_counts) + 1)
    plt.bar(clusters, sample_counts, color='skyblue')

    # Add labels and title
    plt.xlabel('Cluster Number')
    plt.ylabel('Number of Samples')
    plt.title('Number of Samples in Each Cluster')
    plt.xticks(clusters)

    # Save the plot to a BytesIO buffer instead of showing it directly
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()  # Close the plot to free up memory
    buf.seek(0)  # Go to the beginning of the BytesIO buffer

    # Encode the image in base64 to embed in HTML
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()  # Close the buffer to clean up

    return image_base64
