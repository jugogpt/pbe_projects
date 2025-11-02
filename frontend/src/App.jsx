import React, { useState, useEffect } from 'react';
import API from './services/api';
import RecordingPanel from './components/RecordingPanel.jsx';
import AnalysisPanel from './components/AnalysisPanel.jsx';
import VoiceAssistant from './components/VoiceAssistant.jsx';
import ActivityChart from './components/ActivityChart.jsx';
import './styles/App.css';

function App() {
    const [activeTab, setActiveTab] = useState('recording');
    const [status, setStatus] = useState('Ready');
    const [wsConnected, setWsConnected] = useState(false);

    useEffect(() => {
        // Connect to WebSocket
        const handleMessage = (message) => {
            switch (message.type) {
                case 'recording_started':
                    setStatus('Recording started');
                    break;
                case 'recording_stopped':
                    setStatus('Recording stopped');
                    break;
                case 'screenshot_captured':
                    setStatus('Screenshot captured');
                    break;
                case 'analysis_complete':
                    setStatus('Analysis complete');
                    break;
                default:
                    console.log('Unknown message:', message);
            }
        };

        API.connectWebSocket(handleMessage);
        setWsConnected(true);
    }, []);



    return (
        <div className="app">
            {/* Title Bar */}
            <div className="title-bar">
                <div className="title">Activity Tracker AI</div>
                <div className="window-controls">
                    <button onClick={() => window.electron?.minimize()}>─</button>
                    <button onClick={() => window.electron?.maximize()}>□</button>
                    <button onClick={() => window.electron?.close()}>✕</button>
                </div>
            </div>

            {/* Status Bar */}
            <div className="status-bar">
                <span className={`status-indicator ${wsConnected ? 'connected' : ''}`}></span>
                <span>{status}</span>
            </div>

            {/* Main Content */}
            <div className="main-content">
                {/* Sidebar */}
                <div className="sidebar">
                    <button
                        className={activeTab === 'recording' ? 'active' : ''}
                        onClick={() => setActiveTab('recording')}
                    >
                        Recording
                    </button>
                    <button
                        className={activeTab === 'analysis' ? 'active' : ''}
                        onClick={() => setActiveTab('analysis')}
                    >
                        Analysis
                    </button>
                    <button
                        className={activeTab === 'voice' ? 'active' : ''}
                        onClick={() => setActiveTab('voice')}
                    >
                        Voice Assistant
                    </button>
                    <button
                        className={activeTab === 'activity' ? 'active' : ''}
                        onClick={() => setActiveTab('activity')}
                    >
                        Activity
                    </button>
                </div>

                {/* Content Area */}
                <div className="content-area">
                    {activeTab === 'recording' && <RecordingPanel />}
                    {activeTab === 'analysis' && <AnalysisPanel />}
                    {activeTab === 'voice' && <VoiceAssistant />}
                    {activeTab === 'activity' && <ActivityChart />}
                </div>
            </div>
        </div>
    );
}

export default App;
