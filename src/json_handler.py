#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==================================================================================================
# json_handler.py - Functions for JSON data handling
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
import psutil  
from nltk.tokenize import word_tokenize
import hashlib
import requests
from urllib.parse import urlparse
import html
import time
import urllib.parse
from text_processing import compute_text_hash, extract_source_from_url
from config import POSTED_NEWS_FILE


#1
def safe_load_json(filepath, default):

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

#2
def load_posted_news():
    try:
        with open(POSTED_NEWS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

#3
def save_posted_news(posted_news):
    temp_file = POSTED_NEWS_FILE + ".tmp"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(posted_news, f, ensure_ascii=False, indent=4)
        os.replace(temp_file, POSTED_NEWS_FILE)
        print(f"📂 {len(posted_news)} posted articles saved successfully.")
    except Exception as e:
        print(f"⚠️ Error while saving posted_news: {e}")



#4
def load_skipped_news():
    skipped_articles = safe_load_json("skipped_news_ud.json", {})

    if isinstance(skipped_articles, list):
        skipped_articles = {article["id"]: article for article in skipped_articles}

# Cleaning old/failed
    cutoff_date = datetime.today() - timedelta(days=14)
    filtered = {}

    for article_id, article in skipped_articles.items():
        try:
            article_date = datetime.strptime(article.get("date", ""), "%Y-%m-%d")
            if article.get("fail_count", 0) < 3 and article_date >= cutoff_date:
                filtered[article_id] = {
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "fail_count": article.get("fail_count", 1),
                    "date": article.get("date", ""),
                    "reason": article.get("reason", ""),
                    "text_hash": article.get("text_hash", ""),
                    "summary": article.get("summary", ""),
                    "source": article.get("source", ""),
                    "published_date": article.get("published_date", ""),
                    "published_time": article.get("published_time", ""),
                    "rss_source": article.get("rss_source", "")
                }

        except ValueError:
            continue

    with open("skipped_news_ud.json", "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=4)

    return filtered

#5
def save_skipped_news(skipped_articles):
    skipped_file = "skipped_news_ud.json"
    try:
        with open(skipped_file, "r", encoding="utf-8") as f:
            existing_skipped = json.load(f)
            if isinstance(existing_skipped, list):
                existing_skipped = {article["id"]: article for article in existing_skipped}
    except (FileNotFoundError, json.JSONDecodeError):
        existing_skipped = {}

    today_date = datetime.today().strftime("%Y-%m-%d")
    current_time = datetime.today().strftime("%H:%M:%S")

    for article in skipped_articles:
        article_id = article["id"]
        reason = article.get("reason", "לא ידוע")
        title = article.get("title", "")
        url = article.get("url", "")
        summary = article.get("summary", "")
        source = article.get("source", extract_source_from_url(url))
        published_date = article.get("published_date", today_date)
        published_time = article.get("published_time", current_time)
        rss_source = article.get("rss_source", "Unknown") # Call the country field if it exists

        # Calculate hash if missing
        text_hash = article.get("text_hash") or compute_text_hash(summary)

        if article_id in existing_skipped:
            existing = existing_skipped[article_id]
            existing["fail_count"] = existing.get("fail_count", 1) + 1
            existing["date"] = today_date
            existing["reason"] = reason
            existing["text_hash"] = text_hash
            existing["summary"] = summary or existing.get("summary", "")
            existing["source"] = source or existing.get("source", "")
            existing["published_date"] = published_date
            existing["published_time"] = published_time
            existing["rss_source"] = rss_source
        else:
            existing_skipped[article_id] = {
                "title": title,
                "url": url,
                "fail_count": 1,
                "date": today_date,
                "reason": reason,
                "text_hash": text_hash,
                "summary": summary,
                "source": source,
                "published_date": published_date,
                "published_time": published_time,
                "rss_source": rss_source
            }

    with open(skipped_file, "w", encoding="utf-8") as f:
        json.dump(existing_skipped, f, ensure_ascii=False, indent=4)

    print(f"[INFO] Skipped list updated: {len(skipped_articles)} new, {len(existing_skipped)} total.")
