# ==================================================================================================
# messaging.py - Functions for sending messages to Telegram and Teams
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
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TEAMS_WEBHOOK_URL
from json_handler import load_skipped_news, load_posted_news, save_posted_news, save_skipped_news
from text_processing import clean_title, clean_title_for_matching, clean_url, extract_source_from_url, compute_text_hash
from summarizer import summarize_text
from news_retrieval import fetch_full_text

#1
def send_telegram_message(message, retries=3, delay=5):
    print(f"➡️ שולח טלגרם עם הטקסט: {message[:40]}...")
    print(f"[BOT] {TELEGRAM_BOT_TOKEN[:10]}... | [CHAT_ID] {TELEGRAM_CHAT_ID}")

    """ שולח הודעה לטלגרם עם טיפול רק בשגיאת 429 והשהיה במקרה הצורך """

    clean_message = message.strip()
    clean_message_text = BeautifulSoup(clean_message, "html.parser").get_text().strip()

    if not clean_message_text:
        print(" ההודעה ריקה לאחר ניקוי, מדלג על שליחה לטלגרם.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": clean_message, "parse_mode": "HTML"}

    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            print(f"הודעה נשלחה בהצלחה.")
            return  # יציאה מהפונקציה לאחר הצלחה

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", delay))
                print(f"⏳ קיבלנו שגיאת 429 - מחכים {retry_after} שניות...")
                time.sleep(retry_after)  # השהיה לפי זמן שנשלח בהודעה
            else:
                print(f" שגיאה בשליחת הודעה: {e} - סטטוס: {response.status_code}")
                break  # במקרה של שגיאה שאינה 429, לא ננסה שוב

        except requests.exceptions.RequestException as e:
            print(f" שגיאת תקשורת בטלגרם: {e}")
            break  # במקרה של בעיות חיבור כלליות לא ננסה שוב

    print(" לא הצלחנו לשלוח את ההודעה לאחר מספר ניסיונות.")


#2
def post_articles_to_telegram(articles):
    start_time = datetime.now()
    print(f"\n🚀 התחלת שליחת כתבות: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    sent_articles = []
    skipped_articles = []
    skipped_news = load_skipped_news()
    current_posted = load_posted_news()

    posted_titles = set(item["title"] for item in current_posted)
    posted_urls = set(item["url"] for item in current_posted)
    posted_hashes = set(item.get("text_hash") for item in current_posted if "text_hash" in item)

    processed_titles = set()
    processed_urls = set()
    processed_hashes = set()

    for index, article in enumerate(articles):
        article_id = article["id"]
        original_title = clean_title(article["title"]) or "🔹 כתבה ללא כותרת"
        match_title = clean_title_for_matching(article["title"])
        clean_link = clean_url(article["url"])
        summary = article.get("summary", "")
        rss_source = article.get("rss_source", "Unknown")

        print(f"[CHECK] Title: {original_title} | URL: {clean_link}")

        if match_title in posted_titles or clean_link in posted_urls or \
           match_title in processed_titles or clean_link in processed_urls:
            print(f"[DUPLICATE] Skipping by title or URL.")
            skipped_articles.append({
                "id": article_id,
                "title": original_title,
                "url": clean_link,
                "reason": "כפילות לפי כותרת או URL",
                "summary": summary,
                "text_hash": article.get("text_hash", ""),
                "source": article.get("source", extract_source_from_url(clean_link)),
                "published_date": article.get("published_date", datetime.today().strftime("%Y-%m-%d")),
                "published_time": article.get("published_time", datetime.today().strftime("%H:%M:%S")),
                "rss_source": rss_source
            })
            continue

        if article_id in skipped_news:
            fail_count = skipped_news[article_id].get("fail_count", 0)
            if fail_count >= 3:
                print(f"❌ הכתבה '{original_title}' נכשלת יותר מדי פעמים ({fail_count}) – מדלג עליה.")
                continue

        text_hash = article.get("text_hash")
        if not text_hash and summary.strip():
            text_hash = compute_text_hash(summary)
            article["text_hash"] = text_hash
            print(f"[HASH] חושב מחדש hash מהתקציר: {text_hash}")

        try:
            full_text = fetch_full_text(clean_link)
        except Exception as e:
            reason = f"שגיאה בשליפת כתבה: {str(e)}"
            print(f"❌ {reason}")
            skipped_articles.append({
                "id": article_id,
                "title": original_title,
                "url": clean_link,
                "reason": reason,
                "summary": summary,
                "text_hash": text_hash or "",
                "source": article.get("source", extract_source_from_url(clean_link)),
                "published_date": article.get("published_date", datetime.today().strftime("%Y-%m-%d")),
                "published_time": article.get("published_time", datetime.today().strftime("%H:%M:%S")),
                "rss_source": rss_source
            })
            continue

        if not full_text or len(full_text.split()) < 10:
            reason = "טקסט מהכתבה קצר מדי או ריק"
            print(f"🚫 {reason} – דילוג.")
            skipped_articles.append({
                "id": article_id,
                "title": original_title,
                "url": clean_link,
                "reason": reason,
                "summary": summary,
                "text_hash": text_hash or "",
                "source": article.get("source", extract_source_from_url(clean_link)),
                "published_date": article.get("published_date", datetime.today().strftime("%Y-%m-%d")),
                "published_time": article.get("published_time", datetime.today().strftime("%H:%M:%S")),
                "rss_source": rss_source
            })
            continue

        if text_hash and (text_hash in posted_hashes or text_hash in processed_hashes):
            reason = "כפילות לפי hash של התקציר"
            print(f"[DUPLICATE_HASH] {reason} – דילוג.")
            skipped_articles.append({
                "id": article_id,
                "title": original_title,
                "url": clean_link,
                "reason": reason,
                "summary": summary,
                "text_hash": text_hash or "",
                "source": article.get("source", extract_source_from_url(clean_link)),
                "published_date": article.get("published_date", datetime.today().strftime("%Y-%m-%d")),
                "published_time": article.get("published_time", datetime.today().strftime("%H:%M:%S")),
                "rss_source": rss_source
            })
            continue

        processed_titles.add(match_title)
        processed_urls.add(clean_link)
        if text_hash:
            processed_hashes.add(text_hash)

        print(f"\n📨 כתבה {index + 1}/{len(articles)}: {original_title}")

        try:
            summarized_content = summarize_text(full_text, title=original_title)
        except Exception as e:
            reason = f"שגיאה בסיכום: {str(e)}"
            print(f"⚠️ {reason}")
            skipped_articles.append({
                "id": article_id,
                "title": original_title,
                "url": clean_link,
                "reason": reason,
                "summary": summary,
                "text_hash": text_hash or "",
                "source": article.get("source", extract_source_from_url(clean_link)),
                "published_date": article.get("published_date", datetime.today().strftime("%Y-%m-%d")),
                "published_time": article.get("published_time", datetime.today().strftime("%H:%M:%S")),
                "rss_source": rss_source
            })
            continue

        if not summarized_content.strip() or len(summarized_content.split()) < 20:
            reason = "התקציר הסופי קצר מדי או ריק"
            print(f"🚫 {reason} – מסמן ככשלון.")
            skipped_articles.append({
                "id": article_id,
                "title": original_title,
                "url": clean_link,
                "reason": reason,
                "summary": summary,
                "text_hash": text_hash or "",
                "source": article.get("source", extract_source_from_url(clean_link)),
                "published_date": article.get("published_date", datetime.today().strftime("%Y-%m-%d")),
                "published_time": article.get("published_time", datetime.today().strftime("%H:%M:%S")),
                "rss_source": rss_source
            })
            continue

        escaped_summary = html.escape(summarized_content.strip())
        message = f"""
📰 <b>{original_title}</b>
📅 <b>Date:</b> {article['published_date']} {article.get('published_time', '')}
🔗 <a href='{clean_link}'>For Additional Reading</a>

✍️ <b>Summary:</b>
{escaped_summary}
"""
        teams_message = {
            "title": original_title,
            "date": article['published_date'],
            "url": clean_link,
            "summary": escaped_summary
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                send_telegram_message(message)
                send_to_teams(teams_message, TEAMS_WEBHOOK_URL)

                enriched = {
                    "title": original_title,
                    "url": clean_link,
                    "text_hash": text_hash or "",
                    "summary": summarized_content.strip(),
                    "source": article.get("source", extract_source_from_url(clean_link)),
                    "keywords": article.get("keywords", []),
                    "published_date": article.get("published_date", datetime.today().strftime("%Y-%m-%d")),
                    "published_time": article.get("published_time", datetime.today().strftime("%H:%M:%S")),
                    "rss_source": rss_source
                }

                sent_articles.append(enriched)
                current_posted.append(enriched)
                save_posted_news(current_posted)

                print(f"✅ נשלחה ונשמרה: {original_title}")
                break
            except requests.exceptions.RequestException as e:
                reason = f"שגיאה בשליחה לטלגרם או Teams: {str(e)}"
                print(f"❌ {reason}")
                skipped_articles.append({
                    "id": article_id,
                    "title": original_title,
                    "url": clean_link,
                    "reason": reason,
                    "summary": summary,
                    "text_hash": text_hash or "",
                    "source": article.get("source", extract_source_from_url(clean_link)),
                    "published_date": article.get("published_date", datetime.today().strftime("%Y-%m-%d")),
                    "published_time": article.get("published_time", datetime.today().strftime("%H:%M:%S")),
                    "rss_source": rss_source
                })
                break

    if skipped_articles:
        save_skipped_news(skipped_articles)

    print("\n📋 סיום שליחת כתבות:")
    print(f"✅ נשלחו בהצלחה: {len(sent_articles)}")
    print(f"⚠️ דולגו או נכשלו: {len(skipped_articles)}")
    print(f"📊 סה״כ כתבות בטיפול: {len(articles)}")
    print(f"⏱️ משך זמן: {datetime.now() - start_time}")



#3
def send_to_teams(message, webhook_url, retries=3, delay=5):
    """ שולח הודעה ל-Microsoft Teams עם טיפול רק בשגיאת 429 """
    try:
        headers = {"Content-Type": "application/json"}

        # יצירת כרטיס אדפטיבי במבנה נכון עם כפתור
        adaptive_card = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "New Update",
                                "weight": "Bolder",
                                "size": "Medium",
                                "color": "Accent"
                            },
                            {
                                "type": "TextBlock",
                                "text": message['title'],
                                "wrap": True,
                                "weight": "Bolder",
                                "size": "Large"
                            },
                            {
                                "type": "TextBlock",
                                "text": f"📅 תאריך: {message['date']}",
                                "wrap": True
                            },
                            {
                                "type": "TextBlock",
                                "text": f" {message['summary']}",
                                "wrap": True,
                                "separator": True
                            },
                            {
                                "type": "ActionSet",
                                "actions": [
                                    {
                                        "type": "Action.OpenUrl",
                                        "title": "🔗 קריאה נוספת",
                                        "url": message['url']
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }

        for attempt in range(retries):
            try:
                response = requests.post(webhook_url, headers=headers, json=adaptive_card)
                response.raise_for_status()
                print(f"✅ הודעה נשלחה בהצלחה לערוץ Teams!")
                return
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", delay))
                    print(f"⏳ קיבלנו שגיאת 429 - מחכים {retry_after} שניות...")
                    time.sleep(retry_after)
                else:
                    print(f"❌ שגיאה בשליחת הודעה ל-Teams: {e} - סטטוס: {response.status_code}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"⚠️ שגיאת תקשורת בערוץ Teams: {e}")
                break

        print("❌ לא הצלחנו לשלוח את ההודעה ל-Teams לאחר מספר ניסיונות.")
    except Exception as e:
        print(f"⚠️ שגיאה כללית בשליחה ל-Teams: {e}")