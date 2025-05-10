from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import io

from services.voice_service import VoiceService
from services.llm_service import LLMService # Assuming organize_dictated_text will be here

router = APIRouter(prefix="/api/voice", tags=["voice"])

voice_service = VoiceService()
llm_service = LLMService() # Or your OrganizationService

@router.post("/transcribe")
async def transcribe_audio_endpoint(audio_file: UploadFile = File(...)):
    """
    Receives an audio file, transcribes it, and returns the text.
    """
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid audio file type.")
    try:
        audio_data = await audio_file.read()
        transcribed_text = await voice_service.transcribe_audio(audio_data, audio_file.content_type)
        if transcribed_text is None:
            raise HTTPException(status_code=500, detail="Transcription failed.")
        return {"transcription": transcribed_text}
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=f"Error during transcription: {str(e)}")
    finally:
        await audio_file.close()

@router.post("/synthesize")
async def synthesize_speech_endpoint(text_payload: dict):
    """
    Receives text, synthesizes speech, and returns audio data.
    Frontend should send a JSON body like: {"text": "Hello world"}
    """
    text_to_synthesize = text_payload.get("text")
    if not text_to_synthesize:
        raise HTTPException(status_code=400, detail="No text provided for synthesis.")
    try:
        audio_data = await voice_service.synthesize_speech(text_to_synthesize)
        if audio_data is None:
            raise HTTPException(status_code=500, detail="Speech synthesis failed.")
        return StreamingResponse(io.BytesIO(audio_data), media_type="audio/mpeg")
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=f"Error during speech synthesis: {str(e)}")

@router.post("/organize_idea")
async def organize_idea_endpoint(text_payload: dict):
    """
    Receives transcribed text and returns a simple organized version.
    Frontend should send a JSON body like: {"text": "The protagonist finds a mysterious map."}
    """
    transcribed_text = text_payload.get("text")
    if not transcribed_text:
        raise HTTPException(status_code=400, detail="No text provided for organization.")
    try:
        # For MVP, llm_service might have the organization logic
        organized_data = await llm_service.organize_dictated_text(transcribed_text)
        if organized_data is None:
            raise HTTPException(status_code=500, detail="Idea organization failed.")
        return organized_data
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=f"Error during idea organization: {str(e)}") 