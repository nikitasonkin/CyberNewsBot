# ==================================================================================================
# main.py - Main process and entry point for the news aggregator
# ==================================================================================================
import re
import json
import urllib.parse
from datetime import datetime, timedelta
import os
import sys
import nltk
# 🌐 Third-party libraries
import feedparser
from bs4 import BeautifulSoup
from transformers import pipeline
from newspaper import Article, ArticleException
import torch
import psutil 
from nltk.tokenize import word_tokenize
import hashlib
import requests
from urllib.parse import urlparse
import html
import time
from messaging import send_telegram_message, post_articles_to_telegram
from lock_manager import create_lock, remove_lock, is_script_running
from news_retrieval import get_google_alerts,filter_new_articles





#1
# 🔹 Starting the process
def process_and_send_articles():
    print("📬 Entered process_and_send_articles()")
    articles = get_google_alerts()
    new_articles = filter_new_articles(articles)

    if new_articles:
        post_articles_to_telegram(new_articles)
    else:
        print("📭 No new articles for today.")


LOCK_FILE = "script_running.lock"

#2
if __name__ == "__main__":
    now = datetime.now()
    os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
    print("[INFO] Main execution started.")

    try:
        nltk.data.find("tokenizers/punkt")
        print("NLTK resource 'punkt' is available.")
except LookupError:
    nltk.download("punkt")
    print("NLTK resource 'punkt' has been downloaded.")


    try:
        nltk.data.find("tokenizers/punkt_tab")
        print("NLTK resource 'punkt_tab' is available.")
except LookupError:
    nltk.download("punkt_tab")
    print("NLTK resource 'punkt_tab' has been downloaded.")


    try:
        with open("run_times.txt", "a", encoding="utf-8") as f:
            f.write(f"Execution started at {now.strftime('%Y-%m-%d %H:%M:%S')}\n")

        with open("log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n=== New run started at {now.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

        print("Attempting to send startup message via Telegram...")
        send_telegram_message(f"Execution started at {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print("Telegram message sent.")

        print("Checking if script is already running...")
        if is_script_running():
            print("Script is already running. Exiting.")
            sys.exit(0)

        print("Creating lock file...")
        create_lock()

        try:
            print("Starting to process and send articles...")
            process_and_send_articles()
            print("✅ process_and_send_articles() completed successfully.")
        except Exception as e:
            print(f"❌ General error during execution: {e}")
            send_telegram_message(f"❌ General error during execution: {e}")

    finally:
        print("Cleaning up lock file...")
        remove_lock()
        print("Final cleanup complete. Exiting now.")
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)
