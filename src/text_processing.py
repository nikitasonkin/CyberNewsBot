# ==================================================================================================
# text_processing.py - Functions for text cleaning and processing
# ==================================================================================================
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



#1
def clean_url(url):
    # הסרת פרמטרים מהלינק
    parsed_url = urlparse(url)
    clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    print(f"[CLEAN_URL] Cleaned: {clean_url}")
    return clean_url

#2
def clean_title(title):
    """ לניקוי בסיסי לצורכי הצגה בלבד """
    return BeautifulSoup(title, "html.parser").get_text().strip()
#3
def clean_title_for_matching(title):
    """
    ניקוי כותרת לצורך השוואה בלבד:
    - הורדת HTML
    - אותיות קטנות
    - הסרת סיומות כמו ' - מקור' או ' | אתר'
    """
    title = BeautifulSoup(title, "html.parser").get_text()
    title = title.strip().lower()
    title = re.sub(r' - [\w\s]+$| \| [\w\s]+$', '', title)
    return title


#4
# 🔹 ניקוי טקסט מ-HTML
def clean_text(raw_text):
    soup = BeautifulSoup(raw_text, "html.parser")
    text = soup.get_text()
    return re.sub(r'\s+', ' ', text).strip()

#5
def safe_text_cut(text, max_words=500):
    words = text.split()
    if len(words) > max_words:
        print(f"⚠️ טקסט ארוך מ-{max_words} מילים, מבצע חיתוך.")
        return " ".join(words[:max_words])
    return text

#6
def is_summary_relevant(summary, title, threshold=2):
    """בודק האם תקציר מכיל לפחות n מילים מתוך הכותרת"""
    return extract_text_relevance(summary, title.split()) >= threshold

#7
def is_youtube_link(url):
    """בודק אם ה-URL הוא של YouTube"""
    parsed_url = urllib.parse.urlparse(url)
    return "youtube.com" in parsed_url.netloc or "youtu.be" in parsed_url.netloc

#8
def extract_text_relevance(text, keywords):
    if not text:
        return 0

    try:
        text_tokens = set(word_tokenize(text.lower()))
        keyword_tokens = set(word.lower() for word in keywords)
        return len(text_tokens & keyword_tokens)  # חיתוך בין שתי קבוצות
    except Exception as e:
        print(f"⚠️ שגיאה ב-tokenize: {e}")
        return 0

#9
def compute_text_hash(text):
    """
    יוצר hash מהתוכן לאחר ניקוי HTML ורווחים.
    משמש לזיהוי כתבות כפולות גם אם ה-URL או הכותרת שונים.
    """
    if not text or not isinstance(text, str):
        return None  # מגן בפני קריסות

    cleaned = clean_text(text).strip().lower()
    return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()

from urllib.parse import urlparse

def extract_source_from_url(url):
    try:
        return urlparse(url).netloc
    except:
        return ""

from nltk.tokenize import word_tokenize
from collections import Counter

def extract_keywords(text, num_keywords=5):
    try:
        tokens = word_tokenize(text.lower())
        tokens = [t for t in tokens if t.isalpha() and len(t) > 4]
        most_common = Counter(tokens).most_common(num_keywords)
        return [kw for kw, _ in most_common]
    except Exception:
        return []