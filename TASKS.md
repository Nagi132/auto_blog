# TASKS for Auto Blog Project

## Goal
Automate processing posts from a locally saved 2chan thread HTML file, identifying distinct discussion topics using AI, formatting them for Livedoor, and publishing them as separate drafts to the "ポロ速報-LOLまとめ" blog.

## Current Status (May 2025)
- **Fetching:** Manual HTML save to `data/thread.html` is required.
- **Parsing:** Script correctly parses the local HTML using BeautifulSoup4/lxml, handling `cp932` encoding.
- **Topic Clustering:** Uses BERTopic with the `pkshatech/GLuCoSE-base-ja` model and `min_topic_size=4`. Successfully identifies multiple topic clusters from the full thread.
- **Formatting:** Generates Livedoor-style HTML (`t_h`/`t_b` divs) for each cluster, includes `<!--more-->` tag, and styles reply links.
- **Title Generation:** Creates titles in the format `【LoL】Topic Summary...`.
- **Publishing:** Successfully publishes each topic cluster as a separate draft to Livedoor via AtomPub.
- **Documentation:** `README.md` and `TECH_STACK.md` created. `.gitignore` added.

## Chosen Approach
- **Input:** Manually saved 2chan thread HTML file.
- **Core Logic:** Python script using a virtual environment (`.venv`).
- **Topic Identification:** BERTopic library with a Japanese sentence transformer model (`pkshatech/GLuCoSE-base-ja`) and HDBSCAN clustering (via BERTopic default).
- **Output Formatting:** Custom Python logic (`format_output.py`).
- **Publishing:** AtomPub API via `requests` library, creating drafts.
- **Configuration:** Livedoor credentials managed via `.env` file.

## Action Items

- [x] **Improve Fetching/Parsing (using local file):**
    - [x] Use `cp932` encoding.
    - [x] Find `<dl class='thread'>`.
    - [x] Correctly pair `<dt>` and `<dd>` tags.
    - [x] Refine `parse_post_header` regex.
- ~~[ ] Develop Content Selection Logic (Superseded by BERTopic):~~
- [x] **Integrate and Format:**
    - [x] Create HTML generation function (`format_output.py`).
    - [x] Structure: Mimic forum view (t_h/t_b divs, basic styles).
    - [x] Consistency: Replace "名無しさんの野望" with "名無しサモナー".
    - [x] Add Livedoor 'Read More' marker (`<!--more-->`) after first post.
    - [x] Style reply links (`>>`).
- [x] **Implement AI Topic Clustering (BERTopic):**
    - [x] Add `sentence-transformers`, `scikit-learn`, `hdbscan`, `sentencepiece`, `bertopic` to requirements.
    - [x] Create `topic_cluster.py` using BERTopic.
    - [x] Use `pkshatech/GLuCoSE-base-ja` embedding model.
    - [x] Implement basic title generation (`generate_cluster_title`) and update format.
    - [x] Integrate clustering into `main.py` loop.
    - [x] Tune BERTopic `min_topic_size` (currently 4).
- [x] **Implement Publishing:**
    - [x] Update `publish_blog.py` for AtomPub.
    - [x] Handle authentication securely using `.env`.
    - [x] Test publishing drafts.
- [ ] **Review & Refine Current Results:**
    - [ ] Evaluate the quality and coherence of the ~36 topics generated with `min_topic_size=4`.
    - [ ] Further tune BERTopic parameters (`min_topic_size`, representation model, etc.) if needed based on review.
    - [ ] Improve `generate_cluster_title` logic if current titles are not descriptive enough.
- [x] **Cleanup & Documentation:**
    - [x] Remove unused files (`preprocess_text.py`, `select_topic_posts.py`).
    - [x] Remove commented-out code and unused imports.
    - [x] Stop saving intermediate HTML files.
    - [x] Create `README.md`.
    - [x] Create `TECH_STACK.md`.
    - [x] Create `.gitignore`.
- [ ] **Future Enhancements:**
    - [ ] Add robust error handling throughout the pipeline (e.g., for network issues during publish).
    - [ ] Enhance logging (`logs/run.log`) with more detail if needed.
    - [ ] Explore different BERTopic representation models (e.g., KeyBERT, spaCy) for potentially better topic keywords/summaries (might influence title generation).
    - [ ] Add thumbnail selection logic (e.g., find first image in cluster?).
    - [ ] Revisit direct fetching if anti-bot measures can be overcome or alternative sources found.

## Configuration & Error Handling
- [x] Improve configuration management (`config.py` - added file/keyword vars).
- [ ] Add robust error handling throughout the pipeline.
- [ ] Enhance logging (`logs/run.log`). 