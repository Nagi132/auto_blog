# format_output.py
import logging
import html # For escaping
import re
from bs4 import BeautifulSoup # Import BeautifulSoup

def generate_blog_html(selected_posts, topic_keyword):
    """
    Generates an HTML string representing the blog post from selected posts,
    formatted similarly to the Livedoor example (t_h, t_b divs).
    Ensures reply links (>>number) are styled blue.
    """
    if not selected_posts:
        return "<p>No posts selected for this topic.</p>"

    html_parts = []
    # Removed H1 title generation - handled by publish function

    for i, post in enumerate(selected_posts):
        post_number = post.get('number', 'N/A')
        user_info_raw = post.get('user_info', '名無しさん')
        timestamp = post.get('timestamp', '')
        post_id = post.get('id', '')
        original_content_html = post.get('content_html', '')

        # --- Consistent User Info ---
        # Replace specific anonymous name with the desired one
        if user_info_raw == "名無しさんの野望":
            user_info_display = "名無しサモナー"
        else:
            user_info_display = user_info_raw # Keep other names as is

        # --- Process Content HTML for Reply Link Styling ---
        if original_content_html:
            soup = BeautifulSoup(original_content_html, 'html.parser')
            reply_links = soup.find_all('a')
            for link in reply_links:
                # Check if link text looks like a reply link (e.g., >>123)
                link_text = link.get_text(strip=True)
                if re.match(r'^>>\d+$', link_text):
                    # Add or update style attribute
                    if link.has_attr('style'):
                        # Append color if style exists, avoid duplication
                        existing_style = link['style'].rstrip(';') # Remove trailing semicolon if any
                        if 'color:' not in existing_style:
                            link['style'] = f'{existing_style}; color: blue;'
                        # else: color already defined, maybe override or leave?
                        # Let's override for simplicity/consistency:
                        # Find existing color property and replace, or append if not found.
                        # This is complex to do perfectly with just string manipulation.
                        # Simpler: Just append, browser should handle precedence or override.
                        # link['style'] = f'{existing_style}; color: blue;' # Re-appending might be messy
                        # Safest basic approach: only add if not present.
                    else:
                        link['style'] = 'color: blue;'
            # Get the modified HTML string back from soup
            # Use prettify() or just str() - str() avoids adding extra whitespace
            processed_content_html = str(soup)
        else:
            processed_content_html = '<p><i>Content not available.</i></p>'

        # --- Separator after first post ---
        if i == 1: # Add separator *before* the second post (which is the start of the body)
             html_parts.append("<!-- Body -->") # Keep this comment for source readability
             html_parts.append("<!--more-->") # Add the Livedoor/Standard Read More marker
             # Maybe add a visual separator too?
             # html_parts.append("<hr style='border-top: 1px dashed #ccc;'>") 

        # --- Header (t_h) ---
        html_parts.append('<div class="t_h">')
        header_content = f'{post_number}: '
        # Use the display version of user_info
        header_content += f'<span style="color: green;">{html.escape(user_info_display)}</span> '
        header_content += f'<span style="color: gray;"> {html.escape(timestamp)}</span>'
        if post_id:
            header_content += f'<span style="color: gray;"> ID:{html.escape(post_id)}</span>'
        html_parts.append(header_content)
        html_parts.append('</div>')

        # --- Body (t_b) ---
        body_style = "font-weight:bold;margin-bottom:90px;"
        html_parts.append(f'<div class="t_b" style="{body_style}">')
        html_parts.append(f'  {processed_content_html}')
        html_parts.append('</div><br />')

    # Optional: Add the source link (requires original URL)
    # if config.SOURCE_URL:
    #    html_parts.append(f'<p style="color:gray;text-align:right;">引用元: <a target="_blank" href="{config.SOURCE_URL}"><span style="color: gray;">{config.SOURCE_URL}</span></a></p>')

    return "\n".join(html_parts)

# Remove the old test block for generate_blog_html as it used a different structure
# if __name__ == '__main__':
#   ... 