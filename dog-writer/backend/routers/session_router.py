from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, Any

from models.schemas import (
    SessionStartRequest, SessionStartResponse,
    ActivityUpdateRequest, ActivityUpdateResponse,
    SessionEndRequest, SessionEndResponse,
    WeeklyAnalyticsRequest, WeeklyAnalyticsResponse,
    LiveSessionData, TimerPreferences,
    DailyStat
)
from services.database_service import db_service

router = APIRouter(
    prefix="/api/sessions",
    tags=["sessions"],
)

# Global session tracking for live updates
active_sessions: Dict[str, Dict[str, Any]] = {}

@router.post("/start", response_model=SessionStartResponse)
async def start_writing_session(request: SessionStartRequest):
    """
    Start a new writing session for productivity tracking.
    
    RATIONALE: Explicit session management enables precise analytics and
    proper handling of multiple tabs/windows. Each session represents
    a focused writing period with clear start/end boundaries.
    
    ALTERNATIVES:
    1. Implicit sessions (auto-start on first activity)
       - Pros: No user action needed
       - Cons: Unclear session boundaries, multiple sessions per tab
    
    2. Time-windowed sessions (new session after X minutes idle)
       - Pros: Automatic management
       - Cons: May split logical writing sessions
    
    CHOSEN APPROACH: Explicit start with implicit end
    - Users or frontend explicitly start sessions
    - Sessions auto-end after prolonged inactivity
    - Clear analytics boundaries
    """
    try:
        user_id = request.user_id or "default_user"
        
        # Start new session in database
        session_id = db_service.start_writing_session(user_id)
        
        if not session_id:
            raise HTTPException(status_code=500, detail="Failed to start writing session")
        
        # Initialize live session tracking
        active_sessions[session_id] = {
            "user_id": user_id,
            "start_time": datetime.now(),
            "last_activity": datetime.now(),
            "active_seconds": 0,
            "keystrokes": 0,
            "is_active": True,
            "focus_lost_intervals": []
        }
        
        return SessionStartResponse(
            session_id=session_id,
            success=True,
            message="Writing session started successfully"
        )
        
    except Exception as e:
        print(f"Error starting writing session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/activity", response_model=ActivityUpdateResponse)
async def update_session_activity(request: ActivityUpdateRequest):
    """
    Update session with new activity event.
    
    RATIONALE: Real-time activity tracking enables live timer updates
    and accurate productivity measurement. This endpoint is called
    frequently during active writing.
    
    ACTIVITY TYPES EXPLAINED:
    - 'typing': Active text input (keydown events)
    - 'editing': Text manipulation (delete, cut, paste, cursor movement)
    - 'scrolling': Content navigation (implies reading/reviewing)
    - 'thinking_pause': Detected pause still considered productive
    - 'focus_lost': Tab/window lost focus
    - 'focus_regained': Tab/window regained focus
    
    PERFORMANCE CONSIDERATIONS:
    - Called every few seconds during active writing
    - Minimal database writes (batch for performance)
    - In-memory session state for live updates
    """
    try:
        session_id = request.session_id
        
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[session_id]
        current_time = datetime.now()
        
        # Update session state based on activity type
        if request.activity_type in ['typing', 'editing', 'scrolling']:
            # These are "active" activities
            session["last_activity"] = current_time
            session["is_active"] = True
            
            if request.activity_type == 'typing':
                session["keystrokes"] += 1
        
        elif request.activity_type == 'thinking_pause':
            # Pause is still considered part of active writing
            session["is_active"] = True
        
        elif request.activity_type == 'focus_lost':
            session["is_active"] = False
            # Record when focus was lost for focus score calculation
            session["focus_lost_intervals"].append({
                "start": current_time.isoformat(),
                "type": "focus_lost"
            })
        
        elif request.activity_type == 'focus_regained':
            session["is_active"] = True
            # Close the last focus lost interval
            if session["focus_lost_intervals"]:
                last_interval = session["focus_lost_intervals"][-1]
                if "end" not in last_interval:
                    last_interval["end"] = current_time.isoformat()
                    lost_start = datetime.fromisoformat(last_interval["start"])
                    last_interval["duration"] = int((current_time - lost_start).total_seconds())
        
        # Update active time calculation
        if session["is_active"]:
            time_since_start = (current_time - session["start_time"]).total_seconds()
            session["active_seconds"] = int(time_since_start)
        
        # Periodically save to database (every 30 seconds to avoid overwhelming DB)
        last_save = session.get("last_db_save", session["start_time"])
        if (current_time - last_save).total_seconds() > 30:
            db_service.update_session_activity(
                session_id, 
                session["user_id"], 
                request.activity_type,
                request.content_length
            )
            session["last_db_save"] = current_time
        
        return ActivityUpdateResponse(
            success=True,
            message=f"Activity '{request.activity_type}' recorded"
        )
        
    except Exception as e:
        print(f"Error updating session activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/end", response_model=SessionEndResponse)
async def end_writing_session(request: SessionEndRequest):
    """
    End a writing session and calculate final statistics.
    
    RATIONALE: Session end triggers comprehensive analytics calculation
    and data persistence. This is when we compute focus scores, update
    daily statistics, and prepare data for weekly reports.
    
    FOCUS SCORE CALCULATION:
    Focus Score = (Total Active Time) / (Total Session Duration)
    
    This metric helps writers understand their concentration quality,
    similar to how fitness apps show "active minutes" vs "total workout time."
    
    WHY THIS MATTERS:
    - Writers can see their productivity patterns
    - Identifies optimal writing times
    - Motivates consistency without pressure
    - Enables meaningful self-reflection
    """
    try:
        session_id = request.session_id
        
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[session_id]
        
        # Close any open focus lost intervals
        for interval in session["focus_lost_intervals"]:
            if "end" not in interval:
                interval["end"] = datetime.now().isoformat()
                lost_start = datetime.fromisoformat(interval["start"])
                interval["duration"] = int((datetime.now() - lost_start).total_seconds())
        
        # Calculate final statistics
        total_active_seconds = request.total_active_seconds
        total_keystrokes = request.total_keystrokes or session["keystrokes"]
        total_words = request.total_words
        focus_lost_intervals = request.focus_lost_intervals or session["focus_lost_intervals"]
        
        # End session in database
        success = db_service.end_writing_session(
            session_id=session_id,
            total_active_seconds=total_active_seconds,
            total_keystrokes=total_keystrokes,
            total_words=total_words,
            focus_lost_intervals=focus_lost_intervals
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to end writing session")
        
        # Calculate session summary
        total_duration = int((datetime.now() - session["start_time"]).total_seconds())
        focus_score = (total_active_seconds / total_duration * 100) if total_duration > 0 else 0
        
        session_summary = {
            "session_id": session_id,
            "duration_minutes": total_duration // 60,
            "active_minutes": total_active_seconds // 60,
            "focus_score": round(focus_score, 1),
            "keystrokes": total_keystrokes,
            "words": total_words,
            "focus_lost_count": len(focus_lost_intervals)
        }
        
        # Clean up active session
        del active_sessions[session_id]
        
        return SessionEndResponse(
            success=True,
            session_summary=session_summary,
            message="Writing session completed successfully"
        )
        
    except Exception as e:
        print(f"Error ending writing session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/live/{session_id}", response_model=LiveSessionData)
async def get_live_session_data(session_id: str):
    """
    Get real-time session data for live timer display.
    
    RATIONALE: Frontend needs current session state for:
    - Live timer display (HH:MM:SS format)
    - Real-time focus score
    - Session status (active/paused)
    
    This endpoint is called every second by the frontend timer
    component when the timer is visible.
    
    PERFORMANCE: Very lightweight - just returns in-memory data.
    No database queries for maximum responsiveness.
    """
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[session_id]
        current_time = datetime.now()
        
        # Calculate current active seconds
        if session["is_active"]:
            time_since_start = (current_time - session["start_time"]).total_seconds()
            current_active_seconds = int(time_since_start)
        else:
            current_active_seconds = session["active_seconds"]
        
        # Calculate current focus score
        total_duration = (current_time - session["start_time"]).total_seconds()
        current_focus_score = (current_active_seconds / total_duration) if total_duration > 0 else 0
        
        return LiveSessionData(
            session_id=session_id,
            is_active=session["is_active"],
            current_active_seconds=current_active_seconds,
            session_start_time=session["start_time"].isoformat(),
            last_activity_time=session["last_activity"].isoformat(),
            current_focus_score=round(current_focus_score * 100, 1)
        )
        
    except Exception as e:
        print(f"Error getting live session data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/weekly", response_model=WeeklyAnalyticsResponse)
async def get_weekly_analytics(request: WeeklyAnalyticsRequest):
    """
    Generate comprehensive weekly writing analytics.
    
    RATIONALE: Weekly reports provide the perfect balance for productivity
    insights. They're detailed enough to be actionable but not so frequent
    as to become overwhelming.
    
    INSPIRED BY: iPhone Screen Time weekly reports
    - Clear metrics with context
    - Trend comparison with previous periods
    - Motivational insights and achievements
    - Focus on improvement, not judgment
    
    ANALYTICS PHILOSOPHY:
    1. Celebrate progress, however small
    2. Provide context for numbers (trends, comparisons)
    3. Offer actionable insights
    4. Maintain encouraging tone
    5. Focus on self-reflection, not external comparison
    """
    try:
        user_id = request.user_id or "default_user"
        week_offset = request.week_offset
        
        # Get analytics from database service
        analytics_data = db_service.get_weekly_analytics(user_id, week_offset)
        
        if not analytics_data:
            # Return empty analytics for new users
            return WeeklyAnalyticsResponse(
                week_start="",
                week_end="",
                total_minutes=0,
                total_hours=0.0,
                total_sessions=0,
                total_keystrokes=0,
                total_words=0,
                active_days=0,
                avg_daily_minutes=0.0,
                longest_session_minutes=0,
                avg_focus_score=0.0,
                most_productive_day=DailyStat(
                    date="", day_name="", active_minutes=0, sessions=0, focus_score=0.0
                ),
                trend_direction="stable",
                trend_percentage=0.0,
                daily_breakdown=[],
                insights=["🌟 Welcome to your writing journey! Start writing to see your analytics."],
                success=True
            )
        
        # Convert daily breakdown to DailyStat objects
        daily_breakdown = [
            DailyStat(
                date=day['date'],
                day_name=day['day_name'],
                active_minutes=day['active_minutes'],
                sessions=day['sessions'],
                focus_score=day['focus_score']
            )
            for day in analytics_data['daily_breakdown']
        ]
        
        most_productive_day_data = analytics_data['most_productive_day']
        most_productive_day = DailyStat(
            date=most_productive_day_data['date'],
            day_name=most_productive_day_data['day_name'],
            active_minutes=most_productive_day_data['active_minutes'],
            sessions=most_productive_day_data['sessions'],
            focus_score=most_productive_day_data['focus_score']
        )
        
        return WeeklyAnalyticsResponse(
            week_start=analytics_data['week_start'],
            week_end=analytics_data['week_end'],
            total_minutes=analytics_data['total_minutes'],
            total_hours=analytics_data['total_hours'],
            total_sessions=analytics_data['total_sessions'],
            total_keystrokes=analytics_data['total_keystrokes'],
            total_words=analytics_data['total_words'],
            active_days=analytics_data['active_days'],
            avg_daily_minutes=analytics_data['avg_daily_minutes'],
            longest_session_minutes=analytics_data['longest_session_minutes'],
            avg_focus_score=analytics_data['avg_focus_score'],
            most_productive_day=most_productive_day,
            trend_direction=analytics_data['trend_direction'],
            trend_percentage=analytics_data['trend_percentage'],
            daily_breakdown=daily_breakdown,
            insights=analytics_data['insights'],
            success=True
        )
        
    except Exception as e:
        print(f"Error generating weekly analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cleanup")
async def cleanup_inactive_sessions():
    """
    Clean up sessions that have been inactive for too long.
    
    RATIONALE: Prevents memory leaks from abandoned sessions
    (e.g., user closes browser without ending session).
    
    This endpoint can be called:
    1. Periodically by a cron job
    2. Before starting new sessions
    3. During maintenance operations
    
    TIMEOUT: Sessions inactive for 30+ minutes are considered abandoned.
    """
    try:
        current_time = datetime.now()
        session_timeout = 1800  # 30 minutes
        
        sessions_to_remove = []
        
        for session_id, session_data in active_sessions.items():
            time_since_activity = (current_time - session_data["last_activity"]).total_seconds()
            
            if time_since_activity > session_timeout:
                # Auto-end the session
                try:
                    db_service.end_writing_session(
                        session_id=session_id,
                        total_active_seconds=session_data["active_seconds"],
                        total_keystrokes=session_data["keystrokes"],
                        total_words=0,  # Unknown for auto-ended sessions
                        focus_lost_intervals=session_data["focus_lost_intervals"]
                    )
                    sessions_to_remove.append(session_id)
                except Exception as e:
                    print(f"Error auto-ending session {session_id}: {e}")
        
        # Remove cleaned up sessions
        for session_id in sessions_to_remove:
            del active_sessions[session_id]
        
        return {
            "success": True,
            "cleaned_sessions": len(sessions_to_remove),
            "message": f"Cleaned up {len(sessions_to_remove)} inactive sessions"
        }
        
    except Exception as e:
        print(f"Error cleaning up sessions: {e}")
        return {"success": False, "message": str(e)} 