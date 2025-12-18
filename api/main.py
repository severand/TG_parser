"""FastAPI REST API for TG Parser."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

from core.parser import Parser
from utils.validators import validate_keywords, validate_channel_url
from utils.exceptions import ValidationException, ParserException

app = FastAPI(
    title="TG Parser API",
    description="Telegram channel parser and search engine",
    version="1.0.0"
)

# Initialize parser
parser = Parser(max_workers=4)


class SearchRequest(BaseModel):
    """Search request model."""
    channels: List[str] = Field(..., description="List of channel usernames")
    keywords: List[str] = Field(..., description="List of keywords to search")
    max_messages: Optional[int] = Field(None, description="Max messages per channel")
    min_views: Optional[int] = Field(None, description="Minimum view count")
    date_from: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    with_urls: bool = Field(False, description="Only messages with URLs")


class SearchResponse(BaseModel):
    """Search response model."""
    success: bool
    total_results: int
    results: List[dict]
    statistics: dict
    error: Optional[str] = None


class ParseRequest(BaseModel):
    """Parse request model."""
    channels: List[str] = Field(..., description="List of channels")
    max_messages: Optional[int] = Field(None, description="Max messages per channel")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    parser_ready: bool


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        parser_ready=parser is not None
    )


@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search(request: SearchRequest):
    """Search channels for keywords."""
    try:
        # Validate input
        if not validate_keywords(request.keywords):
            raise HTTPException(status_code=400, detail="Invalid keywords")

        for channel in request.channels:
            if not validate_channel_url(channel):
                raise HTTPException(status_code=400, detail=f"Invalid channel: {channel}")

        # Parse and search
        result = parser.parse_and_search(
            channels=request.channels,
            keywords=request.keywords,
            max_messages=request.max_messages,
            min_views=request.min_views
        )

        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])

        return SearchResponse(
            success=True,
            total_results=len(result['search_results']),
            results=[
                {
                    'message_id': r.message_id,
                    'author': r.author,
                    'text': r.text_snippet,
                    'relevance': r.relevance_score,
                    'views': r.views
                }
                for r in result['search_results'][:100]
            ],
            statistics=result['statistics']
        )

    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ParserException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/parse", tags=["Parse"])
async def parse(request: ParseRequest):
    """Parse channels."""
    try:
        messages = parser.parse_channels(request.channels)
        return JSONResponse({
            "success": True,
            "total_messages": len(messages),
            "channels": request.channels
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", tags=["Statistics"])
async def get_statistics():
    """Get parser statistics."""
    return parser.get_statistics()


@app.post("/reset", tags=["System"])
async def reset():
    """Reset parser state."""
    parser.reset()
    return {"status": "reset", "success": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
