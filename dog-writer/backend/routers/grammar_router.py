"""
Grammar Checking Router

Provides real-time and comprehensive grammar checking endpoints
with cost optimization and performance monitoring.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import json
import asyncio
from typing import Dict, Any
from dataclasses import asdict

from models.schemas import GrammarCheckRequest, GrammarCheckResponse
from services.grammar_service import grammar_service
from services.auth_service import get_current_user_id
from services.validation_service import input_validator

router = APIRouter(prefix="/api/grammar", tags=["grammar"])

@router.post("/check", response_model=GrammarCheckResponse)
async def check_grammar(
    request: GrammarCheckRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Check grammar and spelling in text
    
    Supports two modes:
    - real_time: Fast checking with LanguageTool + local spellcheck (<200ms)
    - comprehensive: LLM-based analysis for complex issues (2-5s)
    """
    try:
        # Validate input
        validated_text = input_validator.validate_text_input(request.text)
        
        # Choose checking method
        if request.check_type == "real_time":
            result = await grammar_service.check_real_time(
                validated_text, 
                request.language
            )
        else:  # comprehensive
            result = await grammar_service.check_comprehensive(
                validated_text,
                request.context
            )
        
        # Convert to response format
        issues_response = [
            {
                "start": issue.start,
                "end": issue.end,
                "issue_type": issue.issue_type,
                "severity": issue.severity.value,
                "message": issue.message,
                "suggestions": issue.suggestions,
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grammar check failed: {str(e)}")

@router.post("/check-stream")
async def check_grammar_stream(
    request: GrammarCheckRequest,
    user_id: str = Depends(get_current_user_id)
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
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(generate_stream(), media_type="text/plain")

@router.get("/metrics")
async def get_grammar_metrics(user_id: str = Depends(get_current_user_id)):
    """Get grammar checking performance metrics"""
    return grammar_service.get_metrics()

@router.post("/clear-cache")
async def clear_grammar_cache(user_id: str = Depends(get_current_user_id)):
    """Clear grammar check cache (admin only)"""
    grammar_service.clear_cache()
    return {"message": "Grammar cache cleared"} 