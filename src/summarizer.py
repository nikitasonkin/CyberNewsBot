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
import psutil  # תוסיף לייבוא אם עדיין אין
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
            print("🚀 משתמש ב-GPU")
            return pipeline("summarization", model="facebook/bart-large-cnn", device=0)
        else:
            print("⚠️ GPU לא זמין, עובר ל-CPU")
            return pipeline("summarization", model="facebook/bart-large-cnn", device=-1)
    except Exception as e:
        print(f"⚠️ GPU קרס, עובר ל-CPU: {e}")
        torch.cuda.empty_cache()  # ניקוי זיכרון GPU
        return pipeline("summarization", model="facebook/bart-large-cnn", device=-1)


#2
def is_rss_summary_sufficient(text):
    """
    בודק אם התקציר מ-RSS מספק:
    - מכיל לפחות 20 מילים.
    - אינו ריק או קצר מדי.
    """
    word_count = len(text.split())
    return word_count >= 20


summarizer_loaded = False  # משתנה גלובלי לבדיקת טעינת המודל
#3
def summarize_text(text, title=""):
    global summarizer, summarizer_loaded

    try:
        # בדיקה אם המודל נטען כבר
        if not summarizer_loaded or summarizer is None:
            print("⚠️ המודל לא נטען, טוען מחדש...")
            summarizer = load_summarizer()
            summarizer_loaded = True

        if not text.strip():
            print("⚠️ טקסט ריק.")
            return ""

        # אם הטקסט קצר מ-30 מילים - מחזיר אותו כמו שהוא
        original_word_count = len(text.split())
        if original_word_count < 30:
            print(f"✅ טקסט קצר ({original_word_count} מילים), לא מבצע סיכום.")
            return text

        # מוסיף את הכותרת כהנחיה סמוייה
        if title:
            text = f"{title}. {text}"

        # חיתוך הטקסט ל-500 מילים לכל היותר
        if original_word_count > 500:
            text = " ".join(text.split()[:500])

        max_length = min(200, original_word_count * 2)
        min_length = max(20, max_length // 2)

        print(f"🤖 מבצע סיכום על {len(text.split())} מילים עם max_length={max_length}, min_length={min_length}...")
        summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)

        if summary and summary[0]['summary_text'].strip():
            summarized_text = summary[0]['summary_text'].strip()
            word_count = len(summarized_text.split())
            print(f"✅ נוצר תקציר באורך {word_count} מילים.")
            return summarized_text
        else:
            print("⚠️ התקציר ריק – fallback.")
            return ""

    except NameError as ne:
        print(f"⚠️ בעיה עם המודל (לא נמצא): {ne}")
        summarizer_loaded = False  # מסמן שהמודל לא זמין
        return summarize_text(text, title)  # מנסה שוב לאחר אתחול

    except Exception as e:
        print(f"🔥 שגיאה בסיכום: {e}")
        torch.cuda.empty_cache()
        summarizer_loaded = False  # מסמן שהמודל לא זמין
        return ""


