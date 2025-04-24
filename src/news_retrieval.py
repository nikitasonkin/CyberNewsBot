# 📦 Built-in libraries
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

# Import from our modules
from config import logger, RSS_FEED_URL, rss_country_map
from text_processing import clean_text, clean_url, clean_title_for_matching, compute_text_hash, extract_source_from_url, extract_keywords
from json_handler import load_posted_news, load_skipped_news


#---------------------------------------------------------------------------------------------------------------------------------------------------------
#1
def get_google_alerts(time_range=1):
    """
    Retrieves articles from predefined RSS feeds.
    
    :param time_range: Number of days back to fetch news (default: 1 – today's news)
    :return: A list of new articles with additional metadata
    """
    articles = []
    today = datetime.today().date()
    start_date = today - timedelta(days=time_range)
    invalid_count = 0

    for rss_url in RSS_FEED_URL:
        try:
            response = requests.get(rss_url, timeout=10)
            response.raise_for_status()
            feed = feedparser.parse(response.text)

            if not feed.entries:
                print(f"⚠️ No articles found in RSS: {rss_url}")
                continue

            print(f"📡 RSS Source: {rss_url} - {len(feed.entries)} articles found.")
            rss_source = rss_country_map.get(rss_url, "Unknown")  

            for entry in feed.entries:
                try:
                    article_id = entry.id if hasattr(entry, "id") else str(datetime.now().timestamp())
                    title = clean_text(entry.title) if hasattr(entry, "title") else None
                    raw_url = entry.link if hasattr(entry, "link") else None
                    clean_url = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query).get("url", [raw_url])[0] if raw_url else None
                    summary = clean_text(entry.summary) if hasattr(entry, "summary") else ""
                    published_dt = datetime(*entry.published_parsed[:6]) if hasattr(entry, "published_parsed") else datetime.now()
                    published_date_obj = published_dt.date()
                    published_date = published_dt.strftime("%Y-%m-%d")
                    published_time = published_dt.strftime("%H:%M:%S")

                   # Filter by date range
                    if start_date <= published_date_obj <= today:
                        if not title or not clean_url:
                            print(f"⚠️ Invalid article (missing title or URL) – skipping.")
                            invalid_count += 1
                            continue

                        # Check summary length
                        word_count = len(summary.split())
                        if word_count < 10:
                            print(f"⚠️ Summary too short ({word_count} words) – skipping.")
                            invalid_count += 1
                            continue

                        source = extract_source_from_url(clean_url)
                        keywords = extract_keywords(summary)
                        text_hash = compute_text_hash(summary) if summary.strip() else None

                        articles.append({
                            "id": article_id,
                            "title": title,
                            "url": clean_url,
                            "text_hash": text_hash,
                            "published_date": published_date,
                            "published_time": published_time,
                            "summary": summary,
                            "source": source,
                            "keywords": keywords,
                            "rss_source": rss_source  
                        })
                        print(f"✅Article added: {title}")

                except Exception as e:
                    print(f"⚠️ Error processing article from RSS ({rss_url}): {e}")

        except requests.RequestException as e:
            print(f"❌Failed to fetch RSS from -{rss_url}: {e}")
    print(f"📡 Total new articles retrieved from all RSS feeds: {len(articles)} (Skipped: {invalid_count})")
    return articles




#2
def fetch_full_text(url, max_words=600):
    """
    Retrieves the full text from a given article URL.
    
    :param url: The article's URL
    :param max_words: Maximum number of words to return (default: 600)
    :return: The article's text or an error message
    """
    try:
        print(f"🌐 Attempting to fetch article from URL: {url}")
        # Create the Article object with a custom User-Agent
        article = Article(url, language='en')
        article.download()
        print(f"⬇️ Article download successful: {url}")
        article.parse()
        print(f"📝 Article parsing successful: {url}")

        text = article.text.strip()
        word_count = len(text.split())
        print(f"📄 Extracted {word_count} words from article: {url}")

        # Check if the article is too short
        if word_count < 10:
            print(f"⚠️ Article text too short (<10 words) – skipping: {url}")
            return "⚠️ Article text too short (<10 words)"

        # Trim the article if it's too long
        if word_count > max_words:
            text = " ".join(text.split()[:max_words])
            print(f"✂️ Trimming article to {max_words} words: {url}")

        print(f"✅ Full article text successfully extracted: {url}")
        return text

    except ArticleException as ae:
        print(f"⚠️ ArticleException while processing article from {url}: {ae}")
        return "⚠️ Article processing error"

    except ConnectionError as ce:
        print(f"⚠️ Connection error while accessing article from {url}: {ce}")
        return "⚠️ Connection error"

    except Exception as e:
        print(f"⚠️ General error while retrieving article from {url}: {e}")
        return "⚠️ General article retrieval error"


#3
def filter_new_articles(articles):
    try:
        posted_news = load_posted_news()
        print(f"✅ Successfully loaded previously sent articles. ({len(posted_news)} items)")
    except Exception as e:
        print(f"⚠️ Error loading sent articles: {e}")
        posted_news = []

    try:
        skipped_news = load_skipped_news()
        print(f"✅ Successfully loaded previously skipped articles. ({len(skipped_news)} items)")
    except Exception as e:
        print(f"⚠️ Error loading skipped articles: {e}")
        skipped_news = {}

    new_articles = []

    for article in articles:
        title = clean_title_for_matching(article.get("title", ""))
        url = clean_url(article.get("url", ""))
        content = article.get("summary", "")
        content_word_count = len(content.split())

        print(f"[DEBUG] Checking article: title='{title}' | url='{url}' | summary word count={content_word_count}")

        if not title or not url:
            print(f"⚠️ Article missing title or URL: {article}")
            continue

        # תמיד מחשבים hash (אם יש תוכן)
        text_hash = compute_text_hash(content) if content.strip() else None
        article["text_hash"] = text_hash

        new_articles.append(article)

    print(f"✅ Found {len(new_articles)} articles to process (duplicates will be filtered later).")
    return new_articles
