## CyberNewsBot 🛡️

## Overview
The CYBER Project is a news aggregation and processing system designed to retrieve, process, summarize, and distribute news articles from various RSS feeds. The project includes functionalities for text cleaning, summarization, and sending updates to platforms like Telegram and Microsoft Teams.


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
