# Auto Blog Tech Stack

This document outlines the key technologies and libraries used in the `auto_blog` project as of May 2025.

## Core Language

*   **Python 3:** The primary programming language for the entire script.

## Fetching & Parsing

*   **Manual HTML Saving:** Currently, the 2chan thread HTML is saved manually to `data/thread.html` due to difficulties bypassing anti-bot measures on the target site.
*   **BeautifulSoup4 (`beautifulsoup4`):** Used for parsing the saved HTML file (`data/thread.html`).
*   **lxml (`lxml`):** Used as the underlying parser for BeautifulSoup4, providing robustness in handling the HTML structure.
*   **Requests (`requests`):** Initially used for direct fetching attempts; also used by `publish_blog.py` for making HTTP requests to the Livedoor AtomPub API.

## Topic Identification & Clustering

*   **BERTopic (`bertopic`):** The core library used for identifying distinct topics within the parsed post content. It orchestrates embedding, dimensionality reduction, and clustering.
*   **Sentence Transformers (`sentence-transformers`):** Used by BERTopic to load the text embedding model.
    *   **Embedding Model (`pkshatech/GLuCoSE-base-ja`):** A Japanese-specific text embedding model from Hugging Face, chosen for better semantic understanding of the Japanese text compared to multilingual models.
*   **SentencePiece (`sentencepiece`):** A dependency required by the tokenizer used with the `pkshatech/GLuCoSE-base-ja` model.
*   **HDBSCAN (`hdbscan`):** Used internally by BERTopic (by default) for the density-based clustering step.
*   **UMAP (`umap-learn`):** Used internally by BERTopic (by default) for dimensionality reduction before clustering.
*   **PyTorch (`torch`):** Underlying framework used by Sentence Transformers for model execution (can utilize CPU or GPU).
*   **Scikit-learn (`scikit-learn`):** Provides various machine learning utilities, potentially used by BERTopic, HDBSCAN, or UMAP.

## Content Formatting

*   **Custom Python Logic (`format_output.py`):** Generates the final HTML for each topic cluster, mimicking the desired Livedoor blog post structure (`<div class="t_h">`, `<div class="t_b">`), adding the `<!--more-->` tag, and styling reply links.
*   **BeautifulSoup4 (`beautifulsoup4`):** Also used within `format_output.py` to parse the generated HTML snippet for finding and styling reply links.

## Publishing

*   **Livedoor AtomPub API:** The script interacts with Livedoor's Atom Publishing Protocol endpoint to create new blog posts as drafts.
*   **Custom Python Logic (`publish_blog.py`):** Constructs the necessary XML payload (using Python's `xml.etree.ElementTree`) and sends it to the Livedoor API via `requests` with Basic Authentication.

## Configuration & Environment

*   **python-dotenv (`python-dotenv`):** Used to load sensitive API credentials (Livedoor username, password, API URL) from a `.env` file, keeping them out of the source code.
*   **Virtual Environment (`.venv`):** Used to manage project dependencies and isolate them from the global Python installation.
*   **Requirements File (`requirements.txt`):** Lists all Python package dependencies for easy installation.

## Development & Debugging

*   **Logging (`logging` module):** Used throughout the scripts to record progress, warnings, and errors to `logs/run.log`.
*   **Intermediate Files (`data/` directory):** Used to store the input HTML (`thread.html`) and the generated HTML for each cluster (`blog_post_cluster_*.html`) for debugging. 