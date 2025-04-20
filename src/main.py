# ==================================================================================================
# main.py - Main process and entry point for the news aggregator
# ==================================================================================================
import re
import json
import urllib.parse
from datetime import datetime, timedelta
import os
import sys
from datetime import datetime
import nltk
# 🌐 Third-party libraries
import feedparser
from bs4 import BeautifulSoup
from transformers import pipeline
from newspaper import Article, ArticleException
import torch
import psutil  # תוסיף לייבוא אם עדיין אין
from nltk.tokenize import word_tokenize
import hashlib
import requests
from urllib.parse import urlparse
import html
import time
import urllib.parse
from messaging import send_telegram_message, post_articles_to_telegram
from lock_manager import create_lock, remove_lock, is_script_running
from news_retrieval import get_google_alerts,filter_new_articles
from news_retrieval import filter_new_articles




#1
# 🔹 הפעלת התהליך
def process_and_send_articles():
    print("📬 נכנס ל־process_and_send_articles()")
    articles = get_google_alerts()
    new_articles = filter_new_articles(articles)

    if new_articles:
        post_articles_to_telegram(new_articles)
    else:
        print("📭 אין חדשות חדשות להיום.")

LOCK_FILE = "script_running.lock"

#2
if __name__ == "__main__":
    now = datetime.now()
    os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

    print("התחלת main – הקוד התחיל לרוץ")

    try:
        nltk.data.find("tokenizers/punkt")
        print("משאב 'punkt' זמין.")
    except LookupError:
        nltk.download("punkt")
        print("'punkt' הותקן.")

    try:
        nltk.data.find("tokenizers/punkt_tab")
        print("משאב 'punkt_tab' זמין.")
    except LookupError:
        nltk.download("punkt_tab")
        print("'punkt_tab' הותקן.")

    try:
        with open("run_times.txt", "a", encoding="utf-8") as f:
            f.write(f"הרצה התחילה ב- {now.strftime('%Y-%m-%d %H:%M:%S')}\n")

        with open("log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n=== התחלה חדשה ב- {now.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

        print("מנסה לשלוח הודעת התחלה בטלגרם...")
        send_telegram_message(f"הרצה התחילה ב- {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print("הודעת טלגרם נשלחה")

        print("בודק אם הסקריפט כבר רץ...")
        if is_script_running():
            print("הסקריפט כבר רץ. יוצא.")
            sys.exit(0)

        print("יוצר קובץ נעילה...")
        create_lock()

        try:
            print("מתחיל לעבד ולשלוח כתבות...")
            process_and_send_articles()
            print("סיום תקין של process_and_send_articles()")
        except Exception as e:
            print(f"שגיאה כללית בהרצה: {e}")
            send_telegram_message(f"❌ שגיאה כללית בהרצה: {e}")

    finally:
        print("מנקה קובץ נעילה...")
        remove_lock()
        print("סיום סופי. יוצא מיידית.")
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)
