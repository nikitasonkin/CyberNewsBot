## CyberNewsBot 🛡️

## Overview
CyberNewsBot is a news aggregation system that retrieves, processes, summarizes, and distributes cybersecurity-related articles from RSS feeds. It includes text cleaning, summarization, deduplication, and message delivery to platforms like Telegram and Microsoft Teams.

---

### Configuration File: [`config.py`](https://github.com/nikitasonkin/CyberNewsBot/blob/main/src/config.py)

The `config.py` file is a crucial component of the **CyberNewsBot** project, responsible for managing configurations, environment settings, and logging. Below is a structured overview of its functionality:

---

#### **Logging System**
- **Purpose**: Sets up logging for both console and file outputs.  
- **Key Features**:
  - Logs to a rotating file `app.log`  
    - **Max size**: 10 MB  
    - **Backups**: 5 files
  - Log format: `timestamp - logger name - log level - message`
  - Captures both **INFO** (console) and **DEBUG** (file) levels
- **Why It Matters**: Provides detailed, consistent logs for debugging and monitoring.

---

#### **Environment Variables**
This file relies on environment variables (loaded with **dotenv**) for configurable or sensitive settings.

- **Critical Variables**:
  - `RSS_FEED_URL` – comma-separated RSS URLs (mandatory)
  - `RSS_COUNTRY_MAPPINGS` – optional `url:country` pairs
  - `API_KEY`, `SEARCH_ENGINE_ID` – external-integration keys
  - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` – Telegram credentials
  - `TEAMS_WEBHOOK_URL` – Microsoft Teams webhook
- **Validation**:
  - Verifies presence of required variables
  - Logs warnings for any that are missing, ensuring issues surface early

---

#### **File Constants**
- `LOCK_FILE` – prevents concurrent script instances  
- `POSTED_NEWS_FILE` – JSON log of previously posted news (deduplication)

---

#### **RSS Feed Management**
- **Loading & Cleaning**:
  - Trims whitespace, skips empty URLs
  - Raises an error if no valid feeds exist
- **Country Mapping**:
  - Parses mappings like `url1:country1,url2:country2`
  - Logs malformed or missing mappings

---

#### **Validation Function**
- **Purpose**: Confirms all required environment variables are set.  
- **Implementation**:
  - Checks each key and logs any omissions
  - Returns `True/False` to signal validation success

---

#### **Error Handling**
Comprehensive warnings/error logs for missing or malformed variables ensure robustness.

---

### JSON Handler File: [ `json_handler.py`](https://github.com/nikitasonkin/CyberNewsBot/blob/main/src/json_handler.py)

The `json_handler.py` file is an essential component of the **CyberNewsBot** project, responsible for handling JSON data operations such as loading, saving, and processing. Below is a structured overview of its functionality:

---

#### **Safe JSON Loading**
- **Function**: `safe_load_json(filepath, default)`
- **Purpose**: Safely loads JSON data from a file.
- **Key Features**:
  - Returns a default value if the file is missing or contains invalid JSON.
  - Ensures robustness when dealing with external data sources.

---

#### **Posted News Management**
- **Function**: `load_posted_news()`
  - **Purpose**: Loads previously posted news articles from `POSTED_NEWS_FILE`.
  - **Error Handling**: Returns an empty list if the file is not found or contains invalid JSON.

- **Function**: `save_posted_news(posted_news)`
  - **Purpose**: Saves a list of posted news articles to `POSTED_NEWS_FILE`.
  - **Key Features**:
    - Writes to a temporary file for data integrity.
    - Logs the number of saved articles.

---

#### **Skipped News Management**
- **Function**: `load_skipped_news()`  
  - Loads `skipped_news_ud.json` and converts legacy list format into a dictionary keyed by `id` for quick look‑ups.  
  - **Automatic cleanup**:  
    - Removes entries older than 14 days.  
    - Ignores articles with `fail_count` ≥ 3 (too many failures).  
  - Writes the filtered dataset back to disk and returns it.

- **Function**: `save_skipped_news(skipped_articles)`
  - **Purpose**: Updates and saves the skipped news list.
  - **Key Features**:
    - Merges new and existing skipped articles.
    - Tracks failure counts and updates metadata like `reason`, `summary`, and `text_hash`.
    - Dynamically calculates missing `text_hash` values.
    - Logs the number of new and total skipped articles.

---

#### **Error Handling and Validation**
- Each function incorporates robust error handling to manage:
  - Missing files
  - Invalid JSON
  - Unexpected data formats
- Skipped articles are validated and enriched with metadata such as:
  - Publication dates (`published_date`)
  - Source information
  - Reason for skipping

---

### Lock Manager File: [`lock_manager.py`](https://github.com/nikitasonkin/CyberNewsBot/blob/main/src/lock_manager.py)


The `lock_manager.py` module provides essential functions for managing lock files to ensure that only one instance of a script runs at a time. This is particularly useful in scenarios where concurrent executions could cause conflicts or duplicate processing.

---

#### **Key Functions**

- **`create_lock()`**
  - **Purpose**: Creates a lock file with the current process ID (PID).
  - **Why It Matters**: Prevents multiple instances of the script from running simultaneously.

- **`remove_lock()`**
  - **Purpose**: Deletes the lock file when the script finishes executing.
  - **Use Case**: Ensures that future runs are not blocked by stale lock files.

- **`is_script_running()`**
  - **Purpose**: Checks whether the script is already running by reading the PID from the lock file.
  - **Key Features**:
    - Cleans up stale lock files if the process is no longer active.
    - Helps maintain script execution integrity.

- **`is_process_running(pid)`**
  - **Purpose**: Verifies whether a process with the given PID is still running.
  - **Integration**: Uses the `psutil` library for cross-platform process checks.

---

#### **Integration**
- The module relies on a global constant `LOCK_FILE`, which is defined in the `config.py` module.
- It integrates with `psutil` to handle process management efficiently and reliably.

---

### Main Script File: [`main.py`](https://github.com/nikitasonkin/CyberNewsBot/blob/main/src/main.py)


The `src/main.py` file serves as the main entry point for the **CyberNewsBot** application — a news aggregation, processing, and distribution tool. It orchestrates the overall execution flow, including news retrieval, filtering, messaging, and resource management.

---

#### **Purpose**
- Coordinates the retrieval, filtering, and distribution of news articles.
- Manages logging, NLP resource setup, and script concurrency.

---

#### **Key Function: `process_and_send_articles()`**
- **Retrieves** news articles from Google Alerts.
- **Filters** out previously processed or duplicate articles.
- **Sends** new articles to a Telegram channel.

---

#### **Main Execution Flow**
- Verifies and downloads required NLP resources (e.g., `nltk.punkt`).
- Logs the script start time in `run_times.txt` and `log.txt`.
- Sends a "script started" message to Telegram.
- Prevents duplicate execution by checking for existing lock files.
- Creates a lock file to manage execution state.
- Calls `process_and_send_articles()` to run the main logic.
- Handles all exceptions and sends error notifications to Telegram.
- Removes the lock file as part of cleanup, ensuring future runs are not blocked.

---

#### **External Dependencies**
- **News Retrieval**: `feedparser`, `newspaper3k`
- **NLP Processing**: `nltk`, `transformers`
- **Web Scraping**: `BeautifulSoup`
- **System Monitoring**: `psutil`
- **Messaging**: Internal modules like `messaging.py`, `news_retrieval.py` for Telegram integration

---

#### **Files and Logs**
- **Lock File**: `script_running.lock` – Tracks whether the script is already running.
- **Log Files**:
  - `run_times.txt`: Records each execution timestamp.
  - `log.txt`: Captures detailed script logs and debugging info.

---

#### **Additional Notes**
- Implements robust error handling and logging.
- Uses lock mechanisms to ensure safe single-instance execution.
- Designed for stable, autonomous operation as part of an automated news delivery pipeline.

---

### Messaging Module: [`messaging.py`](https://github.com/nikitasonkin/CyberNewsBot/blob/main/src/messaging.py)

The `messaging.py` file provides the **communication layer** for CyberNewsBot, enabling automated delivery of news summaries to **Telegram** and **Microsoft Teams** while enforcing deduplication, error-tolerance, and retry logic.

---

#### **Key Functions**

| Function | Purpose | Highlights |
| --- | --- | --- |
| `send_telegram_message(message, retries=3, delay=5)` | Sends a plain-text or HTML message to a Telegram chat. | • Cleans HTML tags<br>• Retries on network errors & HTTP 429<br>• Logs status and errors |
| `post_articles_to_telegram(articles)` | Main dispatcher that processes a batch of article dictionaries and posts them to Telegram. | • Deduplicates by `title`, `url`, and `text_hash`<br>• Fetches full text & summarises with `summarize_text`<br>• Saves sent articles via `save_posted_news`<br>• Tracks failures via `save_skipped_news` |
| `send_to_teams(message, webhook_url, retries=3, delay=5)` | Sends an Adaptive Card payload to Microsoft Teams via webhook. | • Retries only on HTTP 429<br>• Rich formatting (title, date, summary, link)<br>• Logs success & failure |

---

#### **Core Workflow in `post_articles_to_telegram()`**

1. **Load State**  
   - `load_skipped_news()` and `load_posted_news()` fetch historical data to prevent duplicates.

2. **Deduplication Checks**  
   - Compares incoming articles against previously posted (`title`, normalized `url`, `text_hash`).  
   - Skips articles that failed ≥ 3 times within the last 14 days.

3. **Content Pipeline**  
   - Fetches full article text via `fetch_full_text()`.  
   - Generates a concise summary with `summarize_text()`.  
   - Recomputes `text_hash` if missing.

4. **Message Construction & Send**  
   - Builds an HTML Telegram message and an Adaptive Card payload for Teams.  
   - Calls `send_telegram_message()` and `send_to_teams()`, handling transient errors with retries.

5. **Persistence**  
   - Updates `posted_news_ud.json` and `skipped_news_ud.json` through `save_posted_news()` / `save_skipped_news()`.

---

#### **Error Handling & Resilience**

- **Network Resilience**: Retries with exponential-style delay for HTTP 429 (rate limiting).  
- **Graceful Fallbacks**: Skips or re-queues articles on fetch/summarization failures without crashing the pipeline.  
- **Atomic Writes**: Uses temporary files when updating JSON stores to avoid corruption.  
- **Verbose Logging**: Prints clear status messages for each major step (sending, skipping, hashing, summarising).

---

#### **Dependencies**

- **Standard**: `os`, `time`, `datetime`, `json`, `re`, `hashlib`, `html`
- **Networking**: `requests`
- **Parsing / NLP**: `BeautifulSoup`, `nltk`, `transformers`
- **News Utilities**: `feedparser`, `newspaper3k`
- **Internal Modules**:  
  - `json_handler.py` – load/save helpers  
  - `text_processing.py` – cleaning, hashing, source extraction  
  - `summarizer.py` – summary generation  
  - `news_retrieval.py` – full-text fetcher

---

#### **Design Notes**

- Separates concerns: message formatting vs. transport vs. persistence.  
- Centralises duplicate detection, ensuring each article is posted exactly once.  
- Supports multi-platform delivery (Telegram + Teams) with unified retry semantics.  

---


### News Retrieval Module: [`news_retrieval.py`](https://github.com/nikitasonkin/CyberNewsBot/blob/main/src/news_retrieval.py)


The `news_retrieval.py` module is responsible for **fetching**, **processing**, and **filtering** news articles from RSS feeds and external sources. It ensures that only relevant, valid, and unique articles move forward in the CyberNewsBot pipeline.

---

#### **Key Functions**

- **`get_google_alerts(time_range=1)`**
  - **Purpose**: Retrieves articles from predefined RSS feeds for a specified number of days back.
  - **Parameters**:
    - `time_range` (int): Number of days to fetch news for (default: `1` for today's news).
  - **Features**:
    - Cleans and normalizes metadata: `title`, `URL`, `summary`, `published_date`.
    - Filters out incomplete or low-quality articles (e.g., missing title/URL, short summaries).
    - Extracts metadata including `source`, `keywords`, and `text_hash`.
  - **Returns**: A list of cleaned and structured article dictionaries.

- **`fetch_full_text(url, max_words=600)`**
  - **Purpose**: Retrieves and processes the full content of an article from its URL.
  - **Parameters**:
    - `url` (str): The article's URL.
    - `max_words` (int): Maximum number of words to keep (default: `600`).
  - **Features**:
    - Uses `newspaper3k` to download and parse content.
    - Trims long articles and skips articles with less than 10 words.
    - Gracefully handles errors like parsing failures or connection issues.
  - **Returns**: Cleaned full-text string or an error indicator.

- **`filter_new_articles(articles)`**
  - **Purpose**: Filters out previously posted or skipped articles from the new batch.
  - **Features**:
    - Loads historical data from `posted_news` and `skipped_news` files.
    - Removes duplicates using `title`, `URL`, and `text_hash`.
    - Ensures only fresh, unique articles proceed.
  - **Returns**: A filtered list of new articles ready for summarization and distribution.

---

#### **Key Features**
- Efficient RSS feed parsing and news retrieval.
- Intelligent article validation (title, summary, date).
- Duplicate prevention using hash-based comparison.
- Full-text fetching and processing.
- Seamless integration with custom modules for configuration, text cleaning, and history tracking.

---

#### **Dependencies**

- **Standard Libraries**: `re`, `json`, `datetime`, `os`, `sys`
- **Third-Party Libraries**:
  - `feedparser`: RSS feed parsing
  - `BeautifulSoup`: HTML cleaning
  - `newspaper3k`: Article download and parsing
  - `nltk`, `transformers`: NLP tasks (summarization, tokenization)
  - `requests`: HTTP requests
- **Custom Modules**:
  - `config`: Loads environment variables and feed settings
  - `text_processing`: Cleans and tokenizes text
  - `json_handler`: Manages reading/writing posted and skipped articles

---

### Summarization Module: [`summarizer.py` ](https://github.com/nikitasonkin/CyberNewsBot/blob/main/src/summarizer.py)

The `src/summarizer.py` module is a core component of the **CyberNewsBot** project. It provides powerful and flexible text summarization capabilities using state-of-the-art NLP models and efficient GPU/CPU handling.

---

#### **Key Features**

- **Summarization Model Loader**
  - Dynamically loads the `facebook/bart-large-cnn` model from Hugging Face.
  - Automatically utilizes **GPU** if available, otherwise defaults to **CPU**.
  - Initializes tokenizer and model once, with fallback logic for reloading on failure.

- **RSS Summary Sufficiency Checker**
  - Validates whether RSS summaries contain enough content.
  - Enforces a minimum length of **15 words** to ensure relevance and completeness.

- **Text Summarization Functionality**
  - Preprocesses text:
    - Skips summarization for very short inputs (less than **30 words**).
    - Trims input to a maximum of **500 words** to optimize model performance.
  - Generates concise summaries:
    - Output length is dynamically controlled using minimum and maximum limits.
  - Includes fallback logic and detailed exception handling for:
    - Missing models
    - GPU memory issues
    - Inference errors

---

#### **Dependencies**

- **Core Libraries**:
  - `transformers`: Hugging Face Transformers for model loading and inference
  - `torch`: For GPU acceleration and tensor operations
  - `nltk`: Natural language processing and tokenization
  - `BeautifulSoup`: HTML tag cleaning
  - `newspaper3k`: Article extraction for full-text retrieval
  - `requests`, `re`, `json`: Various utility needs

---

#### **Example Usage**

```python
# Initialize the summarizer
summarizer = load_summarizer()

# Summarize a given long text
summary = summarize_text("Your long input text here...", title="Optional Title")

print(summary)

### Text Processing Module: `text_processing.py`
```

---

### Utility Module: [`text_processing.py`](https://github.com/nikitasonkin/CyberNewsBot/blob/main/src/text_processing.py)

`text_processing.py` delivers the **core text-sanitizing toolkit** for CyberNewsBot.  
It standardizes URLs, titles, and article bodies; calculates relevance; extracts keywords; and creates stable hashes for duplicate detection.

---

#### **Cleaning & Normalization**
- **`clean_url(url)`**  
  Canonicalizes links by dropping query strings and fragments.

- **`clean_title(title)`**  
  Strips HTML for user-facing display.

- **`clean_title_for_matching(title)`**  
  Preps titles for deduplication (strip HTML ➜ lowercase ➜ remove common suffixes like “ - Site”).

- **`clean_text(raw_text)`**  
  Removes HTML tags, collapses whitespace.

- **`safe_text_cut(text, max_words=500)`**  
  Ensures text stays within length budgets for downstream models.

---

#### **Relevance & Filtering**
- **`is_summary_relevant(summary, title, threshold=2)`**  
  Confirms summary shares at least *threshold* words with the title.

- **`extract_text_relevance(text, keywords)`**  
  Counts intersection between tokenized text and keyword list (NLTK).

- **`is_youtube_link(url)`**  
  Quick domain check for YouTube links (`youtube.com`, `youtu.be`).

---

#### **Duplicate Detection**
- **`compute_text_hash(text)`**  
  Generates SHA-256 hash of cleaned text → resilient identifier even if title/URL changes.

---

#### **Keyword & Source Utilities**
- **`extract_keywords(text, num_keywords=5)`**  
  Returns the top-N most frequent alpha tokens (>4 chars) via `collections.Counter`.

- **`extract_source_from_url(url)`**  
  Extracts domain (e.g., `bbc.com`) for source attribution.

---

#### **Dependencies**
- **Standard**: `re`, `hashlib`, `urllib.parse`, `collections.Counter`
- **Third-Party**: `BeautifulSoup` (HTML stripping), `nltk` (tokenization)

---

#### **Typical Usage**
```python
canonical = clean_url("https://news.com/article?id=1&utm=xyz")
title_key  = clean_title_for_matching("<h1>Breaking News - News.com</h1>")
hash_id    = compute_text_hash(article_summary)
keywords   = extract_keywords(article_body, 5)
```

---

### Project Structure
- `main.py`: Entry point for the application.
- `config.py`: Configuration and environment settings.
- `news_retrieval.py`: Functions for retrieving and filtering news articles.
- `text_processing.py`: Utilities for cleaning and processing text.
- `summarizer.py`: Functions for summarizing text using machine learning models.
- `messaging.py`: Handles sending messages to Telegram and Teams.
- `json_handler.py`: Manages JSON data for posted and skipped news.
- `lock_manager.py`: Ensures only one instance of the script runs at a time.
- `requirements.txt`: Lists all dependencies required for the project.
- `posted_news_ud.json`: Stores metadata of successfully posted news articles.
- `skipped_news_ud.json`: Tracks articles that failed processing.

---

### Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables in the `.env` file:
   - `API_KEY`
   - `SEARCH_ENGINE_ID`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `TEAMS_WEBHOOK_URL`
   - `RSS_FEED_URL`
   - `RSS_COUNTRY_MAP`
4. Run the script:
   ```bash
   python main.py

---

### Dependencies
- `beautifulsoup4`
- `feedparser`
- `newspaper3k`
- `nltk`
- `psutil`
- `python-dotenv`
- `requests`
- `torch`
- `transformers`

---

### Output Files
- ` posted_news_ud.json: All articles sent to Telegram/Teams `
- `skipped_news_ud.json: Articles skipped with reason, timestamp, and fail count`
- ` app.log: Debug logs and events`
- ` run_times.txt: Each run’s timestamp`

---

### License
-`This project is licensed under the MIT License.`

### Author
Created and maintained by Nikita Sonkin.
