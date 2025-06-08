import re
import logging
import time
import os
from bs4 import BeautifulSoup
# Remove Playwright imports

# --- Helper Function for User ID and Info Cleanup ---
def clean_user_info(user_info):
    """Removes parenthesized info and standardizes anonymous names."""
    if user_info is None:
        user_info = "Unknown"
    # Remove patterns like (ﾜｯﾁｮｲ ...)
    user_info = re.sub(r'\s*\(.*\)', '', user_info).strip()
    # Standardize anonymous names
    user_info = user_info.replace("名無しさんの野望", "名無しサモナー")
    # Add other potential anonymous names if needed
    # user_info = user_info.replace("other anonymous name", "名無しサモナー")
    return user_info

def clean_user_id(user_id):
    """Removes redundant ID: prefix using regex and adds logging."""
    if user_id is None:
        user_id = "Unknown"
    
    original_id_for_log = user_id # Store for logging
    logging.debug(f"Cleaning User ID. Initial value: '{original_id_for_log}'")
    
    # Initial cleanup of potential whitespace/nbsp
    user_id = user_id.replace('\xa0', ' ').strip()

    # Use regex to remove the first "ID:" if preceded by optional space and followed by another "ID:" (with optional space)
    # ^\s* asserts optional space at start of string
    # count=1 ensures only the first match is replaced
    cleaned_user_id = re.sub(r'^\s*ID:\s*ID:', 'ID:', user_id, count=1)
    
    if cleaned_user_id != user_id:
        logging.debug(f"Cleaned redundant ID prefix. Result: '{cleaned_user_id}'")
    else:
        logging.debug(f"No redundant ID prefix found or regex didn't match. ID remains: '{user_id}'")
        
    user_id = cleaned_user_id # Update user_id with the result of re.sub

    # Ensure it still starts with ID: after potential cleaning, if not Unknown
    if user_id != "Unknown" and not user_id.startswith("ID:"):
         logging.debug(f"User ID '{user_id}' lost its prefix during cleaning, prepending ID: back if non-empty")
         if user_id: 
              user_id = "ID:" + user_id
         else: 
              user_id = "Unknown"

    return user_id

# --- Parsing Logic for Structure 1: div.post ---
def parse_structure1(post_div):
    """Parses post data from a <div class='post'> structure."""
    header_div = post_div.find('div', class_='post-header', recursive=False)
    content_div = post_div.find('div', class_='post-content', recursive=False)

    if not header_div or not content_div:
        logging.warning(f"Structure 1: Skipping post {post_div.get('id', 'No ID')} - Missing header or content div.")
        return None

    # Extract basic info
    number_span = header_div.find('span', class_='postid')
    number = int(number_span.get_text(strip=True)) if number_span else None

    uid_span = header_div.find('span', class_='uid')
    user_id = uid_span.get_text(strip=True) if uid_span else "Unknown"

    user_info_span = header_div.find('span', class_='postusername')
    user_info = user_info_span.get_text(strip=True) if user_info_span else "Unknown"

    date_span = header_div.find('span', class_='date')
    timestamp = date_span.get_text(strip=True) if date_span else "Unknown"

    content_html = content_div.decode_contents()
    content_text = content_div.get_text(strip=True)

    if number is None:
        logging.error(f"Structure 1: Failed to extract number from post ID {post_div.get('id', 'N/A')}")
        # Decide if we want to keep posts without numbers - currently skipping
        return None

    # Clean and Standardize
    user_info = clean_user_info(user_info)
    user_id = clean_user_id(user_id)

    replies_to = [int(match) for match in re.findall(r'>>(\d+)', content_text)]

    return {
        'number': number,
        'user_info': user_info,
        'timestamp': timestamp,
        'id': user_id,
        'content_html': content_html.strip(),
        'content_text': content_text,
        'replies_to': replies_to
    }

# --- Parsing Logic for Structure 2: div.t_h / div.t_b ---
def parse_structure2(header_div, content_div):
    """Parses post data from a <div class='t_h'> / <div class='t_b'> structure."""
    number = None
    user_info = "Unknown"
    timestamp = "Unknown"
    user_id = "Unknown"

    # Parse header (t_h)
    header_text = header_div.get_text(separator=" ", strip=True).replace('\xa0', ' ')
    match_num = re.match(r"^(\d+)\s*:?", header_text)
    if match_num:
        number = int(match_num.group(1))
    else:
        logging.warning(f"Structure 2: Could not extract post number from start of: {header_text[:50]}")

    if number is None:
        # Potentially add fallback to find number span if needed?
        logging.error(f"Structure 2: Failed to find number in header: {header_text[:100]}")
        return None # Cannot proceed without number

    # Find spans for other details (this part is heuristic due to variations)
    spans = header_div.find_all('span')
    if len(spans) >= 1:
        # Assume first span is user info unless it looks like date/ID
        potential_user_span = spans[0]
        potential_user_text = potential_user_span.get_text(strip=True)
        if not re.search(r'\d{4}/', potential_user_text) and "ID:" not in potential_user_text:
             user_info = potential_user_text

    # Find timestamp and ID - often the last two spans or identified by content
    for span in reversed(spans):
        span_text = span.get_text(strip=True).replace('\xa0', ' ').strip()
        if span_text.startswith("ID:"):
            user_id = span_text # Assign full string first
            # Check preceding text/span for timestamp
            prev_node = span.find_previous() # Find previous node (could be tag or text)
            prev_text = prev_node.get_text(strip=True) if prev_node and hasattr(prev_node, 'get_text') else ""
            if re.search(r'\d{4}/', prev_text):
                 timestamp = prev_text.strip()

            # Fallback: Check span before ID span if previous text node didn't work
            elif len(spans) > 1:
                 try:
                     ts_text = spans[spans.index(span) - 1].get_text(strip=True)
                     if re.search(r'\d{4}/', ts_text):
                          timestamp = ts_text
                 except IndexError:
                      pass # No preceding span
            break # Found ID span

    # Fallback timestamp search across all spans if needed
    if timestamp == "Unknown":
         for span in spans:
              span_text = span.get_text(strip=True)
              # More flexible regex for timestamp
              match_ts = re.search(r'(\d{4}/\d{2}/\d{2}\(.*?\)\s*\d{2}:\d{2}:\d{2}(?:\.\d+)?)', span_text)
              if match_ts:
                   timestamp = match_ts.group(1)
                   break

    # Fallback search in full text if spans failed (less reliable)
    if user_id == "Unknown":
        match_id = re.search(r'(ID:\s?\S+)', header_text)
        if match_id: user_id = match_id.group(1)
    if timestamp == "Unknown":
         match_ts = re.search(r'(\d{4}/\d{2}/\d{2}\(.*?\)\s*\d{2}:\d{2}:\d{2}(?:\.\d+)?)', header_text)
         if match_ts: timestamp = match_ts.group(1)


    # Parse content (t_b)
    content_html = content_div.decode_contents()
    content_text = content_div.get_text(strip=True)

    # Clean and Standardize
    user_info = clean_user_info(user_info)
    user_id = clean_user_id(user_id) # Apply the fix here too!

    replies_to = [int(match) for match in re.findall(r'>>(\d+)', content_text)]

    return {
        'number': number,
        'user_info': user_info,
        'timestamp': timestamp,
        'id': user_id,
        'content_html': content_html.strip(),
        'content_text': content_text,
        'replies_to': replies_to
    }


# --- Main Fetching Function ---
def fetch_conversations(file_path):
    """Parses conversation data from a locally saved HTML file with potentially mixed structures."""
    posts_data = []
    html_content = None
    logging.info(f"Attempting to read and parse HTML from {file_path}...")

    # Read HTML content
    try:
        encodings_to_try = ['utf-8', 'cp932', 'euc-jp']
        for enc in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    html_content = f.read()
                logging.info(f"Successfully read file {file_path} using encoding {enc}")
                break
            except UnicodeDecodeError:
                logging.warning(f"Failed to decode {file_path} with {enc}, trying next...")
            except FileNotFoundError:
                logging.error(f"File not found: {file_path}")
                return []
        if html_content is None:
             logging.error(f"Could not decode file {file_path} with attempted encodings: {encodings_to_try}")
             return []
    except Exception as e:
        logging.error(f"An error occurred reading file {file_path}: {e}", exc_info=True)
        return []

    # --- Modified Parsing Logic ---
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        thread_container = soup.find('div', id='threadcontent')

        if not thread_container:
            logging.error(f"Could not find <div id='threadcontent'> in local file {file_path}")
            return []

        logging.info("Scanning thread content for post structures...")
        processed_elements = set() # Keep track of processed elements to avoid double counting

        # Find potential starting elements for both structures
        potential_posts = thread_container.find_all('div', recursive=False, limit=2500) # Limit to avoid excessive memory on huge files
        if not potential_posts:
             potential_posts = thread_container.find_all('div', recursive=True, limit=2500) # Fallback to recursive if no direct children work
             logging.warning("No direct div children found in threadcontainer, searching recursively.")

        logging.info(f"Found {len(potential_posts)} potential post start elements to check.")

        for element in potential_posts:
            # Skip already processed elements (e.g., a t_b processed via its preceding t_h)
            if element in processed_elements:
                continue

            post_info = None

            # Check for Structure 1: <div class="post">
            if 'post' in element.get('class', []):
                logging.debug(f"Processing element {element.get('id', 'No ID')} as Structure 1")
                post_info = parse_structure1(element)
                processed_elements.add(element)

            # Check for Structure 2: <div class="t_h">
            elif 't_h' in element.get('class', []):
                logging.debug(f"Processing element {element.get_text(strip=True)[:30]} as Structure 2 Header")
                # Find the next sibling that is t_b, skipping over non-element nodes or <br> etc.
                content_div = None
                next_sibling = element.next_sibling
                while next_sibling:
                     # Check if it's an element before accessing name/class
                    if hasattr(next_sibling, 'name') and next_sibling.name == 'div' and 't_b' in next_sibling.get('class', []):
                        content_div = next_sibling
                        break
                    elif hasattr(next_sibling, 'name') and next_sibling.name == 'br': # Skip <br> tags often between t_h and t_b
                         pass
                    elif isinstance(next_sibling, str) and next_sibling.strip() == "": # Skip whitespace nodes
                         pass
                    elif hasattr(next_sibling, 'name'): # If it's another tag, stop looking for t_b for this t_h
                         break

                    next_sibling = next_sibling.next_sibling # Move to the next element

                if content_div:
                    post_info = parse_structure2(element, content_div)
                    processed_elements.add(element)
                    processed_elements.add(content_div) # Mark content div as processed too
                else:
                    logging.warning(f"Structure 2: Found t_h but no matching t_b sibling for: {element.prettify()[:100]}")
                    processed_elements.add(element) # Mark header as processed even if no content found

            # Append valid parsed data
            if post_info:
                posts_data.append(post_info)

    except Exception as e:
        logging.error(f"Error parsing HTML content from {file_path}: {e}", exc_info=True)
        # Return partially parsed data? Or empty list? Returning empty for now.
        return []

    # --- Final Sorting and Deduplication ---
    # Sort final list by post number
    posts_data.sort(key=lambda p: p.get('number', float('inf'))) # Ensure posts with no number sort last

    # Remove duplicates (e.g., if parsing logic accidentally double-counts or structures overlap weirdly)
    final_posts = []
    seen_numbers = set()
    skipped_count = 0
    for post in posts_data:
        num = post.get('number')
        if num is not None and num not in seen_numbers:
            final_posts.append(post)
            seen_numbers.add(num)
        elif num is None: # Keep posts even if number couldn't be parsed? Maybe log warning.
             logging.warning(f"Including post with missing number in final list: {post.get('content_text', '')[:50]}")
             final_posts.append(post) # Keep posts even without number for now
        else:
             logging.debug(f"Skipping duplicate post number: {num}")
             skipped_count += 1

    if skipped_count > 0:
        logging.warning(f"Removed {skipped_count} duplicate posts based on post number.")

    logging.info(f"Successfully parsed {len(final_posts)} unique posts from {file_path}")
    return final_posts

# Removed the __main__ block as it's for testing only