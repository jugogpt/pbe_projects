import React, { useState, useEffect } from 'react';
import API from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function ActivityChart() {
    const [chartData, setChartData] = useState([]);

    useEffect(() => {
        loadChartData();
    }, []);

    const loadChartData = async () => {
        try {
            const response = await API.getChartData();
            if (response.data && response.data.labels) {
                const data = response.data.labels.map((label, idx) => ({
                    app: label,
                    minutes: response.data.data[idx] || 0
                }));
                setChartData(data);
            }
        } catch (error) {
            console.error('Error loading chart data:', error);
        }
    };

    return (
        <div className="panel chart-panel">
            <h2>Activity Usage</h2>

            <div className="chart-container">
                {chartData.length === 0 ? (
                    <p>No usage data available</p>
                ) : (
                    <ResponsiveContainer width="100%" height={400}>
                        <BarChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="app" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="minutes" fill="#6478ff" />
                        </BarChart>
                    </ResponsiveContainer>
                )}
            </div>

            <button onClick={loadChartData}>Refresh Data</button>
        </div>
    );
}

export default ActivityChart;
