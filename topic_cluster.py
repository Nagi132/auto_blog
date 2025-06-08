# topic_cluster.py
import logging
from sentence_transformers import SentenceTransformer # Still needed for specifying the model
from bertopic import BERTopic
import pandas as pd # BERTopic often works well with pandas DataFrames
# Remove HDBSCAN import if no longer directly used
# import hdbscan 
import numpy as np
import torch # To check for GPU

def cluster_posts_by_topic(posts_data, 
                           model_name='pkshatech/GLuCoSE-base-ja-v2', 
                           min_topic_size=6,
                           min_post_length=8):
    """
    Clusters posts into topics using BERTopic.

    Args:
        posts_data (list): List of post dictionaries from fetch_conversations.
        model_name (str): Name of the sentence-transformer model for BERTopic to use.
        min_topic_size (int): The minimum size of a topic (passed to HDBSCAN internally).
        min_post_length (int): Minimum character length for a post to be included in clustering.

    Returns:
        list: A list of clusters. Each cluster is a list of post dictionaries.
              Returns an empty list if no posts or no topics found (excluding outliers).
    """
    if not posts_data:
        logging.warning("No posts provided for BERTopic clustering.")
        return []

    # --- 1. Prepare and Filter Text Data --- 
    filtered_posts_data = []
    original_indices = []
    texts = []
    initial_count = len(posts_data)

    logging.info(f"Filtering posts shorter than {min_post_length} characters.")
    for i, post in enumerate(posts_data):
        text = post.get('content_text', '')
        if len(text) >= min_post_length:
            filtered_posts_data.append(post) # Keep the post data if using it later
            original_indices.append(i)      # Store the *original* index
            texts.append(text)             # Store the text for BERTopic
    
    filtered_count = len(texts)
    logging.info(f"Removed {initial_count - filtered_count} short posts. Clustering {filtered_count} posts.")

    if not texts:
        logging.warning("No posts remaining after filtering. Cannot perform clustering.")
        return []

    # Determine device for sentence transformer embedding
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logging.info(f"Attempting to use device: {device} for embeddings within BERTopic.")

    # --- 2. Initialize and Run BERTopic --- 
    try:
        logging.info(f"Initializing BERTopic with model: {model_name} and min_topic_size: {min_topic_size}")
        
        topic_model = BERTopic(
            embedding_model=model_name, 
            language="japanese", 
            min_topic_size=min_topic_size,
            verbose=True
        )

        logging.info("Running BERTopic fit_transform...")
        # Pass *filtered* texts to fit_transform
        topics, probs = topic_model.fit_transform(texts) 
        
        num_found_topics = len(set(topics)) - (1 if -1 in topics else 0)
        num_outliers = list(topics).count(-1)
        logging.info(f"BERTopic found {num_found_topics} topics and {num_outliers} outliers on filtered data.")

    except Exception as e:
        logging.error(f"Error during BERTopic processing: {e}", exc_info=True)
        return [] 

    if num_found_topics == 0:
        logging.warning("BERTopic found no topics (excluding outliers). Returning empty list.")
        return []

    # --- 3. Group Original Posts by Topic --- 
    clusters = {}
    # Iterate through the *results* from BERTopic (which correspond to filtered texts)
    for filtered_idx, topic_num in enumerate(topics):
        if topic_num != -1: # Ignore outliers
            # Get the index in the *original* posts_data list
            original_post_index = original_indices[filtered_idx]
            if topic_num not in clusters:
                clusters[topic_num] = []
            # Append the *original* post data using the retrieved original index
            clusters[topic_num].append(posts_data[original_post_index])

    # --- 4. Format and Sort Output --- 
    final_clusters = []
    sorted_topic_nums = sorted(clusters.keys())

    for topic_num in sorted_topic_nums:
        posts_in_cluster = clusters[topic_num]
        posts_in_cluster.sort(key=lambda p: p.get('number', 0))
        final_clusters.append(posts_in_cluster)
        logging.info(f"Topic {topic_num} contains {len(posts_in_cluster)} posts (First post: {posts_in_cluster[0].get('number', 'N/A')})")

    logging.info(f"Returning {len(final_clusters)} valid topic clusters.")
    return final_clusters

# Example placeholder 
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("topic_cluster.py run directly - BERTopic test requires data.")
    # You would need to load data/fetched_posts.json here for a real test 