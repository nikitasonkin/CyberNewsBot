# ==================================================================================================
# lock_manager.py - Functions for lock file management
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
from config import LOCK_FILE


#1
def create_lock():
    with open(LOCK_FILE, "w") as f:
        pid = os.getpid()
        f.write(str(pid))
    print(f"🔒 קובץ נעילה נוצר עם PID: {pid}")

#2
def remove_lock():
    """מוחק את קובץ הנעילה כשמסיימים את הריצה"""
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

#3
def is_script_running():
    if not os.path.exists(LOCK_FILE):
        return False

    try:
        with open(LOCK_FILE, "r") as f:
            pid = int(f.read().strip())
            if is_process_running(pid):
                print("⚠️ הסקריפט כבר רץ (PID: {})".format(pid))
                return True
            else:
                print("🧹 תהליך מת - מנקה קובץ נעילה ישן")
                remove_lock()
                return False
    except Exception as e:
        print(f"⚠️ שגיאה בקריאת קובץ נעילה: {e}")
        remove_lock()
        return False

#4
def is_process_running(pid):
    try:
        p = psutil.Process(pid)
        return p.is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
