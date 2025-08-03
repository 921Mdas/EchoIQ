import logging
from playwright.sync_api import sync_playwright
from scrape.scrape_engine.ScrapSources import Scrap_SourceBase  
from fastapi import FastAPI, BackgroundTasks, HTTPException
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main_scraper():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            Scrap_SourceBase(page)
            browser.close()
        logger.info("✅ Scraping completed successfully")
    except Exception as e:
        logger.error(f"❌ Scraping failed: {str(e)}")
        raise
