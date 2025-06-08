import os
from dotenv import load_dotenv # Import load_dotenv

# Load variables from .env file
load_dotenv()

# URL for fetching (currently unused as we use local file)
# URL = "https://anago.2ch.sc/test/read.cgi/game/1742028239/0-" 

# Path to the locally saved HTML file
LOCAL_HTML_FILE = os.path.join('data', 'thread.html')

# Keyword for topic selection (used by main.py)
TOPIC_KEYWORD = "アンベッサ"
# START_POST_NUM = None # Alternative: specify a post number to start from

# Livedoor AtomPub API details (loaded from .env)
API_URL = os.getenv('LIVEDOOR_API_URL')
USERNAME = os.getenv('LIVEDOOR_USERNAME')
ATOMPUB_PASSWORD = os.getenv('LIVEDOOR_ATOMPUB_PASSWORD')

# Ensure data and logs directories exist
if not os.path.exists('data'):
    os.makedirs('data')
if not os.path.exists('logs'):
    os.makedirs('logs')

# --- Sanity Checks (Optional but Recommended) ---
if not API_URL:
    print("Warning: LIVEDOOR_API_URL not found in .env file or environment variables.")
if not USERNAME:
    print("Warning: LIVEDOOR_USERNAME not found in .env file or environment variables.")
if not ATOMPUB_PASSWORD:
    print("Warning: LIVEDOOR_ATOMPUB_PASSWORD not found in .env file or environment variables.")
