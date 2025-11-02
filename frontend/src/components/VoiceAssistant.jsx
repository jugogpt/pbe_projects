import React, { useState, useEffect, useRef } from 'react';
import API from '../services/api';

function VoiceAssistant() {
    const [isRecording, setIsRecording] = useState(false);
    const [currentTranscript, setCurrentTranscript] = useState('');
    const [fullTranscript, setFullTranscript] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [audioLevel, setAudioLevel] = useState(0);
    const [connectionStatus, setConnectionStatus] = useState('disconnected');
    const [microphoneName, setMicrophoneName] = useState('');
    const [workflow, setWorkflow] = useState(null);
    const [workflowProgress, setWorkflowProgress] = useState(null);
    const [renderTrigger, setRenderTrigger] = useState(0);
    const audioIntervalRef = useRef(null);
    const wsConnectionRef = useRef(null);

    // Force re-render on audio level changes for smooth animation
    useEffect(() => {
        if (isRecording && audioLevel > 0) {
            const interval = setInterval(() => {
                setRenderTrigger(prev => prev + 1);
            }, 100); // Update every 100ms for smooth animation

            return () => clearInterval(interval);
        }
    }, [isRecording, audioLevel]);

    // Update connection status when recording starts/stops
    useEffect(() => {
        if (isRecording) {
            setConnectionStatus('connected');
        } else {
            setAudioLevel(0);
            setConnectionStatus('disconnected');
        }
    }, [isRecording]);

    useEffect(() => {
        // Set up WebSocket listener for real-time voice transcript updates
        const handleMessage = (data) => {
            console.log('WebSocket message received:', data);
            setConnectionStatus('receiving');

            switch (data.type) {
                case 'partial_transcript':
                    // Update partial transcript for smooth display
                    const partialText = data.data.text;
                    if (partialText) {
                        setCurrentTranscript(partialText);
                        setIsProcessing(true);
                        setConnectionStatus('transcribing');
                    }
                    break;

                case 'word_detected':
                    // Handle individual word updates for smooth, fast, animated display
                    const word = data.data.word;
                    if (word) {
                        setCurrentTranscript(prev => {
                            // Add word smoothly without duplicates
                            if (!prev || !prev.endsWith(word)) {
                                return prev ? prev + ' ' + word : word;
                            }
                            return prev;
                        });
                        setIsProcessing(true);
                        setConnectionStatus('transcribing');
                    }
                    break;

                case 'final_transcript':
                    console.log('Final transcript:', data.data.text);
                    const finalText = data.data.text;
                    if (finalText) {
                        // Add to full transcript history with spacing
                        setFullTranscript(prev => {
                            if (prev) {
                                return prev + ' ' + finalText.trim();
                            }
                            return finalText.trim();
                        });

                        // Clear current transcript
                        setCurrentTranscript('');
                        setIsProcessing(false);
                        setConnectionStatus('processed');
                        setTimeout(() => setConnectionStatus('connected'), 500);
                    }
                    break;

                case 'workflow_progress':
                    console.log('Workflow progress:', data.data);
                    setWorkflowProgress(data.data);
                    break;

                case 'workflow_generated':
                    console.log('Workflow generated:', data.data);
                    setWorkflow(data.data.workflow);
                    setWorkflowProgress(null); // Clear progress indicator
                    break;

                case 'recording_started':
                    console.log('Recording started');
                    setCurrentTranscript('');
                    setIsProcessing(false);
                    setConnectionStatus('connected');
                    break;

                case 'recording_stopped':
                    console.log('Recording stopped');
                    setIsProcessing(false);
                    setConnectionStatus('stopped');
                    break;

                case 'audio_level':
                    // Update audio level from real audio input
                    const level = data.data.level;
                    setAudioLevel(level);
                    break;

                case 'device_info':
                    // Update microphone device name
                    const deviceName = data.data.device_name;
                    console.log('Microphone device:', deviceName);
                    setMicrophoneName(deviceName);
                    break;

                default:
                    console.log('Unknown message type:', data.type);
            }
        };

        wsConnectionRef.current = API.connectWebSocket(handleMessage);

        return () => {
            // Cleanup if needed
        };
    }, []);

    const handleStartVoice = async () => {
        if (isRecording) return; // Prevent double-starting

        try {
            console.log('Starting voice recording...');
            setConnectionStatus('connecting');

            const response = await API.startVoice();
            console.log('Voice recording started:', response.data);
            setIsRecording(true);
            setCurrentTranscript(''); // Clear previous transcript
        } catch (error) {
            console.error('Error starting voice:', error);

            let errorMessage = 'Failed to start voice recording. ';

            if (error.message && error.message.includes('Network Error')) {
                errorMessage += 'Backend server is not responding. Please ensure the backend is running on http://127.0.0.1:5000';
            } else if (error.response) {
                errorMessage += error.response.data?.detail || 'Unknown server error';
            } else {
                errorMessage += error.message || 'Unknown error';
            }

            setIsRecording(false);
            setConnectionStatus('error');
        }
    };

    const handleStopVoice = async () => {
        try {
            console.log('Stopping voice recording...');
            const response = await API.stopVoice();
            console.log('Voice recording stopped:', response.data);
            setIsRecording(false);
            setConnectionStatus('stopped');
        } catch (error) {
            console.error('Error stopping voice:', error);
        }
    };

    // Generate audio wave visualization bars based on real audio levels
    const generateAudioBars = () => {
        const bars = [];
        const numBars = 40;
        const maxHeight = 50;
        const currentTime = Date.now();

        for (let i = 0; i < numBars; i++) {
            // Create fluid wave pattern that responds to actual audio level
            const delay = i * 30; // Faster wave animation
            const frequency = 3; // Higher wave frequency for more movement
            const offset = Math.sin((i / numBars) * Math.PI * frequency + currentTime / 100) * 0.5;

            // Base height on real audio level with more dynamic response
            // When speaking loudly, audioLevel is high (close to 1)
            // When quiet/not speaking, audioLevel is low (close to 0)
            const baseHeight = audioLevel * 0.9 + 0.05; // Scale from 0.05 to 0.95 for more range
            const height = isRecording
                ? (baseHeight + offset) * maxHeight
                : 8 + Math.sin((i / numBars) * Math.PI * 4 + currentTime / 200) * 2; // Gentle wave when idle

            // Color intensity based on audio level
            const intensity = isRecording ? Math.max(0.3, audioLevel) : 0.3;
            const color = isRecording && audioLevel > 0.05
                ? `rgba(107, 158, 255, ${0.3 + intensity * 0.7})`
                : 'rgba(100, 120, 160, 0.3)';

            bars.push(
                <div
                    key={i}
                    style={{
                        width: '3px',
                        height: `${Math.max(height, 3)}px`,
                        background: color,
                        margin: '0 1px',
                        borderRadius: '2px',
                        transition: isRecording ? 'height 0.08s ease-out, background 0.1s ease-out' : 'all 0.5s ease',
                        animationDelay: `${delay}ms`,
                        boxShadow: isRecording && audioLevel > 0.2
                            ? `0 0 ${3 * audioLevel}px rgba(107, 158, 255, ${audioLevel * 0.5})`
                            : 'none'
                    }}
                />
            );
        }

        return bars;
    };

    return (
        <div className="panel voice-panel">
            <h2>Voice Assistant</h2>

            <div className="voice-controls">
                <button
                    className={isRecording ? 'recording-active' : ''}
                    onClick={isRecording ? handleStopVoice : handleStartVoice}
                    disabled={connectionStatus === 'connecting' || connectionStatus === 'connecting'}
                >
                    {isRecording ? 'Stop Recording' : 'Start Recording'}
                </button>

                {/* Connection Status Indicator */}
                <div style={{
                    marginTop: '10px',
                    fontSize: '12px',
                    color: connectionStatus === 'connected' || connectionStatus === 'transcribing' ? '#6B9EFF' :
                        connectionStatus === 'error' ? '#e74c3c' : '#b0b0b0',
                    fontFamily: 'Alan Sans, sans-serif'
                }}>
                    Status: {connectionStatus}
                </div>

                {/* Microphone Device Indicator */}
                {isRecording && microphoneName && (
                    <div style={{
                        marginTop: '10px',
                        padding: '8px 12px',
                        background: '#1a1f2e',
                        border: '1px solid rgba(100, 100, 120, 0.3)',
                        borderRadius: '6px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                    }}>
                        <div style={{
                            width: '10px',
                            height: '10px',
                            background: '#6B9EFF',
                            borderRadius: '50%',
                            animation: 'pulse 2s infinite'
                        }}></div>
                        <span style={{
                            fontSize: '11px',
                            color: '#e0e0e0',
                            fontFamily: 'Alan Sans, sans-serif',
                            fontWeight: '500'
                        }}>
                            Microphone: {microphoneName}
                        </span>
                    </div>
                )}
            </div>

            {/* Audio Visualization */}
            {isRecording && (
                <div style={{
                    background: '#1a1f2e',
                    border: '1px solid rgba(100, 100, 120, 0.3)',
                    borderRadius: '8px',
                    padding: '20px',
                    marginBottom: '20px',
                    minHeight: '80px',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center'
                }}>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        height: '60px',
                        gap: '2px'
                    }}>
                        {generateAudioBars()}
                    </div>
                </div>
            )}

            {/* Full Transcript Display */}
            {fullTranscript && (
                <div style={{
                    background: '#1a1f2e',
                    border: '1px solid rgba(100, 100, 120, 0.3)',
                    borderRadius: '8px',
                    padding: '16px',
                    marginBottom: '20px',
                    maxHeight: '200px',
                    overflowY: 'auto'
                }}>
                    <h3 style={{
                        fontSize: '16px',
                        fontWeight: '600',
                        color: '#6B9EFF',
                        marginBottom: '12px',
                        fontFamily: 'Alan Sans, sans-serif'
                    }}>Full Transcript</h3>
                    <p style={{
                        color: '#d0d0d0',
                        fontSize: '14px',
                        lineHeight: '1.6',
                        fontFamily: 'Alan Sans, sans-serif',
                        whiteSpace: 'pre-wrap',
                        margin: 0
                    }}>
                        {fullTranscript}
                    </p>
                </div>
            )}

            {/* Workflow Generation Progress */}
            {workflowProgress && (
                <div style={{
                    background: 'linear-gradient(135deg, #1a1f2e 0%, #252a3a 100%)',
                    border: '2px solid #6B9EFF',
                    borderRadius: '8px',
                    padding: '20px',
                    marginBottom: '20px',
                    boxShadow: '0 4px 12px rgba(107, 158, 255, 0.2)'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                        <div style={{
                            width: '20px',
                            height: '20px',
                            border: '3px solid rgba(107, 158, 255, 0.3)',
                            borderTopColor: '#6B9EFF',
                            borderRadius: '50%',
                            animation: 'spin 0.8s linear infinite'
                        }}></div>
                        <h3 style={{
                            fontSize: '18px',
                            fontWeight: '700',
                            color: '#6B9EFF',
                            margin: 0,
                            fontFamily: 'Alan Sans, sans-serif'
                        }}>Generating Workflow...</h3>
                    </div>

                    <div style={{
                        background: 'rgba(0, 0, 0, 0.3)',
                        borderRadius: '4px',
                        padding: '8px 12px',
                        fontSize: '14px',
                        color: '#b0b0b0',
                        fontFamily: 'Alan Sans, sans-serif'
                    }}>
                        {workflowProgress.message}
                    </div>

                    {/* Progress Bar */}
                    <div style={{
                        marginTop: '12px',
                        height: '4px',
                        background: 'rgba(107, 158, 255, 0.1)',
                        borderRadius: '2px',
                        overflow: 'hidden'
                    }}>
                        <div style={{
                            height: '100%',
                            width: workflowProgress.stage === 'starting' ? '20%' :
                                workflowProgress.stage === 'processing' ? '60%' :
                                    workflowProgress.stage === 'formatting' ? '80%' : '100%',
                            background: 'linear-gradient(90deg, #6B9EFF, #8FAEFF)',
                            transition: 'width 0.3s ease',
                            animation: workflowProgress.stage !== 'completed' && workflowProgress.stage !== 'error' ? 'pulse 1.5s ease-in-out infinite' : 'none'
                        }}></div>
                    </div>

                    <style>{`
                        @keyframes spin {
                            to { transform: rotate(360deg); }
                        }
                        @keyframes pulse {
                            0%, 100% { opacity: 1; }
                            50% { opacity: 0.6; }
                        }
                    `}</style>
                </div>
            )}

            {/* Generated Workflow Display */}
            {workflow && (
                <div style={{
                    background: '#1a1f2e',
                    border: '2px solid #6B9EFF',
                    borderRadius: '8px',
                    padding: '20px',
                    marginBottom: '20px'
                }}>
                    <h3 style={{
                        fontSize: '18px',
                        fontWeight: '700',
                        color: '#6B9EFF',
                        marginBottom: '16px',
                        fontFamily: 'Alan Sans, sans-serif'
                    }}>Generated Workflow</h3>

                    <div style={{
                        marginBottom: '16px'
                    }}>
                        <h4 style={{
                            fontSize: '16px',
                            fontWeight: '600',
                            color: '#e0e0e0',
                            marginBottom: '8px',
                            fontFamily: 'Alan Sans, sans-serif'
                        }}>{workflow.title || 'Untitled Workflow'}</h4>
                        <p style={{
                            color: '#b0b0b0',
                            fontSize: '14px',
                            marginBottom: '8px',
                            fontFamily: 'Alan Sans, sans-serif'
                        }}>
                            {workflow.description || 'No description available'}
                        </p>
                    </div>

                    {workflow.steps && workflow.steps.length > 0 && (
                        <div>
                            <h5 style={{
                                fontSize: '14px',
                                fontWeight: '600',
                                color: '#6B9EFF',
                                marginBottom: '12px',
                                fontFamily: 'Alan Sans, sans-serif'
                            }}>Steps:</h5>
                            {workflow.steps.map((step, idx) => (
                                <div key={idx} style={{
                                    background: '#0f1520',
                                    borderRadius: '6px',
                                    padding: '12px',
                                    marginBottom: '8px',
                                    border: '1px solid rgba(100, 100, 120, 0.3)'
                                }}>
                                    <div style={{
                                        display: 'flex',
                                        alignItems: 'start',
                                        gap: '12px'
                                    }}>
                                        <div style={{
                                            background: '#6B9EFF',
                                            color: '#ffffff',
                                            width: '24px',
                                            height: '24px',
                                            borderRadius: '50%',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            fontSize: '12px',
                                            fontWeight: '600',
                                            flexShrink: 0
                                        }}>
                                            {step.step_number || idx + 1}
                                        </div>
                                        <div style={{ flex: 1 }}>
                                            <div style={{
                                                fontSize: '14px',
                                                fontWeight: '600',
                                                color: '#e0e0e0',
                                                marginBottom: '4px',
                                                fontFamily: 'Alan Sans, sans-serif'
                                            }}>
                                                {step.action}: {step.target}
                                            </div>
                                            {step.details && (
                                                <div style={{
                                                    fontSize: '13px',
                                                    color: '#b0b0b0',
                                                    marginBottom: '4px',
                                                    fontFamily: 'Alan Sans, sans-serif'
                                                }}>
                                                    {step.details}
                                                </div>
                                            )}
                                            {step.automation_instruction && (
                                                <div style={{
                                                    fontSize: '12px',
                                                    color: '#6B9EFF',
                                                    fontStyle: 'italic',
                                                    fontFamily: 'Alan Sans, sans-serif',
                                                    padding: '8px',
                                                    background: 'rgba(107, 158, 255, 0.1)',
                                                    borderRadius: '4px',
                                                    marginTop: '4px'
                                                }}>
                                                    🤖 {step.automation_instruction}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {workflow.estimated_time && (
                        <div style={{
                            fontSize: '13px',
                            color: '#b0b0b0',
                            marginTop: '12px',
                            fontFamily: 'Alan Sans, sans-serif'
                        }}>
                            ⏱️ Estimated time: {workflow.estimated_time}
                        </div>
                    )}
                </div>
            )}

            {/* Real-time transcription display with smooth word-by-word appearance */}
            {isRecording && (
                <div className="realtime-transcript" style={{
                    background: audioLevel > 0.1
                        ? 'linear-gradient(135deg, #1a1f2e 0%, #252a3a 100%)'
                        : '#1a1f2e',
                    border: `2px solid ${audioLevel > 0.2 ? '#6B9EFF' : 'rgba(100, 100, 120, 0.3)'}`,
                    borderRadius: '8px',
                    padding: '16px',
                    marginBottom: '20px',
                    minHeight: '60px',
                    transition: 'all 0.15s ease',
                    boxShadow: audioLevel > 0.2
                        ? `0 2px 8px rgba(107, 158, 255, ${audioLevel * 0.5})`
                        : 'none'
                }}>
                    {currentTranscript ? (
                        <p style={{
                            color: '#e0e0e0',
                            fontSize: '16px',
                            lineHeight: '1.6',
                            fontFamily: 'Alan Sans, sans-serif',
                            margin: 0,
                            letterSpacing: '0.5px',
                            transition: 'all 0.1s ease'
                        }}>
                            {currentTranscript}
                            {isProcessing && <span style={{
                                display: 'inline-block',
                                width: '3px',
                                height: '20px',
                                background: audioLevel > 0.3 ? '#e74c3c' : '#6B9EFF',
                                marginLeft: '3px',
                                animation: 'blink 1s infinite',
                                verticalAlign: 'middle',
                                borderRadius: '1px'
                            }}></span>}
                        </p>
                    ) : (
                        <div>
                            <p style={{
                                color: '#b0b0b0',
                                fontSize: '14px',
                                fontStyle: 'italic',
                                margin: '0 0 8px 0',
                                fontFamily: 'Alan Sans, sans-serif'
                            }}>
                                <span style={{
                                    display: 'inline-block',
                                    width: '8px',
                                    height: '8px',
                                    background: '#6B9EFF',
                                    borderRadius: '50%',
                                    marginRight: '8px',
                                    animation: 'pulse 2s infinite'
                                }}></span>
                                Listening... Speak now
                            </p>
                            <p style={{
                                color: '#6B9EFF',
                                fontSize: '12px',
                                margin: 0,
                                fontFamily: 'Alan Sans, sans-serif'
                            }}>
                                Waiting for speech...
                            </p>
                        </div>
                    )}
                </div>
            )}

            <style>{`
                 @keyframes blink {
                     0%, 50% { opacity: 1; }
                     51%, 100% { opacity: 0; }
                 }
                 
                 @keyframes pulse {
                     0%, 100% { opacity: 1; transform: scale(1); }
                     50% { opacity: 0.5; transform: scale(1.2); }
                 }
                 
                 .message.system {
                     background: rgba(100, 120, 160, 0.15);
                     margin: 0 auto 8px;
                     text-align: center;
                     max-width: 80%;
                     border: 1px solid rgba(100, 100, 120, 0.3);
                 }
             `}</style>
        </div>
    );
}

export default VoiceAssistant;
