import config
# Remove unused clean_text, preprocess_text, summarize_text imports if they exist
# Keep publish_blog import if needed later
import logging
import os
import json
from fetch_conversations import fetch_conversations # Import the updated function
# Remove single-topic selection import
# from select_topic_posts import find_related_posts 
from topic_cluster import cluster_posts_by_topic # <--- Import the clustering function
from format_output import generate_blog_html # <--- Import the HTML generator
from publish_blog import publish_to_blog
from config import API_URL, USERNAME, ATOMPUB_PASSWORD
# Remove unused transformers import
# from transformers import pipeline 

# Ensure the logs directory exists
os.makedirs('logs', exist_ok=True)
# Ensure the data directory exists
os.makedirs('data', exist_ok=True)

logging.basicConfig(filename='logs/run.log', level=logging.INFO)

def generate_cluster_title(cluster_posts):
    """Generates a simple title based on the first post's content."""
    if not cluster_posts:
        return "まとめ" # Default title
    
    first_post_text = cluster_posts[0].get('content_text', '')
    # Take the first ~30 characters, trying to avoid partial words if possible
    # This is a very basic strategy and can be improved
    title_part = first_post_text[:30].strip()
    if len(first_post_text) > 30:
        # Try to backtrack to the last space if we cut mid-word
        last_space = title_part.rfind(' ')
        if last_space > 15: # Only backtrack if it makes sense
            title_part = title_part[:last_space]
        title_part += "..."
        
    # Return in the format "【LoL】Title here"
    return f"【LoL】{title_part}"

def main():
    # --- 1. Fetch/Parse from Local File ---
    local_html_path = config.LOCAL_HTML_FILE # Get path from config
    if not os.path.exists(local_html_path):
        logging.error(f"Local HTML file not found: {local_html_path}")
        logging.error("Please save the target 2chan thread page to this location first.")
        return

    logging.info(f"Parsing posts from local file: {local_html_path}")
    all_posts_data = fetch_conversations(local_html_path) # Use the function that reads local file

    if not all_posts_data:
        logging.error("Failed to parse any posts from the local file.")
        return

    logging.info(f"Successfully parsed {len(all_posts_data)} posts.")
    # Optional: Save the full parsed data if needed for debugging elsewhere
    # full_parsed_path = os.path.join('data', 'fetched_posts.json')
    # with open(full_parsed_path, 'w', encoding='utf-8') as f:
    #     json.dump(all_posts_data, f, ensure_ascii=False, indent=2)
    # logging.info(f"Saved all parsed posts to {full_parsed_path}")

    # --- 2. Cluster Posts into Topics ---
    logging.info("Clustering posts into topics...")
    # Call the updated function without DBSCAN parameters
    topic_clusters = cluster_posts_by_topic(all_posts_data)

    if not topic_clusters:
        logging.warning("No topic clusters identified. Exiting.")
        return

    logging.info(f"Identified {len(topic_clusters)} potential topic clusters.")

    # --- Loop Through Clusters and Process Each --- 
    for i, cluster in enumerate(topic_clusters):
        cluster_id = i + 1 # Simple 1-based ID for logging/filenames
        logging.info(f"--- Processing Cluster {cluster_id} ({len(cluster)} posts) ---")

        # --- 3a. Generate Title for Cluster ---
        # Using a helper function for title generation
        topic_title = generate_cluster_title(cluster)
        logging.info(f"Generated title: {topic_title}")

        # --- 3b. Generate Output HTML for Cluster ---
        # Pass the list of posts *for this cluster* and the generated title/keyword
        # Note: generate_blog_html uses the second arg for logging/placeholder only now
        output_html = generate_blog_html(cluster, topic_title) 

        # Save the generated HTML for review/debugging - Commented out
        # Use cluster ID in filename to avoid overwrites
        # output_html_path = os.path.join('data', f'blog_post_cluster_{cluster_id}.html')
        # try:
        #     with open(output_html_path, 'w', encoding='utf-8') as f:
        #         f.write(output_html)
        #     logging.info(f"Saved generated HTML fragment for cluster {cluster_id} to {output_html_path}")
        # except Exception as e:
        #     logging.error(f"Error saving generated HTML for cluster {cluster_id}: {e}")
        #     continue # Skip to next cluster if saving fails

        # print(f"Cluster {cluster_id}: Generated HTML for {len(cluster)} posts. Saved to {output_html_path}") # Commented out print

        # --- 4a. Publish Cluster as Draft ---
        logging.info(f"Attempting to publish blog post for cluster {cluster_id}...")
        if not config.API_URL or not config.USERNAME or not config.ATOMPUB_PASSWORD:
            logging.error("Livedoor API credentials missing. Skipping publish for cluster {cluster_id}.")
            print(f"Error: Livedoor API credentials not found. Skipping publish for cluster {cluster_id}.")
            continue # Skip to next cluster
        else:
            success = publish_to_blog(config.API_URL, config.USERNAME, config.ATOMPUB_PASSWORD, topic_title, output_html)
            if success:
                logging.info(f"Publishing successful for cluster {cluster_id}.")
            else:
                logging.error(f"Publishing failed for cluster {cluster_id}. Check logs.")
        
        # Optional: Add a small delay between posts?
        # import time
        # time.sleep(5) 

    logging.info("Main script finished processing all clusters.")


if __name__ == "__main__":
    main()
