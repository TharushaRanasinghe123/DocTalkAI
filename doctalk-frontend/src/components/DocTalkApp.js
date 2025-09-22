import React, { useState, useEffect, useRef } from 'react';

// Enhanced Status Component with icons and animations
const StatusIndicator = ({ label, status, message, icon }) => {
  const getStatusConfig = (status) => {
    switch (status) {
      case 'connected': return {
        textClass: 'text-emerald-600 font-semibold',
        bgClass: 'bg-emerald-100',
        dotClass: 'bg-emerald-500 animate-pulse'
      };
      case 'disconnected': return {
        textClass: 'text-red-600 font-semibold',
        bgClass: 'bg-red-100',
        dotClass: 'bg-red-500'
      };
      case 'waiting': return {
        textClass: 'text-amber-600 font-semibold',
        bgClass: 'bg-amber-100',
        dotClass: 'bg-amber-500 animate-pulse'
      };
      default: return {
        textClass: 'text-slate-600',
        bgClass: 'bg-slate-100',
        dotClass: 'bg-slate-400'
      };
    }
  };

  const config = getStatusConfig(status);

  return (
    <div className={`flex items-center justify-between p-3 rounded-lg ${config.bgClass} transition-all duration-300`}>
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${config.dotClass}`}></div>
          <span className="font-medium text-slate-700">{icon} {label}</span>
        </div>
      </div>
      <span className={config.textClass}>{message}</span>
    </div>
  );
};

// Enhanced Transcript Display Component
const TranscriptDisplay = ({ interimText, userMessages, aiResponses, onClear }) => {
  const userBoxRef = useRef(null);
  const aiBoxRef = useRef(null);

  useEffect(() => {
    if (userBoxRef.current) {
      userBoxRef.current.scrollTop = userBoxRef.current.scrollHeight;
    }
  }, [userMessages, interimText]);

  useEffect(() => {
    if (aiBoxRef.current) {
      aiBoxRef.current.scrollTop = aiBoxRef.current.scrollHeight;
    }
  }, [aiResponses]);

  return (
    <div className="mt-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-slate-800 flex items-center space-x-2">
          <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
          <span>Live Conversation</span>
        </h2>
        <button 
          onClick={onClear}
          className="px-4 py-2 bg-slate-500 text-white rounded-lg hover:bg-slate-600 transition-colors duration-200 text-sm font-medium shadow-sm hover:shadow-md"
        >
          Clear Conversation
        </button>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Speech Box */}
        <div className="flex flex-col shadow-lg rounded-xl overflow-hidden border border-blue-200">
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-4 py-3">
            <h3 className="font-semibold text-white flex items-center space-x-2">
              <span>👤</span>
              <span>Your Speech</span>
            </h3>
          </div>
          <div 
            ref={userBoxRef}
            className="p-5 bg-blue-50/50 min-h-[280px] max-h-[350px] overflow-y-auto leading-relaxed"
          >
            {userMessages.length > 0 ? (
              userMessages.map((message, index) => (
                <div key={index} className="mb-3 p-3 text-slate-800 whitespace-pre-wrap text-sm bg-white rounded-lg shadow-sm border border-blue-100">
                  {message}
                </div>
              ))
            ) : (
              <div className="flex items-center justify-center h-full text-blue-400 italic text-center">
                <div>
                  <div className="text-3xl mb-2">🎤</div>
                  <div>Start speaking to see your words appear here...</div>
                </div>
              </div>
            )}
            {interimText && (
              <div className="mt-3 p-3 text-blue-600 italic opacity-80 text-sm bg-blue-100 rounded-lg border border-blue-200">
                {interimText}
              </div>
            )}
          </div>
        </div>

        {/* AI Response Box */}
        <div className="flex flex-col shadow-lg rounded-xl overflow-hidden border border-emerald-200">
          <div className="bg-gradient-to-r from-emerald-500 to-emerald-600 px-4 py-3">
            <h3 className="font-semibold text-white flex items-center space-x-2">
              <span>🤖</span>
              <span>AI Response</span>
            </h3>
          </div>
          <div 
            ref={aiBoxRef}
            className="p-5 bg-emerald-50/50 min-h-[280px] max-h-[350px] overflow-y-auto leading-relaxed"
          >
            {aiResponses.length > 0 ? (
              aiResponses.map((response, index) => (
                <div key={index} className="mb-3 p-3 text-slate-800 whitespace-pre-wrap text-sm bg-white rounded-lg shadow-sm border border-emerald-100">
                  {response}
                </div>
              ))
            ) : (
              <div className="flex items-center justify-center h-full text-emerald-400 italic text-center">
                <div>
                  <div className="text-3xl mb-2">💬</div>
                  <div>AI responses will appear here...</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
const DocTalkApp = () => {
  // State management
  const [isRecording, setIsRecording] = useState(false);
  const [interimText, setInterimText] = useState('');
  const [userMessages, setUserMessages] = useState([]);
  const [aiResponses, setAiResponses] = useState([]);
  const [backendStatus, setBackendStatus] = useState({ status: 'disconnected', message: 'Checking...' });
  const [websocketStatus, setWebsocketStatus] = useState({ status: 'disconnected', message: 'Disconnected' });
  const [microphoneStatus, setMicrophoneStatus] = useState({ status: 'disconnected', message: 'Not active' });
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);

  // Refs for audio handling
  const socketRef = useRef(null);
  const audioStreamRef = useRef(null);
  const audioContextRef = useRef(null);
  const processorRef = useRef(null);

  // Test backend connection
  const testBackendConnection = async () => {
    try {
      const response = await fetch('http://localhost:8001/health');
      
      if (response.ok) {
        setBackendStatus({ status: 'connected', message: 'Connected (Port 8001)' });
        return true;
      }
    } catch (error) {
      setBackendStatus({ status: 'disconnected', message: 'Not connected' });
    }
    return false;
  };

  // Convert Float32Array to Int16Array
  const convertFloat32ToInt16 = (float32Array) => {
    const int16Array = new Int16Array(float32Array.length);
    for (let i = 0; i < float32Array.length; i++) {
      const s = Math.max(-1, Math.min(1, float32Array[i]));
      int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return int16Array;
  };

  // Start recording function
  const startRecording = async () => {
    if (isRecording) return;

    setInterimText('');
    setUserMessages([]);
    setAiResponses([]);

    // Check backend connection first
    if (!await testBackendConnection()) {
      alert('Cannot connect to backend server. Please make sure it\'s running on port 8001.');
      return;
    }

    try {
      setMicrophoneStatus({ status: 'waiting', message: 'Requesting access...' });

      // Get microphone access
      audioStreamRef.current = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      });

      setMicrophoneStatus({ status: 'connected', message: 'Active' });

      // Set up WebSocket connection
      const wsUrl = "ws://localhost:8001/ws/transcribe";
      setWebsocketStatus({ status: 'waiting', message: 'Connecting...' });

      socketRef.current = new WebSocket(wsUrl);

      socketRef.current.onopen = () => {
        setWebsocketStatus({ status: 'connected', message: 'Connected' });
        setIsRecording(true);

        // Set up audio processing
        audioContextRef.current = new AudioContext({ sampleRate: 16000 });
        const source = audioContextRef.current.createMediaStreamSource(audioStreamRef.current);

        // Create a processor to handle audio data
        processorRef.current = audioContextRef.current.createScriptProcessor(4096, 1, 1);

        processorRef.current.onaudioprocess = (event) => {
          if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
            const inputData = event.inputBuffer.getChannelData(0);
            const int16Data = convertFloat32ToInt16(inputData);
            socketRef.current.send(int16Data.buffer);
          }
        };

        source.connect(processorRef.current);
        processorRef.current.connect(audioContextRef.current.destination);
      };

      socketRef.current.onmessage = async (event) => {
        if (event.data instanceof Blob) {
          // Audio data from ElevenLabs
          setIsPlayingAudio(true);
          const audioUrl = URL.createObjectURL(event.data);
          const audio = new Audio(audioUrl);
          
          audio.onended = () => {
            setIsPlayingAudio(false);
            URL.revokeObjectURL(audioUrl);
          };
          
          audio.onerror = () => {
            setIsPlayingAudio(false);
          };
          
          audio.play();
        } else {
          // Text data (intent/transcript)
          try {
            const data = JSON.parse(event.data);

            // Handle different message types
            switch(data.type) {
              case 'transcript':
                if (data.transcript) {
                  if (data.is_final) {
                    setUserMessages(prev => [...prev, data.transcript]);
                    setInterimText('');
                  } else {
                    setInterimText(data.transcript);
                  }
                }
                break;

              case 'intent':
                if (data.processed_response) {
                  setAiResponses(prev => [...prev, data.processed_response]);
                }
                break;

              case 'speech_start':
                setIsPlayingAudio(true);
                break;

              case 'speech_end':
                setIsPlayingAudio(false);
                break;

              default:
                break;
            }
          } catch (error) {
            // Handle error silently
          }
        }
      };

      socketRef.current.onerror = (error) => {
        setWebsocketStatus({ status: 'disconnected', message: 'Error' });
      };

      socketRef.current.onclose = () => {
        setWebsocketStatus({ status: 'disconnected', message: 'Disconnected' });
        if (isRecording) {
          stopRecording();
        }
      };

    } catch (error) {
      setMicrophoneStatus({ status: 'disconnected', message: 'Access denied' });
      alert('Error accessing microphone: ' + error.message);
    }
  };

  // Stop recording function
  const stopRecording = () => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: 'end_of_speech' }));
    }

    if (socketRef.current) {
      socketRef.current.close();
    }

    if (audioStreamRef.current) {
      audioStreamRef.current.getTracks().forEach(track => track.stop());
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
    }

    setIsRecording(false);
    setMicrophoneStatus({ status: 'disconnected', message: 'Not active' });
    setWebsocketStatus({ status: 'disconnected', message: 'Disconnected' });
    setInterimText('');
  };

  // Clear transcript
  const clearTranscript = () => {
    setInterimText('');
    setUserMessages([]);
    setAiResponses([]);
  };

  // Test backend connection on component mount
  useEffect(() => {
    testBackendConnection();

    // Cleanup on unmount
    return () => {
      if (isRecording) {
        stopRecording();
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-xl border border-white/20">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-3">
              DocTalk AI
            </h1>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Experience real-time voice conversations with AI. Click "Start Recording" and speak naturally - 
              the AI will respond with both text and voice.
            </p>
          </div>

          {/* Control Buttons */}
          <div className="flex justify-center space-x-4 mb-8">
            <button
              onClick={startRecording}
              disabled={isRecording}
              className={`px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg ${
                isRecording 
                  ? 'bg-slate-300 text-slate-500 cursor-not-allowed shadow-none transform-none' 
                  : 'bg-gradient-to-r from-emerald-500 to-green-500 text-white hover:from-emerald-600 hover:to-green-600 hover:shadow-xl'
              }`}
            >
              {isRecording ? '🎙️ Recording...' : '🚀 Start Recording'}
            </button>
            <button
              onClick={stopRecording}
              disabled={!isRecording}
              className={`px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg ${
                !isRecording 
                  ? 'bg-slate-300 text-slate-500 cursor-not-allowed shadow-none transform-none' 
                  : 'bg-gradient-to-r from-red-500 to-rose-500 text-white hover:from-red-600 hover:to-rose-600 hover:shadow-xl'
              }`}
            >
              🛑 Stop Recording
            </button>
          </div>

          {/* Transcript Display */}
          <TranscriptDisplay 
            interimText={interimText}
            userMessages={userMessages}
            aiResponses={aiResponses}
            onClear={clearTranscript}
          />
        </div>
      </div>
    </div>
  );
};

export default DocTalkApp;