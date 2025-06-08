import requests
import logging
import xml.etree.ElementTree as ET
# config import is no longer needed here if called from main.py which imports config

def publish_to_blog(api_url, username, atompub_password, title, content):
    """Publishes content to a Livedoor blog using AtomPub."""
    headers = {
        'Content-Type': 'application/atom+xml'
    }
    
    # Register app namespace for control elements
    ET.register_namespace('app', "http://www.w3.org/2007/app")
    
    entry = ET.Element("entry", xmlns="http://www.w3.org/2005/Atom")
    
    title_element = ET.SubElement(entry, "title")
    title_element.text = title
    
    content_element = ET.SubElement(entry, "content", type="html")
    # Ensure content is properly escaped within CDATA or handled by ET
    # Using text directly might be okay if content is simple HTML, 
    # but CDATA is safer for complex/user-generated HTML.
    # content_element.text = f"<![CDATA[{content}]]>"
    content_element.text = content # Keep simple for now, Livedoor might handle it
    
    # Add app:control element for draft status
    # Need to use the namespace when creating the element tag
    control = ET.SubElement(entry, "{http://www.w3.org/2007/app}control") 
    draft = ET.SubElement(control, "{http://www.w3.org/2007/app}draft")
    draft.text = "yes" # Post as draft first
    # draft.text = "no" # Post directly (not as draft)
    
    # Convert XML Element Tree to string
    # Use xml_declaration=True for standard XML output
    entry_xml_string = ET.tostring(entry, encoding='utf-8', method='xml', xml_declaration=True).decode('utf-8')
    
    logging.info(f'Publishing to API URL: {api_url}')
    # Avoid logging password directly
    logging.info(f'Using Username: {username}') 
    logging.debug(f'XML Payload: {entry_xml_string}') # Log payload only in debug
    
    try:
        response = requests.post(
            api_url, 
            headers=headers, 
            data=entry_xml_string.encode('utf-8'), # Ensure UTF-8 encoding for the request body
            auth=(username, atompub_password),
            timeout=30 # Add a timeout
        )
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        
        logging.info(f'Response Status Code: {response.status_code}')
        logging.info(f'Response Text: {response.text[:500]}...') # Log truncated response
        print(f'Post published successfully as draft! Status: {response.status_code}')
        return True # Indicate success

    except requests.exceptions.RequestException as e:
        logging.error(f'Failed to publish post due to network error: {e}')
        print(f'Failed to publish post: {e}')
    except Exception as e:
        # Catch other potential errors like XML building issues
        logging.error(f'An unexpected error occurred during publishing: {e}')
        print(f'An unexpected error occurred: {e}')
        
    return False # Indicate failure

# Remove the old test block
# if __name__ == '__main__':
#    ...
