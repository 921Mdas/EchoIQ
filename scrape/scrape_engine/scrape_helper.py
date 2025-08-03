
import os
import glob
import json
from typing import Dict
import logging

from datetime import datetime
import re
import dateparser



# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to load JSON config for a publication from any source_base country folder
def load_config(source_id: str) -> Dict:
    """Search recursively for JSON config in all continent folders under scrape/sourcebase_configs"""
    try:
        # 1. Define the root configs directory relative to project root
        configs_root = os.path.join("scrape", "sourcebase_configs")
        
        # Verify the root exists
        if not os.path.exists(configs_root):
            raise FileNotFoundError(f"Config root directory not found: {os.path.abspath(configs_root)}")

        # 2. Get list of all continent folders
        try:
            continents = [d for d in os.listdir(configs_root) 
                        if os.path.isdir(os.path.join(configs_root, d))]
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not list continent folders in {configs_root}")

        if not continents:
            raise FileNotFoundError(f"No continent folders found in {configs_root}")

        # 3. Search all continent folders recursively
        matches = []
        for continent in continents:
            search_path = os.path.join(configs_root, continent, "**", f"{source_id}.json")
            matches.extend(glob.glob(search_path, recursive=True))

        # 4. Case-insensitive fallback if no exact match found
        if not matches:
            logger.debug(f"No exact match for {source_id}.json, trying case-insensitive search...")
            for continent in continents:
                continent_path = os.path.join(configs_root, continent)
                for root, _, files in os.walk(continent_path):
                    for file in files:
                        if file.lower() == f"{source_id.lower()}.json":
                            matches.append(os.path.join(root, file))

        # 5. Handle results
        if not matches:
            available = []
            for continent in continents:
                continent_path = os.path.join(configs_root, continent)
                for root, _, files in os.walk(continent_path):
                    available.extend(f"{continent}/{os.path.relpath(root, os.path.join(configs_root, continent))}/{f}" 
                                  for f in files if f.endswith('.json'))
            
            error_msg = (f"No config found for source_id '{source_id}' in {configs_root}. "
                       f"Available configs:\n{chr(10).join(sorted(available))}")
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # 6. Load the first matching config
        config_path = matches[0]
        logger.info(f"Loading config for {source_id} from: {config_path}")
        
        with open(config_path, "r", encoding='utf-8') as f:
            config = json.load(f)

        # 7. Add metadata about the source
        path_parts = os.path.normpath(config_path).split(os.sep)
        continent_index = path_parts.index("sourcebase_configs") + 1
        config["_meta"] = {
            "loaded_from": config_path,
            "continent": path_parts[continent_index],
            "country": path_parts[continent_index + 1] if len(path_parts) > continent_index + 1 else None,
            "source_id": source_id
        }
        
        return config

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file {config_path}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Config load failed for {source_id}: {str(e)}", exc_info=True)
        raise
# Function to convert date string to datetime.date object
def convert_date(date_string):
    if isinstance(date_string, datetime):
        return date_string
    if not date_string or not isinstance(date_string, str):
        return None
    dt = dateparser.parse(date_string, languages=['fr'])
    return dt.date() if dt else None

# Function to process article date from URL or soup
def process_article_date(url=None, soup=None, raw_date=None, publication_id=None):
    try:
        if publication_id == 'sur7cd' and url:
            if '/20' in url:
                match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
                if match:
                    return f"{match[1]}-{match[2]}-{match[3]}"
        if soup:
            date_tag = (soup.select_one('span.date-display-single') or 
                       soup.select_one('span.submitted') or 
                       soup.select_one('time') or 
                       soup.select_one('span.color1') or 
                       soup.select_one('span.date'))
            if date_tag:
                raw_date = date_tag.get('content', date_tag.text.strip())
        if raw_date:
            return convert_date(raw_date)
        return datetime.now().isoformat()
    except Exception as e:
        logger.warning(f"Date processing failed: {str(e)}")
        return datetime.now().isoformat()