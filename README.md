## CyberNewsBot 🛡️

## Overview
CyberNewsBot is a news aggregation system that retrieves, processes, summarizes, and distributes cybersecurity-related articles from RSS feeds. It includes text cleaning, summarization, deduplication, and message delivery to platforms like Telegram and Microsoft Teams.


### Configuration File: `config.py`

The `config.py` file is a crucial component of the **CyberNewsBot** project, responsible for managing configurations, environment settings, and logging. Below is a structured overview of its functionality:

---

#### **Logging System**
- **Purpose**: Sets up logging for both console and file outputs.
- **Key Features**:
  - Logs to a file (`app.log`) with rotation:
    - Maximum file size: 10 MB.
    - Keeps 5 backup files.
  - Formats logs with: `timestamp - logger name - log level - message`.
  - Logs both INFO and DEBUG levels.
- **Why It Matters**: Ensures detailed and consistent logging for debugging and monitoring purposes.

---

#### **Environment Variables**
This file relies on environment variables to fetch sensitive or configurable settings. These are loaded via the `dotenv` library.

- **Critical Variables**:
  - `RSS_FEED_URL`: A comma-separated list of RSS feed URLs (mandatory).
  - `RSS_COUNTRY_MAPPINGS`: Maps RSS feed URLs to countries (optional).
  - `API_KEY`, `SEARCH_ENGINE_ID`: Keys for external integrations.
  - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`: Credentials for Telegram bot integration.
  - `TEAMS_WEBHOOK_URL`: Webhook for Microsoft Teams notifications.
- **Validation**:
  - Ensures that all critical environment variables are present.
  - Logs warnings for missing variables, ensuring issues are identified early.

---

#### **File Constants**
- `LOCK_FILE`: Used to prevent multiple script instances from running concurrently.
- `POSTED_NEWS_FILE`: Tracks previously posted news in JSON format to avoid duplicates.

---

#### **RSS Feed Management**
- Loads and cleans RSS feed URLs:
  - Strips whitespace and skips empty URLs.
  - Logs a sample of loaded feeds for verification.
- Handles URL-country mappings:
  - Parses mappings in the format: `url1:country1,url2:country2`.
  - Logs errors if mappings are malformed or missing.

---

#### **Validation Function**
- **Purpose**: Ensures all required environment variables are set and valid.
- **Implementation**:
  - Checks for missing variables and logs warnings.
  - Returns a boolean indicating validation success.

---

#### **Error Handling**
- Logs errors and warnings for missing or malformed environment variables, ensuring robustness.

---

**Source**: [View the file on GitHub](https://github.com/nikitasonkin/CyberNewsBot/blob/main/src/config.py)

### JSON Handler File: `json_handler.py`

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
  - **Purpose**: Loads skipped news articles from `skipped_news_ud.json`.
  - **Key Features**:
    - Converts list-based JSON into a dictionary for efficient access.
    - Filters out old or failed articles based on a 14-day cutoff.
    - Removes articles with more than 3 failed attempts.

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

**Source**: [View the file on GitHub](https://github.com/nikitasonkin/CyberNewsBot/blob/main/src/json_handler.py)

### Lock Manager File: `lock_manager.py`

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

**Source**: [View the file on GitHub](https://github.com/nikitasonkin/CyberNewsBot/blob/main/src/lock_manager.py)

### Main Script File: `main.py`

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

**Source**: [View the file on GitHub](https://github.com/nikitasonkin/CyberNewsBot/blob/main/src/main.py)

### Main Script File: `main.py`

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

**Source**: [View the file on GitHub](https://github.com/nikitasonkin/CyberNewsBot/blob/main/src/main.py)

### Messaging Module: `messaging.py`

The `messaging.py` file provides essential functions for sending messages to communication platforms such as **Telegram** and **Microsoft Teams**. It plays a critical role in automating the dissemination of news articles with a focus on reliability, clarity, and error tolerance.

---

#### **Key Functions**

- **`send_telegram_message(message, retries=3, delay=5)`**
  - **Purpose**: Sends a message to a Telegram chat using a bot token and chat ID.
  - **Features**:
    - Retries in case of network issues or HTTP 429 (rate limiting).
    - Cleans the message content (e.g., HTML tags) before sending.
    - Logs errors if sending fails after all retries.

- **`post_articles_to_telegram(articles)`**
  - **Purpose**: Processes and sends a batch of news articles to a Telegram channel.
  - **Key Features**:
    - Filters out duplicate articles based on `title`, `URL`, or `text_hash`.
    - Fetches full text of articles (if needed) and summarizes them.
    - Formats and sends concise messages via Telegram.
    - Tracks and saves sent and skipped articles for reference.

- **`send_to_teams(message, webhook_url, retries=3, delay=5)`**
  - **Purpose**: Sends a formatted message to a Microsoft Teams channel via webhook.
  - **Key Features**:
    - Supports retries on rate-limit errors.
    - Sends content as an adaptive card with basic formatting.

---

#### **Core Features**

- **Error Handling**: Built-in logic to catch and manage:
  - Network failures
  - Invalid responses
  - Duplicate detection
- **Content Summarization**:
  - Integrates with NLP tools to generate concise summaries for Telegram/Teams messages.
- **Configurable Retries**:
  - Functions include retry logic to handle transient issues.
- **Deduplication Logic**:
  - Prevents sending the same article multiple times using checks against previously posted articles.

---

#### **Dependencies**

- **Standard Libraries**: `os`, `datetime`, `json`, `time`, `re`
- **Third-Party Libraries**:
  - `requests`: For HTTP requests to Telegram and Teams.
  - `BeautifulSoup`: For HTML content cleaning.
  - `nltk`, `transformers`: For summarization and NLP processing.
  - `feedparser`: For RSS integration.

---

**Source**: [View the file on GitHub](https://github.com/nikitasonkin/CyberNewsBot/blob/main/src/messaging.py)

### News Retrieval Module: `news_retrieval.py`

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

**Source**: [View the file on GitHub](https://github.com/nikitasonkin/CyberNewsBot/blob/main/src/news_retrieval.py)

### Summarization Module: `summarizer.py`

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

The `src/text_processing.py` file is a **utility module** in the **CyberNewsBot** project, providing essential functions for **text cleaning**, **URL processing**, **relevance scoring**, and **duplicate detection**. It ensures consistency and quality of input data before it is passed to downstream components such as the summarizer or message delivery systems.

---

#### **Key Features**

- **URL Cleaning**
  - `clean_url(url)`: Removes query parameters from URLs for normalization and deduplication.

- **Title Cleaning**
  - `clean_title(title)`: Strips HTML tags for cleaner display in messages.
  - `clean_title_for_matching(title)`: Prepares titles for comparison by:
    - Removing HTML tags
    - Lowercasing text
    - Stripping suffixes (e.g., site names)

- **Text Cleaning**
  - `clean_text(raw_text)`: Cleans HTML, whitespace, and extraneous characters from raw text.
  - `safe_text_cut(text, max_words=500)`: Trims long texts to a maximum word limit, useful for model input.

- **Relevance and Matching**
  - `is_summary_relevant(summary, title, threshold=2)`: Checks if the summary contains enough overlap with the title to be considered relevant.
  - `extract_text_relevance(text, keywords)`: Calculates how many keywords appear in the text, supporting filtering logic.

- **YouTube Link Detection**
  - `is_youtube_link(url)`: Determines whether the provided URL is a YouTube video link.

- **Duplicate Detection**
  - `compute_text_hash(text)`: Generates a SHA-256 hash of cleaned text for identifying duplicate content.

- **Keyword Extraction**
  - `extract_keywords(text, num_keywords=5)`: Extracts the most common words from the text using frequency analysis.

- **Source Extraction**
  - `extract_source_from_url(url)`: Extracts and returns the domain name (e.g., `bbc.com`) from a URL.

---

#### **Dependencies**

- **Standard Libraries**:
  - `re`, `hashlib`, `urllib.parse`, `collections.Counter`
- **Third-Party Libraries**:
  - `nltk`: Tokenization and basic NLP utilities
  - `BeautifulSoup`: Cleans HTML content

---

#### **Example Usage**

```python
# Clean a URL
cleaned_url = clean_url("https://example.com/article?id=123&ref=xyz")

# Extract keywords from a text
keywords = extract_keywords("Cybersecurity is evolving fast. Companies need better defense.", num_keywords=3)

# Generate content hash
content_hash = compute_text_hash("<p>Breaking news on AI and cybersecurity.</p>")



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


### Output Files
- ` posted_news_ud.json: All articles sent to Telegram/Teams `
- `skipped_news_ud.json: Articles skipped with reason, timestamp, and fail count`
- ` app.log: Debug logs and events`
- ` run_times.txt: Each run’s timestamp`

### License
-`This project is licensed under the MIT License.`

### Author
Created and maintained by Nikita Sonkin.
