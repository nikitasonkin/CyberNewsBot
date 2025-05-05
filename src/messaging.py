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
import psutil
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
    print(f"➡️ Sending Telegram message: {message[:40]}...")
    print(f"[BOT] {TELEGRAM_BOT_TOKEN[:10]}... | [CHAT_ID] {TELEGRAM_CHAT_ID}")

    clean_message = message.strip()
    clean_message_text = BeautifulSoup(clean_message, "html.parser").get_text().strip()

    if not clean_message_text:
        print("⚠️ Message is empty after cleaning. Skipping Telegram send.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": clean_message, "parse_mode": "HTML"}

    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            print("✅ Message sent successfully.")
            return  # Exit after successful sendציאה מהפונקציה לאחר הצלחה

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", delay))
                print(f"⏳ Received 429 Too Many Requests – retrying in {retry_after} seconds...")
                time.sleep(retry_after)  
            else:
                print(f"❌ Error sending message: {e} – Status code: {response.status_code}")
                break  

        except requests.exceptions.RequestException as e:
            print(f"❌ Telegram communication error: {e}")
            break  

    print("⚠️ Failed to send the message after multiple attempts.")


#2
def post_articles_to_telegram(articles):
    start_time = datetime.now()
    print(f"\n🚀 Starting to send articles: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    sent_articles = []
    skipped_articles = []
    skipped_news = load_skipped_news()
    current_posted = load_posted_news()

    posted_titles = set(clean_title_for_matching(item["title"]) for item in current_posted)
    posted_urls = set(clean_url(item["url"]) for item in current_posted)
    posted_hashes = set(item.get("text_hash") for item in current_posted if "text_hash" in item)

    processed_titles = set()
    processed_urls = set()
    processed_hashes = set()

    for index, article in enumerate(articles):
        article_id = article["id"]
        original_title = clean_title(article["title"]) or "🔹 Untitled Article"
        match_title = clean_title_for_matching(article["title"])
        clean_link = clean_url(article["url"])
        summary = article.get("summary", "")
        rss_source = article.get("rss_source", "Unknown")
        text_hash = article.get("text_hash")

        print(f"[CHECK] Title: {original_title} | URL: {clean_link}")


        if text_hash and (text_hash in posted_hashes or text_hash in processed_hashes):
            print(f"[DUPLICATE_HASH] Skipping by summary hash.")
            skipped_articles.append({
                "id": article_id,
                "title": original_title,
                "url": clean_link,
                "reason": "Duplicate by summary hash",
                "summary": summary,
                "text_hash": text_hash,
                "source": article.get("source", extract_source_from_url(clean_link)),
                "published_date": article.get("published_date", datetime.today().strftime("%Y-%m-%d")),
                "published_time": article.get("published_time", datetime.today().strftime("%H:%M:%S")),
                "rss_source": rss_source
            })
            continue

        if match_title in posted_titles or match_title in processed_titles:
            print(f"[DUPLICATE_TITLE] Skipping by title.")
            skipped_articles.append({
                "id": article_id,
                "title": original_title,
                "url": clean_link,
                "reason": "Duplicate by title",
                "summary": summary,
                "text_hash": text_hash or "",
                "source": article.get("source", extract_source_from_url(clean_link)),
                "published_date": article.get("published_date", datetime.today().strftime("%Y-%m-%d")),
                "published_time": article.get("published_time", datetime.today().strftime("%H:%M:%S")),
                "rss_source": rss_source
            })
            continue

        # בדיקת כפילות לפי URL
        if clean_link in posted_urls or clean_link in processed_urls:
            print(f"[DUPLICATE_URL] Skipping by url.")
            skipped_articles.append({
                "id": article_id,
                "title": original_title,
                "url": clean_link,
                "reason": "Duplicate by url",
                "summary": summary,
                "text_hash": text_hash or "",
                "source": article.get("source", extract_source_from_url(clean_link)),
                "published_date": article.get("published_date", datetime.today().strftime("%Y-%m-%d")),
                "published_time": article.get("published_time", datetime.today().strftime("%H:%M:%S")),
                "rss_source": rss_source
            })
            continue

        if article_id in skipped_news:
            fail_count = skipped_news[article_id].get("fail_count", 0)
            if fail_count >= 3:
                print(f"❌ The article '{original_title}' has failed too many times ({fail_count}) – skipping it.")
                continue

        if not text_hash and summary.strip():
            text_hash = compute_text_hash(summary)
            article["text_hash"] = text_hash
            print(f"[HASH] Recomputing hash from summary: {text_hash}")

        try:
            full_text = fetch_full_text(clean_link)
        except Exception as e:
            reason = f"Error while fetching article: {str(e)}"
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
            reason = "Article text is empty or too short"
            print(f"🚫 {reason} – skipped.")
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

        print(f"\n📨 Article {index + 1}/{len(articles)}: {original_title}")

        try:
            summarized_content = summarize_text(full_text, title=original_title)
        except Exception as e:
            reason = f"Error during summarization: {str(e)}"
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
            reason = "Final summary is too short or empty"
            print(f"🚫 {reason} – marking as failed.")
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

                print(f"✅ Sent and saved: {original_title}")
                break
            except requests.exceptions.RequestException as e:
                reason = f"Error sending to Telegram or Teams: {str(e)}"
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

    print("\n📋 Finished sending articles:")
    print(f"✅ Successfully sent: {len(sent_articles)}")
    print(f"⚠️ Skipped or failed: {len(skipped_articles)}")
    print(f"📊 Total summaries processed: {len(articles)}")
    print(f"⏱️ Duration: {datetime.now() - start_time}")



#3
def send_to_teams(message, webhook_url, retries=3, delay=5):
     """Sends a message to Microsoft Teams, with retry handling for HTTP 429 errors only."""
    try:
        headers = {"Content-Type": "application/json"}
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
                                "text": f"📅 Date: {message['date']}",
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
                                        "title": "🔗 Further reading",
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
                print(f"✅ Message successfully sent to Teams!")
                return
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", delay))
                    print(f"⏳ Received HTTP 429 – retrying in {retry_after} seconds...")
                    time.sleep(retry_after)
                else:
                    print(f"❌ Failed to send message to Teams: {e} - status: {response.status_code}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Communication error with Teams: {e}")
                break

        print("❌ Failed to send message to Teams after multiple attempts.")
    except Exception as e:
        print(f"⚠️ General error while sending to Teams: {e} {e}")
