from scrape.scrape_engine.source_ids import PUBLICATIONS
from scrape.scrape_engine.scraper import run_scraper
from database.database import insertInDB

def Scrap_SourceBase(page):
    """Main scraping function that handles all publications"""
    results = {}
    
    for pub_id in PUBLICATIONS:
        try:
            articles = run_scraper(pub_id, page)
            if articles:
                insertInDB(articles)
                results[pub_id] = len(articles)
            else:
                results[pub_id] = 0
        except Exception as e:
            print(f"❌ {pub_id} failed: {str(e)}")
            results[pub_id] = None
    
    # Print simple report
    print("\n=== Results ===")
    for pub_id, count in results.items():
        status = "✅" if count else "⚠️" if count == 0 else "❌"
        print(f"{status} {pub_id}: {count or 'No'} articles")
    
    return results