from fastapi import APIRouter, Request, Query, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor
import time
import logging
from typing import List
from datetime import datetime, timedelta
from contextlib import contextmanager
from database.database import get_db_cursor
from routes.route_helper import (
    extract_keywords_cloud,
    process_trend_data
)
from database.database_helper import build_where_clause

router = APIRouter()
logger = logging.getLogger(__name__)

# Database Dependency
@contextmanager
def get_db() -> tuple[connection, cursor]:
    """
    Context manager for database connections
    """
    db = get_db_cursor()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    conn, cur = db
    try:
        yield conn, cur
    finally:
        cur.close()
        conn.close()

@router.get("/api/data")
async def get_data(
    request: Request,
    and_terms: List[str] = Query([], alias="and"),
    or_terms: List[str] = Query([], alias="or"),
    not_terms: List[str] = Query([], alias="not"),
    sources: List[str] = Query([], alias="sources")
):
    start_time = time.time()
    
    try:
        # Use the context manager directly in the route
        with get_db() as (conn, _):
            # Combine parameters
            params = {
                "and_keywords": request.query_params.getlist("and") or and_terms,
                "or_keywords": request.query_params.getlist("or") or or_terms,
                "not_keywords": request.query_params.getlist("not") or not_terms,
                "sources": request.query_params.getlist("sources") or sources
            }

            logger.info(f"Received params: {params}")

            # Empty results if no filters
            if not any(params["and_keywords"] + params["or_keywords"] + params["not_keywords"] + params["sources"]):
                return JSONResponse(content={
                    "success": True,
                    "articles": [],
                    "trend_data": [],
                    "top_publications": [],
                    "top_countries": [],
                    "wordcloud_data": [],
                    "total_articles": 0,
                    "processing_time": "0.00s",
                    "filter_applied": params
                })

            where_clause, query_params = build_where_clause(
                params["and_keywords"],
                params["or_keywords"],
                params["not_keywords"],
                params["sources"],
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # [Rest of your database queries...]
                cursor.execute(f"""
                    SELECT title, date, url, source_name, source_logo, country
                    FROM articles
                    WHERE {where_clause}
                    ORDER BY date DESC;
                """, query_params)
                articles = cursor.fetchall()

                # [Other queries...]

            # Process results
            trend_data = process_trend_data(all_dates)
            wordcloud_data = extract_keywords_cloud([a["title"] for a in articles])
            processing_time = time.time() - start_time

            return JSONResponse(content={
                "success": True,
                "articles": articles,
                "trend_data": trend_data,
                "top_publications": top_publications,
                "top_countries": top_countries,
                "wordcloud_data": wordcloud_data,
                "total_articles": len(articles),
                "processing_time": f"{processing_time:.2f}s",
                "filter_applied": params
            })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")