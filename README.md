CyberNewsBot 🛡️
Overview
The CYBER Project is a news aggregation and processing system designed to retrieve, process, summarize, and distribute news articles from various RSS feeds. The project includes functionalities for text cleaning, summarization, and sending updates to platforms like Telegram and Microsoft Teams.

Features
🔎 Retrieve cyber news from multiple country-specific RSS feeds

🧼 Clean and normalize article text and metadata

🧠 Summarize full articles using a pre-trained transformer model (BART)

🔁 Eliminate duplicates using title, url, and text_hash

📤 Send to Telegram and Teams with formatted message

📂 Track skipped articles with reasons, dates, and fail counts

🪵 Store logs for monitoring and debugging

🔐 Use a lock file to avoid parallel runs

Project Structure
main.py: Entry point for the application.

config.py: Configuration and environment settings.

news_retrieval.py: Functions for retrieving and filtering news articles.

text_processing.py: Utilities for cleaning and processing text.

summarizer.py: Functions for summarizing text using machine learning models.

messaging.py: Handles sending messages to Telegram and Teams.

json_handler.py: Manages JSON data for posted and skipped news.

lock_manager.py: Ensures only one instance of the script runs at a time.

requirements.txt: Lists all dependencies required for the project.

posted_news_ud.json: Stores metadata of successfully posted news articles.

skipped_news_ud.json: Tracks articles that failed processing.

run_times.txt: Logs the execution times of the script.

Setup
Clone the repository.
Install dependencies:
pip install -r requirements.txt
Configure environment variables in the .env file:
API_KEY
SEARCH_ENGINE_ID
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
TEAMS_WEBHOOK_URL
RSS_FEED_URL
RSS_COUNTRY_MAP
Run the script:
python main.py
Dependencies
beautifulsoup4
feedparser
newspaper3k
nltk
psutil
python-dotenv
requests
torch
transformers
##Output Files posted_news_ud.json: All articles sent to Telegram/Teams skipped_news_ud.json: Articles skipped with reason, timestamp, and fail count log.txt: Debug logs and events run_times.txt: Each run’s timestamp

Logging
Logs are stored in app.log and include detailed information about the script's execution, including errors and processed articles.

License
This project is licensed under the MIT License.

##Author Created and maintained by Nikita Sonkin.
