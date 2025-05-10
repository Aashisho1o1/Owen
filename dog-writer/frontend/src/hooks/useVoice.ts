import { useState, useCallback, useRef } from 'react';
import api from '../services/api'; // Assuming api.ts is in ../services/

interface OrganizedIdea {
  original_text?: string;
  summary?: string;
  category?: string;
  error?: string;
}

export const useVoice = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcription, setTranscription] = useState<string | null>(null);
  const [organizedIdea, setOrganizedIdea] = useState<OrganizedIdea | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);

  const startRecording = useCallback(async () => {
    if (isRecording) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        setIsLoading(true);
        setError(null);
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' }); // or audio/wav, ensure backend supports
        audioChunksRef.current = []; // Clear chunks for next recording
        
        // Stop all tracks on the stream to turn off the microphone light/indicator
        stream.getTracks().forEach(track => track.stop());

        try {
          const transcriptionResponse = await api.transcribeAudio(audioBlob);
          setTranscription(transcriptionResponse.transcription);

          if (transcriptionResponse.transcription) {
            const organizationResponse = await api.organizeIdea(transcriptionResponse.transcription);
            setOrganizedIdea(organizationResponse);
          } else {
            setOrganizedIdea(null); // No transcription to organize
          }
        } catch (e: any) {
          console.error("Error in transcription/organization process:", e);
          setError(e.message || 'Failed to process audio.');
          setTranscription(null);
          setOrganizedIdea(null);
        }
        setIsLoading(false);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setTranscription(null); // Clear previous transcription
      setOrganizedIdea(null); // Clear previous organized idea
      setError(null);
    } catch (err) {
      console.error("Error starting recording:", err);
      setError("Could not start recording. Please check microphone permissions.");
      setIsRecording(false);
    }
  }, [isRecording]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      // isLoading will be set to true in onstop handler
    }
  }, [isRecording]);

  const synthesizeAndPlayText = useCallback(async (textToSynthesize: string) => {
    if (isPlayingAudio) {
        if (audioPlayerRef.current) {
            audioPlayerRef.current.pause();
            audioPlayerRef.current.currentTime = 0;
        }
        setIsPlayingAudio(false);
        // If you want a toggle behavior, you might return here
        // or allow it to proceed to play the new text.
    }
    
    if (!textToSynthesize.trim()) {
        setError("Cannot play empty text.");
        return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const audioBlob = await api.synthesizeSpeech(textToSynthesize);
      if (audioBlob) {
        const audioUrl = URL.createObjectURL(audioBlob);
        if (audioPlayerRef.current) {
            audioPlayerRef.current.pause(); // Stop any current playback
        }
        audioPlayerRef.current = new Audio(audioUrl);
        audioPlayerRef.current.play();
        setIsPlayingAudio(true);
        audioPlayerRef.current.onended = () => {
          setIsPlayingAudio(false);
          URL.revokeObjectURL(audioUrl); // Clean up object URL
        };
        audioPlayerRef.current.onerror = (e) => {
            console.error("Audio playback error:", e);
            setError("Failed to play audio.");
            setIsPlayingAudio(false);
            URL.revokeObjectURL(audioUrl);
        };
      } else {
        setError("Speech synthesis failed to return audio.");
      }
    } catch (e: any) {
      console.error("Error synthesizing speech:", e);
      setError(e.message || 'Failed to synthesize speech.');
    }
    setIsLoading(false);
  }, [isPlayingAudio]);

  const stopAudioPlayback = useCallback(() => {
    if (audioPlayerRef.current && isPlayingAudio) {
        audioPlayerRef.current.pause();
        audioPlayerRef.current.currentTime = 0; // Reset to start
        setIsPlayingAudio(false);
        if (audioPlayerRef.current.src && audioPlayerRef.current.src.startsWith('blob:')){
            URL.revokeObjectURL(audioPlayerRef.current.src); // Clean up blob URL if it was from a blob
        }
    }
  }, [isPlayingAudio]);

  return {
    isRecording,
    transcription,
    organizedIdea,
    isLoading,
    error,
    startRecording,
    stopRecording,
    synthesizeAndPlayText,
    isPlayingAudio,
    stopAudioPlayback,
    clearError: () => setError(null),
    clearTranscription: () => { 
        setTranscription(null);
        setOrganizedIdea(null);
    }
  };
}; 