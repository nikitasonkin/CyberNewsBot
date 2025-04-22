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
import psutil  
from nltk.tokenize import word_tokenize
import hashlib
import requests
from urllib.parse import urlparse
import html
import time
import urllib.parse



#1
def clean_url(url):
    # Remove query parameters from the URL
    parsed_url = urlparse(url)
    clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    print(f"[CLEAN_URL] Cleaned: {clean_url}")
    return clean_url


#2
def clean_title(title):
    """Performs basic title cleaning for display purposes only."""
    return BeautifulSoup(title, "html.parser").get_text().strip()
#3
def clean_title_for_matching(title):
    """
    Cleans the title for matching purposes only:
    - Removes HTML tags
    - Converts to lowercase
    - Removes suffixes like ' - Source' or ' | Website'
    """
    title = BeautifulSoup(title, "html.parser").get_text()
    title = title.strip().lower()
    title = re.sub(r' - [\w\s]+$| \| [\w\s]+$', '', title)
    return title


#4
# 🔹 Clean text from HTML tags
def clean_text(raw_text):
    soup = BeautifulSoup(raw_text, "html.parser")
    text = soup.get_text()
    return re.sub(r'\s+', ' ', text).strip()

#5
def safe_text_cut(text, max_words=500):
    words = text.split()
    if len(words) > max_words:
        print(f"⚠️ Text exceeds {max_words} words – trimming.")
        return " ".join(words[:max_words])
    return text

#6
def is_summary_relevant(summary, title, threshold=2):
    """Checks if the summary contains at least `n` words from the title."""
    return extract_text_relevance(summary, title.split()) >= threshold

#7
def is_youtube_link(url):
    """Checks whether the given URL is a YouTube link."""
    parsed_url = urllib.parse.urlparse(url)
    return "youtube.com" in parsed_url.netloc or "youtu.be" in parsed_url.netloc

#8
def extract_text_relevance(text, keywords):
    if not text:
        return 0

    try:
        text_tokens = set(word_tokenize(text.lower()))
        keyword_tokens = set(word.lower() for word in keywords)
        return len(text_tokens & keyword_tokens)  # Intersection between tokens
    except Exception as e:
        print(f"⚠️ Error during tokenization: {e}")
        return 0

#9
def compute_text_hash(text):
    """
    Generates a hash from the content after removing HTML and extra whitespace.
    Used to identify duplicate articles even if the URL or title is different.
    """
    if not text or not isinstance(text, str):
        return None  # Prevents crashes on invalid input

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
