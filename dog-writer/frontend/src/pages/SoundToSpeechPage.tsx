import React, { useState, useRef, useEffect } from 'react';
import { logger } from '../utils/logger';

// This component is now properly named SoundToSpeechPage
const SoundToSpeechPage: React.FC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const [wavePath, setWavePath] = useState("M0,50 Q30,40 60,50 T120,50 T180,50 T240,50 T300,50");

  // Animate the wave effect
  useEffect(() => {
    let animationId: number;
    let step = 0;

    const animateWave = () => {
      // Create smooth wave animation
      const newPath = `M0,50 Q30,${40 + Math.sin(step) * 8} 60,50 T${120 + Math.sin(step + 1) * 5},${50 + Math.cos(step) * 3} T${180 + Math.cos(step) * 4},${50 + Math.sin(step) * 4} T${240 + Math.sin(step + 2) * 6},50 T300,50`;
      setWavePath(newPath);
      step += 0.05;
      animationId = requestAnimationFrame(animateWave);
    };

    if (isRecording) {
      animateWave();
    } else {
      // Slower animation when not recording
      const intervalId = setInterval(() => {
        const newPath = `M0,50 Q30,${40 + Math.sin(step) * 5} 60,50 T${120 + Math.sin(step + 1) * 3},${50 + Math.cos(step) * 2} T${180 + Math.cos(step) * 3},${50 + Math.sin(step) * 3} T${240 + Math.sin(step + 2) * 4},50 T300,50`;
        setWavePath(newPath);
        step += 0.02;
      }, 50);
      
      return () => clearInterval(intervalId);
    }

    return () => {
      cancelAnimationFrame(animationId);
    };
  }, [isRecording]);

  // Start/stop recording logic
  const handleMicClick = async () => {
    if (!isRecording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorderRef.current = new window.MediaRecorder(stream);
        audioChunksRef.current = [];
        mediaRecorderRef.current.ondataavailable = (e) => {
          audioChunksRef.current.push(e.data);
        };
        mediaRecorderRef.current.start();
        setIsRecording(true);
      } catch (err) {
        logger.error("Error accessing microphone:", err);
        alert('Microphone access denied or not available.');
      }
    } else {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
    }
  };

  return (
    <div style={{
      width: '100vw',  // Use viewport width
      height: '100vh', // Use viewport height
      display: 'flex',
      position: 'fixed', // Fix position to viewport
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      overflow: 'hidden'
    }}>
      <div style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(180deg, var(--primary-dark) 0%, #4a5d97 100%)',
        position: 'relative',
        padding: '2rem',
        textAlign: 'center'
      }}>
        {/* Title */}
        <h1 style={{
          color: 'white',
          fontSize: '2.5rem',
          fontWeight: 600,
          marginBottom: '4rem',
          letterSpacing: '0.02em',
          textShadow: '0 2px 16px rgba(0,0,0,0.15)',
          zIndex: 10,
          position: 'relative'
        }}>Sound to Speech</h1>
        
        {/* Animated Wave Background */}
        <div style={{
          position: 'absolute',
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1
        }}>
          <svg 
            width="300" 
            height="100" 
            viewBox="0 0 300 100" 
            style={{
              opacity: isRecording ? 0.4 : 0.25,
              transition: 'opacity 0.5s',
              transform: 'scale(1.5)'
            }}
          >
            <path 
              d={wavePath} 
              stroke="white" 
              strokeWidth="2" 
              fill="none"
              strokeLinecap="round"
            />
          </svg>
        </div>
        
        {/* Microphone Button */}
        <button
          aria-label={isRecording ? 'Stop recording' : 'Start recording'}
          onClick={handleMicClick}
          style={{
            width: 140,
            height: 140,
            borderRadius: '50%',
            background: `linear-gradient(135deg, var(--accent-color) 0%, #36d6c9 100%)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: isRecording 
              ? '0 0 0 0 rgba(20, 184, 166, 0.5), 0 8px 32px rgba(0,0,0,0.25)' 
              : '0 8px 32px rgba(0,0,0,0.25)',
            border: 'none',
            outline: 'none',
            cursor: 'pointer',
            transition: 'box-shadow 0.2s, transform 0.2s',
            position: 'relative',
            zIndex: 10,
            animation: isRecording ? 'pulse 1.5s infinite' : 'none',
            transform: isRecording ? 'scale(1.05)' : 'scale(1)'
          }}
        >
          <svg 
            width="60" 
            height="100" 
            viewBox="0 0 64 64" 
            fill="none" 
            style={{
              filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.15))'
            }}
          >
            <rect x="24" y="12" width="16" height="32" rx="8" fill="white"/>
            <rect x="28" y="44" width="8" height="8" rx="4" fill="white"/>
            <rect x="20" y="52" width="24" height="4" rx="2" fill="white"/>
          </svg>
        </button>
        
        <div style={{
          marginTop: '3rem',
          color: 'rgba(255, 255, 255, 0.7)',
          fontSize: '0.95rem',
          maxWidth: '500px',
          lineHeight: '1.5',
          zIndex: 10
        }}>
          {isRecording ? 
            'Recording... Click the microphone to stop.' : 
            'Click the microphone button to start recording your voice.'}
        </div>
      </div>
      
      {/* CSS animations */}
      <style>{`
        @keyframes pulse {
          0% { box-shadow: 0 0 0 0 rgba(20, 184, 166, 0.6); }
          70% { box-shadow: 0 0 0 24px rgba(20, 184, 166, 0); }
          100% { box-shadow: 0 0 0 0 rgba(20, 184, 166, 0); }
        }
      `}</style>
    </div>
  );
};

export default SoundToSpeechPage; 