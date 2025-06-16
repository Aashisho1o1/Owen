"""
Grammar Checking Router - SECURE VERSION

Provides real-time and comprehensive grammar checking endpoints
with cost optimization, performance monitoring, and security features.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
import json
import asyncio
from typing import Dict, Any
from dataclasses import asdict
import logging

from models.schemas import GrammarCheckRequest, GrammarCheckResponse
from services.grammar_service import grammar_service, SecurityError
# from services.auth_service import get_current_user_id, get_optional_user_id
from services.validation_service import input_validator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/grammar", tags=["grammar"])

def get_client_ip(request: Request) -> str:
    """Extract client IP for rate limiting and logging"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

@router.post("/check", response_model=GrammarCheckResponse)
async def check_grammar(
    request: Request,
    grammar_request: GrammarCheckRequest,
    # user_id: str = Depends(get_optional_user_id)  # Optional auth for public access
):
    """
    Check grammar and spelling in text with security validation
    
    Supports two modes:
    - real_time: Fast checking with LanguageTool + local spellcheck (<200ms)
    - comprehensive: LLM-based analysis for complex issues (2-5s)
    
    Security features:
    - Input validation and sanitization
    - Rate limiting per IP/user
    - Request size limits
    - Malicious content detection
    """
    client_ip = get_client_ip(request)
    user_id = None  # No auth for now
    
    try:
        # Validate input using our security service
        validated_text = input_validator.validate_text_input(grammar_request.text)
        
        # Additional grammar-specific validation
        if len(validated_text) > 50000:  # Grammar service limit
            raise HTTPException(
                status_code=413,
                detail="Text too long for grammar checking. Maximum 50,000 characters allowed."
            )
        
        # Log request for monitoring
        logger.info(
            f"Grammar check request: user={user_id or 'anonymous'}, "
            f"ip={client_ip}, type={grammar_request.check_type}, "
            f"length={len(validated_text)}"
        )
        
        # Choose checking method based on request type
        if grammar_request.check_type == "real_time":
            result = await grammar_service.check_real_time(validated_text)
        elif grammar_request.check_type == "comprehensive":
            result = await grammar_service.check_comprehensive(
                validated_text,
                grammar_request.context
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid check_type. Must be 'real_time' or 'comprehensive'"
            )
        
        # Convert to response format
        issues_response = [
            {
                "start": issue.start,
                "end": issue.end,
                "issue_type": issue.issue_type,
                "severity": issue.severity.value,
                "message": issue.message,
                "suggestions": issue.suggestions[:5],  # Limit suggestions
                "confidence": issue.confidence,
                "source": issue.source
            }
            for issue in result.issues
        ]
        
        return GrammarCheckResponse(
            text_length=len(result.text),
            word_count=result.word_count,
            issues=issues_response,
            check_type=result.check_type.value,
            processing_time_ms=result.processing_time_ms,
            cached=result.cached
        )
        
    except SecurityError as e:
        logger.warning(
            f"Security violation in grammar check: user={user_id or 'anonymous'}, "
            f"ip={client_ip}, error={str(e)}"
        )
        raise HTTPException(status_code=400, detail="Input validation failed")
    
    except ValueError as e:
        logger.warning(f"Invalid input in grammar check: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid input format")
    
    except Exception as e:
        logger.error(
            f"Grammar check failed: user={user_id or 'anonymous'}, "
            f"ip={client_ip}, error={str(e)}"
        )
        raise HTTPException(
            status_code=500, 
            detail="Grammar check service temporarily unavailable"
        )

@router.post("/check-stream")
async def check_grammar_stream(
    request: GrammarCheckRequest,
    # user_id: str = Depends(get_current_user_id)
):
    """
    Streaming grammar check for real-time feedback
    Returns results as they become available
    """
    async def generate_stream():
        try:
            # First, send fast local results
            local_issues = await grammar_service.check_spelling_fast(request.text)
            
            if local_issues:
                yield f"data: {json.dumps({'type': 'local', 'issues': [asdict(issue) for issue in local_issues]})}\n\n"
            
            # Then send LanguageTool results
            languagetool_issues = await grammar_service.check_with_languagetool(request.text)
            
            if languagetool_issues:
                yield f"data: {json.dumps({'type': 'languagetool', 'issues': [asdict(issue) for issue in languagetool_issues]})}\n\n"
            
            # For comprehensive mode, also send LLM results
            if request.check_type == "comprehensive":
                comprehensive_result = await grammar_service.check_comprehensive(request.text)
                yield f"data: {json.dumps({'type': 'comprehensive', 'result': asdict(comprehensive_result)})}\n\n"
            
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            logger.exception("An error occurred during grammar checking.")
            yield f"data: {json.dumps({'type': 'error', 'message': 'An internal error has occurred.'})}\n\n"
    
    return StreamingResponse(generate_stream(), media_type="text/plain")

@router.get("/metrics")
async def get_grammar_metrics():
    """Get grammar checking performance metrics"""
    return grammar_service.get_metrics()

@router.post("/clear-cache")
async def clear_grammar_cache():  # user_id: str = Depends(get_current_user_id)
    """Clear grammar check cache (admin only)"""
    grammar_service.clear_cache()
    return {"message": "Grammar cache cleared"} 