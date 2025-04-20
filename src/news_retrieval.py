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
import psutil  # תוסיף לייבוא אם עדיין אין
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

#פונקציות לשליפת חדשות
#---------------------------------------------------------------------------------------------------------------------------------------------------------
#1
def get_google_alerts(time_range=1):
    """
    שולף כתבות מ-RSS שהוגדרו מראש.
    :param time_range: מספר הימים לאחור לשליפת חדשות (ברירת מחדל: 1 - היום הנוכחי)
    :return: רשימת כתבות חדשות עם שדות נוספים
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
                print(f"⚠️ אין כתבות ב-RSS: {rss_url}")
                continue

            print(f"📡 מקור RSS: {rss_url} - נמצאו {len(feed.entries)} כתבות.")
            rss_source = rss_country_map.get(rss_url, "Unknown")  # כאן מוסף שדה המדינה

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

                    # סינון לפי טווח תאריכים
                    if start_date <= published_date_obj <= today:
                        if not title or not clean_url:
                            print(f"⚠️ כתבה לא תקינה (כותרת/URL חסרים) - מדלג.")
                            invalid_count += 1
                            continue

                        # בדיקת אורך התקציר
                        word_count = len(summary.split())
                        if word_count < 10:
                            print(f"⚠️ תקציר קצר מדי ({word_count} מילים) - מדלג.")
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
                            "rss_source": rss_source  # הוספת המדינה
                        })
                        print(f"✅ נוספה כתבה: {title}")

                except Exception as e:
                    print(f"⚠️ שגיאה בעיבוד כתבה מ-RSS ({rss_url}): {e}")

        except requests.RequestException as e:
            print(f"❌ שגיאה בשליפת RSS מ-{rss_url}: {e}")

    print(f"📡 נמצאו {len(articles)} כתבות חדשות מכל ה-RSS (נדחו: {invalid_count}).")
    return articles




#2
def fetch_full_text(url, max_words=600):
    """
    שליפת טקסט מלא מכתבה
    :param url: כתובת URL של המאמר
    :param max_words: מספר המילים המקסימלי לשליפה (ברירת מחדל: 600)
    :return: טקסט המאמר או הודעת שגיאה
    """
    try:
        print(f"🌐 מנסה לשלוף כתבה מ-URL: {url}")
        # הגדרת מאמר עם User-Agent מותאם
        article = Article(url, language='en')
        article.download()
        print(f"⬇️ הורדת המאמר הצליחה: {url}")
        article.parse()
        print(f"📝 ניתוח המאמר הצליח: {url}")

        text = article.text.strip()
        word_count = len(text.split())
        print(f"📄 נשלפו {word_count} מילים מהכתבה: {url}")

        # בדיקה אם הכתבה קצרה מדי
        if word_count < 10:
            print(f"⚠️ טקסט קצר מדי (פחות מ-10 מילים) - דילוג על כתבה: {url}")
            return "⚠️ טקסט קצר מדי (פחות מ-10 מילים)"

        # חיתוך הטקסט במידה וארוך מדי
        if word_count > max_words:
            text = " ".join(text.split()[:max_words])
            print(f"✂️ חותך את הטקסט ל-{max_words} מילים: {url}")

        print(f"✅ טקסט שלם נשלף בהצלחה: {url}")
        return text

    except ArticleException as ae:
        print(f"⚠️ שגיאה בעיבוד מאמר (ArticleException) מ-{url}: {ae}")
        return "⚠️ שגיאת עיבוד מאמר"

    except ConnectionError as ce:
        print(f"⚠️ שגיאת חיבור לכתבה מ-{url}: {ce}")
        return "⚠️ שגיאת חיבור לאתר"

    except Exception as e:
        print(f"⚠️ שגיאה כללית בשליפת כתבה מ-{url}: {e}")
        return "⚠️ שגיאה כללית בשליפת כתבה"


#3
def filter_new_articles(articles):
    try:
        posted_news = load_posted_news()
        print(f"✅ נתוני כתבות שכבר נשלחו נטענו בהצלחה. ({len(posted_news)} פריטים)")
    except Exception as e:
        print(f"⚠️ שגיאה בטעינת כתבות שנשלחו: {e}")
        posted_news = []

    try:
        skipped_news = load_skipped_news()
        print(f"✅ נתוני כתבות שנכשלו נטענו בהצלחה. ({len(skipped_news)} פריטים)")
    except Exception as e:
        print(f"⚠️ שגיאה בטעינת כתבות שנכשלו: {e}")
        skipped_news = {}

    processed_titles = set()
    processed_urls = set()
    processed_hashes = set()

    for item in posted_news:
        processed_titles.add(clean_title_for_matching(item.get("title", "")))
        processed_urls.add(clean_url(item.get("url", "")))
        processed_hashes.add(item.get("text_hash", ""))

    for item in skipped_news.values():
        processed_titles.add(clean_title_for_matching(item.get("title", "")))
        processed_urls.add(clean_url(item.get("url", "")))
        processed_hashes.add(item.get("text_hash", ""))

    new_articles = []
    duplicate_count = 0

    for article in articles:
        title = clean_title_for_matching(article.get("title", ""))
        url = clean_url(article.get("url", ""))
        content = article.get("summary", "")
        content_word_count = len(content.split())

        print(f"[DEBUG] בודק כתבה: title='{title}' | url='{url}' | מילים בתקציר={content_word_count}")

        if not title or not url:
            print(f"⚠️ כתבה ללא כותרת או כתובת: {article}")
            continue

        if title in processed_titles:
            duplicate_count += 1
            print(f"[🔁 DUPLICATE_TITLE] '{title}' נמצא כבר – דילוג.")
            continue

        if url in processed_urls:
            duplicate_count += 1
            print(f"[🔁 DUPLICATE_URL] '{url}' נמצא כבר – דילוג.")
            continue

        # חישוב hash תמיד, אם יש תקציר כלשהו
        text_hash = compute_text_hash(content) if content.strip() else None
        if text_hash:
            print(f"[HASH] חושב hash: {text_hash}")
            if text_hash in processed_hashes:
                duplicate_count += 1
                print(f"[🔁 DUPLICATE_HASH] hash='{text_hash}' כבר קיים – דילוג.")
                continue

        article["text_hash"] = text_hash
        new_articles.append(article)
        processed_titles.add(title)
        processed_urls.add(url)
        if text_hash:
            processed_hashes.add(text_hash)

    print(f"🧐 מסנן {duplicate_count} כתבות כפולות או שכבר נכשלו בעבר.")
    print(f"✅ נמצאו {len(new_articles)} כתבות חדשות לשליחה.")
    return new_articles
