from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from database.database import get_db_cursor as get_db_connection
from database.database_helper import build_where_clause
from .route_helper import AIService
import logging

router = APIRouter()
ai_service = AIService()
logger = logging.getLogger(__name__)

@router.get("/api/summary")
async def get_articles_summary(request: Request):
    try:
        # 1. Convert query params to lists
        query_params = {
            "and": request.query_params.getlist("and"),
            "or": request.query_params.getlist("or"),
            "not": request.query_params.getlist("not"),
            "source": request.query_params.getlist("source")
        }

        if not any(query_params.values()):
            return JSONResponse(
                {"success": False, "error": "At least one query parameter is required"},
                status_code=400
            )

        # 2. Build database query
        where_clause, db_params = build_where_clause(
            query_params["and"],
            query_params["or"],
            query_params["not"],
            query_params["source"]
        )

        # 3. Fetch titles
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"SELECT title FROM articles WHERE {where_clause} ORDER BY date DESC LIMIT 20",
                    db_params
                )
                titles = [row[0] for row in cursor.fetchall()]

        # 4. Prepare base response
        response = {
            "success": True,
            "count": len(titles),
            "titles": titles[:5]
        }

        # 5. Generate summary if enough articles
        if len(titles) >= 3:
            try:
                response["summary"] = ai_service.summarize(tuple(titles[:15]))
            except Exception as e:
                logger.error(f"❌ Summary generation failed: {e}", exc_info=True)
                response["summary"] = "Summary generation failed"
                response["success"] = False

        return JSONResponse(response)

    except Exception as e:
        logger.error(f"🔥 Internal server error: {e}", exc_info=True)
        return JSONResponse(
            {"success": False, "error": "Internal server error"},
            status_code=500
        )
