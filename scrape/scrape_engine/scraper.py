
import datetime
from typing import List, Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
from scrape.scrape_engine.scrape_helper import load_config
from scrape.scrape_engine.scrape_helper import process_article_date


logger = logging.getLogger(__name__)

#receives soure id and page object
## returns a list of articles with lenient date processing
## This scraper is designed to handle cases where the date might not be present or is in an unexpected format.
def run_scraper(source_id: str, page) -> List[Dict]:
    """Scrape articles with more lenient date processing"""
    try:
        config = load_config(source_id)
        base_url = config["config"]["base_url"]
        selectors = config["config"]["selectors"]
        
        # Fetch page
        page.goto(base_url, timeout=config["config"].get("timeout_ms", 60000))
        page.wait_for_selector(selectors["article"])
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        articles = []
        
        for article in soup.select(selectors["article"]):
            try:
                # Title
                title_tag = article.select_one(selectors["title"])
                if not title_tag:
                    logger.warning("Skipping article: missing title")
                    continue
                
                # URL
                url = urljoin(base_url, title_tag.get("href", "").strip())

                # Default to today's date unless we can extract
                date = datetime.datetime.now().strftime("%Y-%m-%d")

                # Try to extract the raw date safely
                date_selector = selectors.get("date", "")
                if date_selector:
                    date_element = article.select_one(date_selector)
                    raw_date = date_element.text.strip() if date_element else None

                    if raw_date:
                        try:
                            date = process_article_date(
                                url=url,
                                soup=article,
                                raw_date=raw_date,
                                publication_id=source_id
                            )
                        except Exception:
                            # Already defaulted above
                            logger.debug("Could not parse date, using today’s date.")

                articles.append({
                    "date": date,
                    "title": title_tag.text.strip(),
                    "url": url,
                    "source_name": config["meta"]["source_name"],
                    "country": config["meta"]["country"],
                    "source_logo": config["meta"].get("source_logo", "")
                })

            except Exception as e:
                logger.warning(f"Skipping article due to error: {str(e)}")
                continue
                
        return articles
        
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        return []
