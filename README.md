# Auto Blog from 2chan Thread

This Python script automates the process of fetching posts from a saved 2chan thread HTML file, identifying distinct discussion topics using AI (BERTopic and sentence embeddings), formatting the posts for each topic, and publishing them as separate draft posts to a Livedoor blog via the AtomPub API.

## Features

*   Parses locally saved 2chan HTML (`Shift_JIS`/`cp932` encoding supported).
*   Uses BERTopic with a Japanese sentence transformer model (`pkshatech/GLuCoSE-base-ja`) to cluster posts by topic.
*   Formats posts for each topic into Livedoor-style HTML, including a `<!--more-->` tag after the first post.
*   Generates a simple title for each topic like `【LoL】Topic summary...`.
*   Publishes each identified topic as a separate **draft** post to a configured Livedoor blog using the AtomPub API.

## Tech Stack

See [TECH_STACK.md](TECH_STACK.md) for a detailed list of libraries and technologies used.

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd auto_blog
    ```
2.  **Create Python Virtual Environment:**
    ```bash
    python -m venv .venv
    ```
3.  **Activate Virtual Environment:**
    *   Windows (Command Prompt/PowerShell):
        ```cmd
        .venv\Scripts\activate
        ```
    *   macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```
4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Create Configuration File (`.env`):**
    Create a file named `.env` in the root directory of the project and add your Livedoor AtomPub API credentials:
    ```dotenv
    LIVEDOOR_API_URL="https://livedoor.blogcms.jp/atompub/YOUR_BLOG_ID/article"
    LIVEDOOR_USERNAME="your_livedoor_id"
    LIVEDOOR_ATOMPUB_PASSWORD="your_atompub_api_key"
    # Optional: Override default local HTML file path
    # LOCAL_HTML_FILE="data/my_thread.html"
    ```
    *   Replace `YOUR_BLOG_ID` with your specific Livedoor blog ID.
    *   Replace `your_livedoor_id` with your Livedoor login username.
    *   Replace `your_atompub_api_key` with the AtomPub API key obtained from your Livedoor blog settings.
    *   You can find/generate the AtomPub API key in your Livedoor blog's settings, usually under "設定" -> "投稿設定" -> "AtomPub".

## Usage

1.  **Save Target HTML:** Manually save the full HTML source of the 2chan thread you want to process into the `data/` directory. By default, the script looks for `data/thread.html`. You can change this path in `config.py` or by setting `LOCAL_HTML_FILE` in your `.env` file.
2.  **Activate Virtual Environment (if not already active):**
    ```cmd
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    # source .venv/bin/activate
    ```
3.  **Run the Script:**
    ```bash
    python main.py 
    ```
4.  **Check Livedoor Drafts:** The script will parse the HTML, run topic clustering, and attempt to publish each identified topic cluster as a separate draft post on your Livedoor blog. Check your blog's draft section.
5.  **Review and Publish:** Open the generated drafts in the Livedoor editor. 
    *   Add a suitable thumbnail.
    *   The content will have a `<!--more-->` tag after the first post. You may need to manually cut the content *after* this tag and paste it into the "続きを読む" (Read More) section of the Livedoor editor, as AtomPub might not automatically split it.
    *   Review the content and title.
    *   Manually publish the post from the Livedoor interface.

## Customization

*   **Topic Clustering:** The BERTopic parameters (e.g., `min_topic_size`) can be adjusted in `topic_cluster.py`.
*   **HTML Formatting:** Styles and structure can be modified in `format_output.py`.
*   **Title Generation:** The logic for generating titles is in the `generate_cluster_title` function in `main.py`. 