#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==================================================================================================
# config.py - Configuration and environment settings
# ==================================================================================================
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Set up logging first before it's used
def setup_logging():
    """Initialize the logging system with console and file handlers"""
    logger = logging.getLogger('news_aggregator')
    logger.setLevel(logging.INFO)
    
    # Create console handler with formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create file handler with rotation (10 MB per file, keep 5 backup files)
    file_handler = RotatingFileHandler('app.log', maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    
    # Create formatter and attach to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Initialize logger before using it
logger = setup_logging()

# Load environment variables
load_dotenv()

# Global constants
LOCK_FILE = "script_running.lock"
POSTED_NEWS_FILE = "posted_news_ud.json"

# Load RSS feed URLs from environment variables or a secure configuration file
RSS_FEED_URL = os.getenv("RSS_FEED_URL", "").split(",")
# Clean URLs by removing whitespace
RSS_FEED_URL = [url.strip() for url in RSS_FEED_URL if url.strip()]
if not RSS_FEED_URL:
    raise ValueError("RSS_FEED_URLS environment variable is not set or empty.")

# Log loaded RSS feeds for debugging
logger.info(f"Loaded {len(RSS_FEED_URL)} RSS feeds: {RSS_FEED_URL[:2]}...")

# Load country mappings from environment variables
RSS_COUNTRY_MAPPINGS = os.getenv("RSS_COUNTRY_MAPPINGS", "")
rss_country_map = {}

if RSS_COUNTRY_MAPPINGS:
    try:
        # Format should be "url1:country1,url2:country2"
        mapping_pairs = RSS_COUNTRY_MAPPINGS.split(",")
        for pair in mapping_pairs:
            if ":" in pair:
                url, country = pair.split(":", 1)
                rss_country_map[url.strip()] = country.strip()
        logger.info(f"Loaded {len(rss_country_map)} RSS country mappings")
    except Exception as e:
        logger.error(f"Error parsing RSS_COUNTRY_MAPPINGS: {e}")
else:
    logger.warning("Warning: RSS_COUNTRY_MAPPINGS not set in environment variables")

API_KEY = os.getenv("API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")

# Add validation after all environment variables are loaded
def validate_env_vars():
    """Validate all required environment variables"""
    required_vars = {
        "API_KEY": API_KEY,
        "SEARCH_ENGINE_ID": SEARCH_ENGINE_ID,
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
        "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
        "TEAMS_WEBHOOK_URL": TEAMS_WEBHOOK_URL
    }
    
    missing = [var for var, val in required_vars.items() if not val]
    
    if missing:
        logger.warning(f"Missing environment variables: {', '.join(missing)}")
        return False
    return True

# Call validation after loading environment variables
if not validate_env_vars():
    logger.warning("Some required environment variables are missing. Some features may not work properly.")