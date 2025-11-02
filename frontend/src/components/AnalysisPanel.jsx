import React, { useState, useEffect, useRef } from 'react';
import API from '../services/api';

function AnalysisPanel() {
    const [recordings, setRecordings] = useState([]);
    const [selectedRecording, setSelectedRecording] = useState(null);
    const [analysis, setAnalysis] = useState('');
    const [workflow, setWorkflow] = useState(null);
    const [loading, setLoading] = useState(false);
    const fileInputRef = useRef(null);
    const wsRef = useRef(null);

    useEffect(() => {
        loadRecordings();

        // Connect to WebSocket for real-time updates
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.hostname}:5000/ws`;
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            switch (data.type) {
                case 'workflow_generated':
                    console.log('Workflow generated:', data.data);
                    setWorkflow(data.data.workflow);
                    break;
                case 'analysis_complete':
                    if (data.data.workflow) {
                        setWorkflow(data.data.workflow);
                    }
                    break;
                default:
                    break;
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    const loadRecordings = async () => {
        try {
            const response = await API.listRecordings();
            setRecordings(response.data.recordings || []);
        } catch (error) {
            console.error('Error loading recordings:', error);
            console.error('Error details:', error.response?.data || error.message);
        }
    };

    const handleFileSelect = async () => {
        // Create file input element
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'video/*';
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (file) {
                setLoading(true);
                try {
                    // Upload file to server and save it
                    const response = await API.uploadVideo(file);

                    if (response.data.success) {
                        // Reload recordings list to include the new upload
                        await loadRecordings();

                        // Set the uploaded recording as selected
                        setSelectedRecording({
                            path: response.data.path,
                            filename: response.data.filename,
                            file: null // File is now saved on server
                        });
                    }
                } catch (error) {
                    console.error('Error uploading video:', error);
                    alert(`Failed to upload video: ${error.message || 'Unknown error'}`);
                } finally {
                    setLoading(false);
                }
            }
        };
        input.click();
    };

    const handleQuickAnalysis = async () => {
        if (!selectedRecording) {
            alert('Please select a recording first');
            return;
        }

        setLoading(true);
        try {
            console.log('Starting quick analysis for:', selectedRecording.path);
            const response = await API.quickAnalysis(selectedRecording.path);
            console.log('Analysis response:', response);

            if (response.data.analysis) {
                setAnalysis(response.data.analysis);
            } else {
                setAnalysis('Analysis completed but no results returned');
            }
        } catch (error) {
            console.error('Error analyzing video:', error);
            setAnalysis(`Error analyzing video: ${error.message || 'Unknown error'}`);
        } finally {
            setLoading(false);
        }
    };

    const handleDetailedAnalysis = async () => {
        if (!selectedRecording) {
            alert('Please select a recording first');
            return;
        }

        setLoading(true);
        try {
            console.log('Starting detailed analysis for:', selectedRecording.path);
            const response = await API.detailedAnalysis(selectedRecording.path);
            console.log('Analysis response:', response);

            if (response.data.analysis) {
                setAnalysis(response.data.analysis);
            } else {
                setAnalysis('Analysis completed but no results returned');
            }
        } catch (error) {
            console.error('Error analyzing video:', error);
            setAnalysis(`Error analyzing video: ${error.message || 'Unknown error'}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="panel analysis-panel">
            <h2>Video Analysis</h2>

            <div className="recording-selector">
                <h3>Select Recording</h3>
                <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                    <select
                        value={selectedRecording?.path || ''}
                        onChange={(e) => {
                            const rec = recordings.find(r => r.path === e.target.value);
                            setSelectedRecording(rec);
                        }}
                        style={{ flex: 1 }}
                    >
                        <option value="">Select from saved recordings...</option>
                        {recordings.map((recording, idx) => (
                            <option key={idx} value={recording.path}>
                                {recording.filename}
                            </option>
                        ))}
                    </select>
                    <button onClick={handleFileSelect} style={{ padding: '8px 16px' }}>
                        Browse Files
                    </button>
                </div>
                {selectedRecording && (
                    <p style={{ color: '#4a9eff' }}>Selected: {selectedRecording.filename}</p>
                )}
            </div>

            <div className="analysis-controls">
                <button
                    onClick={handleQuickAnalysis}
                    disabled={!selectedRecording || loading}
                >
                    {loading ? 'Analyzing...' : 'Quick Analysis'}
                </button>
                <button
                    onClick={handleDetailedAnalysis}
                    disabled={!selectedRecording || loading}
                >
                    {loading ? 'Analyzing...' : 'Detailed Workflow'}
                </button>
            </div>

            <div className="analysis-results">
                <h3>Analysis Results</h3>
                <pre style={{
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    background: '#1a1a1a',
                    color: '#e0e0e0',
                    padding: '16px',
                    borderRadius: '8px',
                    border: '1px solid #333'
                }}>
                    {analysis || 'Select a recording and run analysis'}
                </pre>
            </div>

            {/* Generated Workflow Display */}
            {workflow && (
                <div style={{
                    background: 'linear-gradient(135deg, #1a1f2e 0%, #252a3a 100%)',
                    border: '2px solid #6B9EFF',
                    borderRadius: '8px',
                    padding: '20px',
                    marginTop: '20px',
                    boxShadow: '0 4px 12px rgba(107, 158, 255, 0.2)'
                }}>
                    <h3 style={{
                        color: '#6B9EFF',
                        marginBottom: '16px',
                        fontSize: '18px',
                        fontWeight: '600'
                    }}>
                        🤖 Generated Workflow
                    </h3>

                    {workflow.title && (
                        <h4 style={{ color: '#fff', marginBottom: '12px' }}>
                            {workflow.title}
                        </h4>
                    )}

                    {workflow.description && (
                        <p style={{ color: '#b0b0b0', marginBottom: '16px' }}>
                            {workflow.description}
                        </p>
                    )}

                    {workflow.steps && Array.isArray(workflow.steps) && workflow.steps.length > 0 && (
                        <div style={{ marginTop: '16px' }}>
                            <h4 style={{ color: '#6B9EFF', marginBottom: '12px' }}>Steps:</h4>
                            {workflow.steps.map((step, idx) => (
                                <div key={idx} style={{
                                    background: 'rgba(107, 158, 255, 0.1)',
                                    borderLeft: '3px solid #6B9EFF',
                                    padding: '12px',
                                    marginBottom: '8px',
                                    borderRadius: '4px'
                                }}>
                                    <div style={{ color: '#fff', fontWeight: '500', marginBottom: '4px' }}>
                                        {step.step_number || idx + 1}. {step.action || 'Action'}
                                    </div>
                                    <div style={{ color: '#b0b0b0', fontSize: '14px' }}>
                                        {step.target && <div>Target: {step.target}</div>}
                                        {step.details && <div>Details: {step.details}</div>}
                                        {step.automation_instruction && (
                                            <div style={{ color: '#6B9EFF', marginTop: '4px' }}>
                                                🤖 {step.automation_instruction}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {workflow.estimated_time && (
                        <div style={{ color: '#b0b0b0', marginTop: '16px' }}>
                            ⏱️ Estimated time: {workflow.estimated_time}
                        </div>
                    )}

                    {workflow.automation_ready !== undefined && (
                        <div style={{
                            color: workflow.automation_ready ? '#4ade80' : '#f59e0b',
                            marginTop: '12px',
                            fontWeight: '500'
                        }}>
                            {workflow.automation_ready ? '✅ Automation ready' : '⚠️ Manual review required'}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default AnalysisPanel;
