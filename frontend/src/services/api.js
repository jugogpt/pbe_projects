import axios from 'axios';

const API_BASE = 'http://127.0.0.1:5000/api';
const WS_URL = 'ws://127.0.0.1:5000/ws';

class API {
    constructor() {
        this.ws = null;
        this.wsCallbacks = [];
    }

    // WebSocket connection
    connectWebSocket(onMessage) {
        this.ws = new WebSocket(WS_URL);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            onMessage(data);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            // Reconnect after 3 seconds
            setTimeout(() => this.connectWebSocket(onMessage), 3000);
        };
    }

    // Recording endpoints
    async startRecording() {
        return await axios.post(`${API_BASE}/recording/start`);
    }

    async stopRecording() {
        return await axios.post(`${API_BASE}/recording/stop`);
    }

    async getRecordingStatus() {
        return await axios.get(`${API_BASE}/recording/status`);
    }

    async listRecordings() {
        return await axios.get(`${API_BASE}/recordings/list`);
    }

    // Screenshot endpoints
    async captureScreenshot() {
        return await axios.post(`${API_BASE}/screenshot/capture`);
    }

    async listScreenshots() {
        return await axios.get(`${API_BASE}/screenshots/list`);
    }

    // Activity tracking
    async getUsageData(date) {
        return await axios.get(`${API_BASE}/activity/usage`, {
            params: { date }
        });
    }

    async getChartData() {
        return await axios.get(`${API_BASE}/activity/chart-data`);
    }

    // Video analysis
    async uploadVideo(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            return await axios.post(`${API_BASE}/analysis/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
        } catch (error) {
            console.error('Video upload error:', error.response?.data || error.message);
            throw error;
        }
    }

    async quickAnalysis(videoPath) {
        try {
            return await axios.post(`${API_BASE}/analysis/quick`, {
                video_path: videoPath,
                detailed: false
            });
        } catch (error) {
            console.error('Quick analysis error:', error.response?.data || error.message);
            throw error;
        }
    }

    async detailedAnalysis(videoPath) {
        try {
            return await axios.post(`${API_BASE}/analysis/detailed`, {
                video_path: videoPath,
                detailed: true
            });
        } catch (error) {
            console.error('Detailed analysis error:', error.response?.data || error.message);
            throw error;
        }
    }

    // Voice assistant
    async startVoice() {
        return await axios.post(`${API_BASE}/voice/start`);
    }

    async stopVoice() {
        return await axios.post(`${API_BASE}/voice/stop`);
    }

    async sendVoiceMessage(text) {
        return await axios.post(`${API_BASE}/voice/message`, { text });
    }

    async getTranscripts() {
        return await axios.get(`${API_BASE}/voice/transcripts`);
    }

    // System
    async openFolder(path) {
        return await axios.post(`${API_BASE}/system/open-folder`, { path });
    }

    async getFolders() {
        return await axios.get(`${API_BASE}/system/folders`);
    }
}

export default new API();
