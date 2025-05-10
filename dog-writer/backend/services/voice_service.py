import os
from dotenv import load_dotenv
from google.cloud import speech
from elevenlabs.client import ElevenLabs

load_dotenv() # Loads environment variables from .env file

class VoiceService:
    def __init__(self):
        # Google Cloud Speech-to-Text client
        # Ensure GOOGLE_APPLICATION_CREDENTIALS environment variable is set
        # to the path of your Google Cloud service account key JSON file.
        self.speech_client = speech.SpeechClient()

        # ElevenLabs client
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.elevenlabs_api_key:
            print("Warning: ELEVENLABS_API_KEY not found in .env. TTS will not work.")
            self.elevenlabs_client = None
        else:
            self.elevenlabs_client = ElevenLabs(api_key=self.elevenlabs_api_key)

    async def transcribe_audio(self, audio_data: bytes, content_type: str = "audio/webm") -> str | None:
        """
        Transcribes audio data using Google Cloud Speech-to-Text.
        Adjust content_type based on what the frontend sends (e.g., audio/wav, audio/mp3, audio/webm).
        """
        try:
            audio = speech.RecognitionAudio(content=audio_data)
            
            # Determine encoding based on content_type
            # This is a simplified mapping; you might need a more robust one.
            encoding_map = {
                "audio/webm": speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                "audio/wav": speech.RecognitionConfig.AudioEncoding.LINEAR16,
                "audio/mp3": speech.RecognitionConfig.AudioEncoding.MP3,
                "audio/ogg": speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
                # Add other mappings as needed
            }
            encoding = encoding_map.get(content_type.split(';')[0], speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED)
            if encoding == speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED:
                print(f"Warning: Unsupported audio content type for transcription: {content_type}. Trying WEBM_OPUS.")
                encoding = speech.RecognitionConfig.AudioEncoding.WEBM_OPUS # Default or raise error

            config = speech.RecognitionConfig(
                encoding=encoding,
                # sample_rate_hertz=16000, # Required for LINEAR16 and FLAC, ensure frontend sends this if needed
                language_code="en-US",
                # enable_automatic_punctuation=True, # Optional
            )

            response = self.speech_client.recognize(config=config, audio=audio)

            if response.results and response.results[0].alternatives:
                return response.results[0].alternatives[0].transcript
            return ""
        except Exception as e:
            print(f"Error in Google STT: {e}")
            return None

    async def synthesize_speech(self, text: str) -> bytes | None:
        """
        Synthesizes speech from text using ElevenLabs.
        """
        if not self.elevenlabs_client:
            print("ElevenLabs client not initialized. Cannot synthesize speech.")
            return None
        try:
            # Example voice ID, replace with a desired voice from your ElevenLabs account
            # You can list available voices using: self.elevenlabs_client.voices.get_all()
            voice_id = "pNInz6obpgDQGcFmaJgB" # Example: Rachel
            
            audio_stream = self.elevenlabs_client.generate(
                text=text,
                voice=voice_id,
                model="eleven_multilingual_v2" # Or another suitable model
            )
            
            audio_bytes = b""
            for chunk in audio_stream:
                if chunk:
                    audio_bytes += chunk
            return audio_bytes

        except Exception as e:
            print(f"Error in ElevenLabs TTS: {e}")
            return None

# Example usage (for testing the service directly):
# if __name__ == "__main__":
#     import asyncio
#     async def test_transcription():
#         service = VoiceService()
#         # You'd need a sample audio file here (e.g., sample.wav)
#         # with open("path/to/your/sample.wav", "rb") as f:
#         #     audio_bytes = f.read()
#         # text = await service.transcribe_audio(audio_bytes, "audio/wav")
#         # print(f"Transcription: {text}")
#     async def test_synthesis():
#         service = VoiceService()
#         audio = await service.synthesize_speech("Hello from your AI writing assistant!")
#         if audio:
#             with open("synthesized_speech.mp3", "wb") as f:
#                 f.write(audio)
#             print("Speech synthesized to synthesized_speech.mp3")

#     # asyncio.run(test_transcription())
#     # asyncio.run(test_synthesis()) 