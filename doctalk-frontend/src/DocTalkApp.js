import React, { useState, useEffect, useRef } from 'react';

// Status Component
const StatusIndicator = ({ label, status, message }) => {
  const getStatusClass = (status) => {
    switch (status) {
      case 'connected': return 'text-green-600 font-bold';
      case 'disconnected': return 'text-red-600 font-bold';
      case 'waiting': return 'text-yellow-600 font-bold';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="flex items-center py-1">
      <strong className="mr-2">{label}:</strong>
      <span className={getStatusClass(status)}>{message}</span>
    </div>
  );
};

// Debug Log Component
const DebugLog = ({ logs }) => {
  const logRef = useRef(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="mt-4 p-3 bg-gray-100 rounded border">
      <strong className="block mb-2">Debug Log:</strong>
      <div 
        ref={logRef}
        className="font-mono text-xs max-h-24 overflow-y-auto"
        dangerouslySetInnerHTML={{ 
          __html: logs.map(log => `[${log.timestamp}] ${log.message}`).join('<br>')
        }}
      />
    </div>
  );
};

// Updated Transcript Display Component with separate boxes
const TranscriptDisplay = ({ interimText, userText, aiResponses, onClear }) => {
  const userBoxRef = useRef(null);
  const aiBoxRef = useRef(null);

  // Auto-scroll user box when new content is added
  useEffect(() => {
    if (userBoxRef.current) {
      userBoxRef.current.scrollTop = userBoxRef.current.scrollHeight;
    }
  }, [userText, interimText]);

  // Auto-scroll AI box when new content is added
  useEffect(() => {
    if (aiBoxRef.current) {
      aiBoxRef.current.scrollTop = aiBoxRef.current.scrollHeight;
    }
  }, [aiResponses]);

  return (
    <div className="mt-5">
      <div className="flex justify-between items-center mb-2">
        <strong>Live Conversation:</strong>
        <button 
          onClick={onClear}
          className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm"
        >
          Clear Conversation
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* User Speech Box */}
        <div className="flex flex-col">
          <div className="bg-blue-100 px-3 py-2 rounded-t border-b-2 border-blue-300">
            <strong className="text-blue-800">👤 Your Speech</strong>
          </div>
          <div 
            ref={userBoxRef}
            className="p-4 border-l border-r border-b border-blue-300 rounded-b min-h-[200px] max-h-[300px] overflow-y-auto bg-blue-50 leading-relaxed"
          >
            {userText && (
              <div className="text-blue-900 whitespace-pre-wrap">{userText}</div>
            )}
            {interimText && (
              <span className="text-blue-600 italic opacity-70">{interimText}</span>
            )}
            {!userText && !interimText && (
              <div className="text-blue-400 italic">Your speech will appear here...</div>
            )}
          </div>
        </div>

        {/* AI Response Box */}
        <div className="flex flex-col">
          <div className="bg-green-100 px-3 py-2 rounded-t border-b-2 border-green-300">
            <strong className="text-green-800">🤖 AI Response</strong>
          </div>
          <div 
            ref={aiBoxRef}
            className="p-4 border-l border-r border-b border-green-300 rounded-b min-h-[200px] max-h-[300px] overflow-y-auto bg-green-50 leading-relaxed"
          >
            {aiResponses.length > 0 ? (
              aiResponses.map((response, index) => (
                <div key={index} className="mb-2 text-green-900 whitespace-pre-wrap">
                  {response}
                </div>
              ))
            ) : (
              <div className="text-green-400 italic">AI responses will appear here...</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
const DocTalkApp = () => {
  // State management - Updated to separate user and AI text
  const [isRecording, setIsRecording] = useState(false);
  const [interimText, setInterimText] = useState('');
  const [userText, setUserText] = useState(''); // User speech only
  const [aiResponses, setAiResponses] = useState([]); // AI responses only
  const [backendStatus, setBackendStatus] = useState({ status: 'disconnected', message: 'Checking...' });
  const [websocketStatus, setWebsocketStatus] = useState({ status: 'disconnected', message: 'Disconnected' });
  const [microphoneStatus, setMicrophoneStatus] = useState({ status: 'disconnected', message: 'Not active' });
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [debugLogs, setDebugLogs] = useState([]);

  // Refs for audio handling
  const socketRef = useRef(null);
  const audioStreamRef = useRef(null);
  const audioContextRef = useRef(null);
  const processorRef = useRef(null);

  // Utility function to add debug logs
  const addDebugLog = (message) => {
    const timestamp = new Date().toLocaleTimeString();
    setDebugLogs(prev => [...prev, { timestamp, message }]);
  };

  // Test backend connection
  const testBackendConnection = async () => {
    try {
      addDebugLog('Testing backend connection...');
      const response = await fetch('http://localhost:8001/health');
      
      if (response.ok) {
        setBackendStatus({ status: 'connected', message: 'Connected (Port 8001)' });
        addDebugLog('✅ Backend server is running');
        return true;
      }
    } catch (error) {
      setBackendStatus({ status: 'disconnected', message: 'Not connected' });
      addDebugLog('❌ Cannot connect to backend: ' + error.message);
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
    setUserText('');
    setAiResponses([]);

    // Check backend connection first
    if (!await testBackendConnection()) {
      alert('Cannot connect to backend server. Please make sure it\'s running on port 8001.');
      return;
    }

    try {
      addDebugLog('Requesting microphone access...');
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
      addDebugLog('✅ Microphone access granted');

      // Set up WebSocket connection
      const wsUrl = "ws://localhost:8001/ws/transcribe";
      addDebugLog(`Connecting to WebSocket: ${wsUrl}`);
      setWebsocketStatus({ status: 'waiting', message: 'Connecting...' });

      socketRef.current = new WebSocket(wsUrl);

      socketRef.current.onopen = () => {
        addDebugLog('✅ WebSocket connected to backend');
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

        addDebugLog('🎤 Recording started - Speak into microphone');
      };

      socketRef.current.onmessage = async (event) => {
        if (event.data instanceof Blob) {
          // Audio data from ElevenLabs
          setIsPlayingAudio(true);
          const audioUrl = URL.createObjectURL(event.data);
          const audio = new Audio(audioUrl);
          
          audio.onended = () => {
            setIsPlayingAudio(false);
            URL.revokeObjectURL(audioUrl); // Clean up memory
          };
          
          audio.onerror = () => {
            setIsPlayingAudio(false);
            addDebugLog("❌ Error playing audio response");
          };
          
          audio.play();
          addDebugLog("🔊 Playing AI speech response");
        } else {
          // Text data (intent/transcript)
          try {
            const data = JSON.parse(event.data);
            addDebugLog(`Received: ${JSON.stringify(data)}`);

            // Handle different message types
            switch(data.type) {
              case 'transcript':
                if (data.transcript) {
                  if (data.is_final) {
                    // Add to user text instead of finalText
                    setUserText(prev => prev + data.transcript + ' ');
                    setInterimText('');
                    addDebugLog(`✅ Final: ${data.transcript}`);
                  } else {
                    setInterimText(data.transcript);
                    addDebugLog(`⏳ Interim: ${data.transcript}`);
                  }
                }
                break;

              case 'intent':
                addDebugLog(`🎯 Intent detected: ${data.intent} (${data.confidence})`);
                if (data.processed_response) {
                  // Add to AI responses instead of finalText
                  setAiResponses(prev => [...prev, data.processed_response]);
                }
                break;

              case 'speech_start':
                setIsPlayingAudio(true);
                addDebugLog("🎵 AI started speaking");
                break;

              case 'speech_end':
                setIsPlayingAudio(false);
                addDebugLog("✅ AI finished speaking");
                break;

              default:
                addDebugLog(`Unknown message type: ${data.type}`);
            }
          } catch (error) {
            addDebugLog('Error parsing WebSocket message: ' + error.message);
          }
        }
      };

      socketRef.current.onerror = (error) => {
        addDebugLog('❌ WebSocket error: ' + error.message);
        setWebsocketStatus({ status: 'disconnected', message: 'Error' });
      };

      socketRef.current.onclose = () => {
        addDebugLog('WebSocket connection closed');
        setWebsocketStatus({ status: 'disconnected', message: 'Disconnected' });
        if (isRecording) {
          stopRecording();
        }
      };

    } catch (error) {
      addDebugLog('❌ Error starting recording: ' + error.message);
      setMicrophoneStatus({ status: 'disconnected', message: 'Access denied' });
      alert('Error accessing microphone: ' + error.message);
    }
  };

  // Stop recording function
  const stopRecording = () => {
    addDebugLog('Stopping recording...');

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

    addDebugLog('Recording stopped');
  };

  // Clear transcript - Updated to clear both user and AI text
  const clearTranscript = () => {
    setInterimText('');
    setUserText('');
    setAiResponses([]);
    addDebugLog('Conversation cleared');
  };

  // Test backend connection on component mount
  useEffect(() => {
    addDebugLog('Page loaded');
    testBackendConnection();

    // Cleanup on unmount
    return () => {
      if (isRecording) {
        stopRecording();
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 py-5">
      <div className="max-w-6xl mx-auto px-5">
        <div className="bg-white p-5 rounded-lg shadow-md">
          <h1 className="text-2xl font-bold mb-4">DocTalk A1 - Real-Time Voice Conversation</h1>
          <p className="mb-5 text-gray-700">
            Click "Start Recording" and speak into your microphone. The AI will respond with both text and voice.
          </p>

          {/* Status Container */}
          <div className="mb-4 p-3 bg-gray-50 border border-gray-200 rounded">
            <StatusIndicator 
              label="Backend Server" 
              status={backendStatus.status} 
              message={backendStatus.message} 
            />
            <StatusIndicator 
              label="WebSocket" 
              status={websocketStatus.status} 
              message={websocketStatus.message} 
            />
            <StatusIndicator 
              label="Microphone" 
              status={microphoneStatus.status} 
              message={microphoneStatus.message} 
            />
            <StatusIndicator 
              label="AI Audio" 
              status={isPlayingAudio ? 'connected' : 'disconnected'} 
              message={isPlayingAudio ? 'Playing response...' : 'Silent'} 
            />
          </div>

          {/* Control Buttons */}
          <div className="mb-5">
            <button
              onClick={startRecording}
              disabled={isRecording}
              className={`px-4 py-2 mr-3 rounded text-white font-medium ${
                isRecording 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-green-500 hover:bg-green-600'
              }`}
            >
              Start Recording
            </button>
            <button
              onClick={stopRecording}
              disabled={!isRecording}
              className={`px-4 py-2 rounded text-white font-medium ${
                !isRecording 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-red-500 hover:bg-red-600'
              }`}
            >
              Stop Recording
            </button>
          </div>

          {/* Updated Transcript Display with separate boxes */}
          <TranscriptDisplay 
            interimText={interimText}
            userText={userText}
            aiResponses={aiResponses}
            onClear={clearTranscript}
          />

          {/* Debug Log */}
          <DebugLog logs={debugLogs} />
        </div>
      </div>
    </div>
  );
};

export default DocTalkApp;