import React, { useState, useEffect } from 'react';
import API from '../services/api';

function RecordingPanel() {
    const [isRecording, setIsRecording] = useState(false);
    const [recordings, setRecordings] = useState([]);

    useEffect(() => {
        loadRecordings();
    }, []);

    const loadRecordings = async () => {
        try {
            const response = await API.listRecordings();
            setRecordings(response.data.recordings || []);
        } catch (error) {
            console.error('Error loading recordings:', error);
        }
    };

    const handleStartRecording = async () => {
        try {
            console.log('Starting recording...');
            const response = await API.startRecording();
            console.log('Recording started:', response.data);
            setIsRecording(true);
            alert('Recording started successfully');
        } catch (error) {
            console.error('Error starting recording:', error);
            alert(`Error starting recording: ${error.message || 'Unknown error'}`);
        }
    };

    const handleStopRecording = async () => {
        try {
            console.log('Stopping recording...');
            const response = await API.stopRecording();
            console.log('Recording stopped:', response.data);
            setIsRecording(false);
            alert('Recording stopped successfully');
            loadRecordings(); // Refresh list
        } catch (error) {
            console.error('Error stopping recording:', error);
            alert(`Error stopping recording: ${error.message || 'Unknown error'}`);
        }
    };

    const handleCaptureScreenshot = async () => {
        try {
            console.log('Capturing screenshot...');
            const response = await API.captureScreenshot();
            console.log('Screenshot captured:', response.data);
            alert('Screenshot captured successfully');
        } catch (error) {
            console.error('Error capturing screenshot:', error);
            alert(`Error capturing screenshot: ${error.message || 'Unknown error'}`);
        }
    };

    return (
        <div className="panel recording-panel">
            <h2>Screen Recording</h2>

            <div className="controls">
                <button
                    className={isRecording ? 'recording-active' : ''}
                    onClick={isRecording ? handleStopRecording : handleStartRecording}
                >
                    {isRecording ? 'Stop Recording' : 'Start Recording'}
                </button>

                <button onClick={handleCaptureScreenshot}>
                    Capture Screenshot
                </button>
            </div>

            <div className="recordings-list">
                <h3>Recent Recordings</h3>
                {recordings.length === 0 ? (
                    <p>No recordings yet</p>
                ) : (
                    <ul>
                        {recordings.map((recording, idx) => (
                            <li key={idx}>{recording.filename}</li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
}

export default RecordingPanel;
