import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urlparse
from helper import sources

def guess_selectors(soup):
    """Try to guess article, title, date, url selectors"""
    selectors = {
        "article": None,
        "title": None,
        "date": None,
        "url": None
    }

    # Guess article container
    if soup.find("article"):
        selectors["article"] = "article"
    elif soup.find("div", class_="post"):
        selectors["article"] = "div.post"
    elif soup.find("div", class_="what-cap"):
        selectors["article"] = "div.what-cap"

    # Guess title
    if soup.select_one("h1 a, h2 a, h3 a, h4 a"):
        selectors["title"] = "h1 a, h2 a, h3 a, h4 a"

    # Guess date
    if soup.find("time"):
        selectors["date"] = "time"
    elif soup.find("span", class_="date"):
        selectors["date"] = "span.date"
    elif soup.find("span"):
        selectors["date"] = "span"

    # URL is usually same as title
    selectors["url"] = selectors["title"]

    return selectors


def extract_metadata(soup, base_url):
    """Extract favicon, site name, description, language"""
    meta = {
        "source_name": soup.title.string.strip() if soup.title else urlparse(base_url).netloc,
        "source_logo": None,
        "source_url": base_url,
        "source_description": None,
        "source_language": soup.html.get("lang", "fr"),  # fallback French
        "source_favicon": None
    }

    # Meta description
    desc = soup.find("meta", attrs={"name": "description"})
    if desc:
        meta["source_description"] = desc.get("content")

    # OpenGraph description
    og_desc = soup.find("meta", property="og:description")
    if og_desc:
        meta["source_description"] = og_desc.get("content")

    # Logo (og:image as fallback)
    og_image = soup.find("meta", property="og:image")
    if og_image:
        meta["source_logo"] = og_image.get("content")

    # Favicon
    icon = soup.find("link", rel=lambda v: v and "icon" in v.lower())
    if icon:
        meta["source_favicon"] = icon.get("href")

    return meta


def generate_publication_config(source_id, base_url, country="Congo (DRC)"):
    print(f"🔎 Fetching {base_url} ...")
    r = requests.get(base_url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    selectors = guess_selectors(soup)
    meta = extract_metadata(soup, base_url)

    config = {
        "$schema": "../../publication_schema.json",
        "source_id": source_id,
        "config": {
            "base_url": base_url,
            "selectors": selectors,
            "required_selectors": [selectors["article"]],
            "timeout_ms": 60000
        },
        "meta": {
            "source_name": meta["source_name"],
            "country": country,
            "source_logo": meta["source_logo"],
            "source_url": base_url,
            "source_description": meta["source_description"],
            "source_type": "News",
            "source_language": meta["source_language"],
            "source_category": "General News",
            "source_tags": [country, "News"],
            "source_favicon": meta["source_favicon"],
            "source_country": country,
            "source_region": "Africa",
            "source_region_code": "AF",
            "source_language_code": meta["source_language"],
            "source_language_name": meta["source_language"],
            "source_language_native": meta["source_language"],
            "source_language_native_name": meta["source_language"],
            "language": meta["source_language"]
        }
    }

    return config


def save_config(config, continent_folder, country_folder):
    """
    Saves the config JSON into a folder structure: Continent/Country/source_id.json
    Creates folders if they don't exist.
    """
    folder = os.path.join(continent_folder, country_folder)
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, f"{config['source_id']}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {file_path}")



# Example run
if __name__ == "__main__":
    for src in sources:
        try:
            # Generate the publication config using source_id and url
            publication = generate_publication_config(src["source_id"], src["url"], country=src["Country"])

            # Save it into the folder structure using Continent and Country
            save_config(publication, continent_folder=src["Continent"], country_folder=src["Country"])

        except Exception as e:
            print(f"⚠️ Failed for {src['url']}: {e}")