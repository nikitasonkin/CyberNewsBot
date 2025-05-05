#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==================================================================================================
# summarizer.py - Functions for text summarization
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
def load_summarizer():
    try:
        if torch.cuda.is_available():
            print("🚀 Using GPU for summarization")
            return pipeline("summarization", model="facebook/bart-large-cnn", device=0)
        else:
            print("⚠️ GPU not available, falling back to CPU")
            return pipeline("summarization", model="facebook/bart-large-cnn", device=-1)
    except Exception as e:
        print(f"⚠️ GPU failed – switching to CPU: {e}")
        torch.cuda.empty_cache()  
        return pipeline("summarization", model="facebook/bart-large-cnn", device=-1)


#2
def is_rss_summary_sufficient(text):
    """
    Checks whether the RSS summary is sufficient:
    - Contains at least 20 words.
    - Not empty or too short.
    """
    word_count = len(text.split())
    return word_count >= 15


summarizer_loaded = False # Global flag to check if the model is loaded
#3
def summarize_text(text, title=""):
    global summarizer, summarizer_loaded

    try:
        # Check if the model is already loaded
        if not summarizer_loaded or summarizer is None:
            print("⚠️ Summarization model not loaded – reloading...")
            summarizer = load_summarizer()
            summarizer_loaded = True

        if not text.strip():
            print("⚠️ Input text is empty.")
            return ""

        # Return short texts (under 30 words) as-is
        original_word_count = len(text.split())
        if original_word_count < 30:
            print(f"✅ Short text detected ({original_word_count} words) – skipping summarization.")
            return text

        # Optionally prepend the title as hidden context
        if title:
            text = f"{title}. {text}"

        # Trim to 500 words max
        if original_word_count > 500:
            text = " ".join(text.split()[:500])

        max_length = min(200, original_word_count * 2)
        min_length = max(20, max_length // 2)

        print(f"🤖 Summarizing {len(text.split())} words with max_length={max_length}, min_length={min_length}...")
        summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)

        if summary and summary[0]['summary_text'].strip():
            summarized_text = summary[0]['summary_text'].strip()
            word_count = len(summarized_text.split())
            print(f"✅ Summary generated – {word_count} words.")
            return summarized_text
        else:
            print("⚠️ Empty summary returned – using fallback.")
            return ""

    except NameError as ne:
        print(f"⚠️ Model error (not found): {ne}")
        summarizer_loaded = False
        return summarize_text(text, title)  # Retry after reloading

    except Exception as e:
        print(f"🔥 Error during summarization: {e}")
        torch.cuda.empty_cache()
        summarizer_loaded = False
        return ""



