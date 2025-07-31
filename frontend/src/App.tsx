import React, { useState, useEffect } from 'react';
import axios from 'axios';
import io, { Socket } from 'socket.io-client';
import './App.css';

interface DroneStatus {
  armed: boolean;
  flying: boolean;
  mode: string;
  position: {
    lat: number;
    lng: number;
    alt: number;
  };
  battery: {
    percentage: number;
    voltage: number;
    current: number;
  };
  sensors: {
    gps_satellites: number;
    compass_heading: number;
    gps_hdop: number;
  };
  timestamp: string;
}

interface TelemetryData {
  flight_data: {
    armed: boolean;
    flying: boolean;
    mode: string;
    position: {
      latitude: number;
      longitude: number;
      altitude: number;
      relative_altitude: number;
    };
    attitude: {
      roll: number;
      pitch: number;
      yaw: number;
    };
    velocity: {
      ground_speed: number;
      vx: number;
      vy: number;
      vz: number;
    };
  };
  sensor_data: {
    battery: {
      voltage: number;
      current: number;
      remaining: number;
      capacity: number;
    };
    gps: {
      satellites: number;
      fix_type: number;
      hdop: number;
      vdop: number;
    };
  };
  system_status: {
    cpu_usage: number;
    memory_usage: number;
    temperature: number;
    uptime: string;
  };
  timestamp: string;
}

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [droneStatus, setDroneStatus] = useState<DroneStatus | null>(null);
  const [telemetryData, setTelemetryData] = useState<TelemetryData | null>(null);
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState<string | null>(null);

  useEffect(() => {
    // Initialize Socket.IO connection
    const newSocket = io('http://localhost:5000');
    setSocket(newSocket);

    newSocket.on('connect', () => {
      setIsConnected(true);
      console.log('Connected to drone system');
    });

    newSocket.on('disconnect', () => {
      setIsConnected(false);
      console.log('Disconnected from drone system');
    });

    newSocket.on('telemetry_update', (data: TelemetryData) => {
      setTelemetryData(data);
    });

    newSocket.on('status_update', (data: DroneStatus) => {
      setDroneStatus(data);
    });

    // Initial data fetch
    fetchDroneStatus();
    fetchTelemetryData();

    // Cleanup
    return () => {
      newSocket.close();
    };
  }, []);

  const fetchDroneStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/drone/status`);
      setDroneStatus(response.data);
    } catch (error) {
      console.error('Error fetching drone status:', error);
    }
  };

  const fetchTelemetryData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/telemetry/current`);
      setTelemetryData(response.data);
    } catch (error) {
      console.error('Error fetching telemetry data:', error);
    }
  };

  const sendDroneCommand = async (command: string, data: any = {}) => {
    setLoading(command);
    try {
      const response = await axios.post(`${API_BASE_URL}/drone/${command}`, data);
      console.log(`Command ${command} result:`, response.data);
      setTimeout(() => fetchDroneStatus(), 1000); // Refresh status after command
    } catch (error) {
      console.error(`Error sending command ${command}:`, error);
    } finally {
      setLoading(null);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🚁 Surveillance Drone Control System</h1>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            ●
          </span>
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </header>

      <div className="dashboard">
        {/* Drone Status Panel */}
        <div className="panel status-panel">
          <h2>Drone Status</h2>
          {droneStatus ? (
            <div className="status-grid">
              <div className="status-item">
                <span className="label">Armed:</span>
                <span className={`value ${droneStatus.armed ? 'armed' : 'disarmed'}`}>
                  {droneStatus.armed ? 'ARMED' : 'DISARMED'}
                </span>
              </div>
              <div className="status-item">
                <span className="label">Flying:</span>
                <span className={`value ${droneStatus.flying ? 'flying' : 'grounded'}`}>
                  {droneStatus.flying ? 'FLYING' : 'GROUNDED'}
                </span>
              </div>
              <div className="status-item">
                <span className="label">Mode:</span>
                <span className="value">{droneStatus.mode}</span>
              </div>
              <div className="status-item">
                <span className="label">Battery:</span>
                <span className="value">{droneStatus.battery.percentage}%</span>
              </div>
              <div className="status-item">
                <span className="label">GPS Satellites:</span>
                <span className="value">{droneStatus.sensors.gps_satellites}</span>
              </div>
              <div className="status-item">
                <span className="label">Position:</span>
                <span className="value">
                  {droneStatus.position.lat.toFixed(6)}, {droneStatus.position.lng.toFixed(6)}
                </span>
              </div>
              <div className="status-item">
                <span className="label">Altitude:</span>
                <span className="value">{droneStatus.position.alt.toFixed(1)}m</span>
              </div>
              <div className="status-item">
                <span className="label">Last Update:</span>
                <span className="value">{formatTimestamp(droneStatus.timestamp)}</span>
              </div>
            </div>
          ) : (
            <div className="loading">Loading drone status...</div>
          )}
        </div>

        {/* Control Panel */}
        <div className="panel control-panel">
          <h2>Drone Controls</h2>
          <div className="control-buttons">
            <button 
              className="control-btn arm-btn"
              onClick={() => sendDroneCommand(droneStatus?.armed ? 'disarm' : 'arm')}
              disabled={loading !== null}
            >
              {loading === (droneStatus?.armed ? 'disarm' : 'arm') ? 'Processing...' : 
               droneStatus?.armed ? 'DISARM' : 'ARM'}
            </button>
            
            <button 
              className="control-btn takeoff-btn"
              onClick={() => sendDroneCommand('takeoff', { altitude: 10 })}
              disabled={loading !== null || !droneStatus?.armed || droneStatus?.flying}
            >
              {loading === 'takeoff' ? 'Processing...' : 'TAKEOFF'}
            </button>
            
            <button 
              className="control-btn land-btn"
              onClick={() => sendDroneCommand('land')}
              disabled={loading !== null || !droneStatus?.flying}
            >
              {loading === 'land' ? 'Processing...' : 'LAND'}
            </button>
            
            <button 
              className="control-btn emergency-btn"
              onClick={() => sendDroneCommand('emergency-stop')}
              disabled={loading !== null}
            >
              {loading === 'emergency-stop' ? 'Processing...' : 'EMERGENCY STOP'}
            </button>
          </div>
        </div>

        {/* Telemetry Panel */}
        <div className="panel telemetry-panel">
          <h2>Real-time Telemetry</h2>
          {telemetryData ? (
            <div className="telemetry-grid">
              <div className="telemetry-section">
                <h3>Flight Data</h3>
                <div className="telemetry-item">
                  <span className="label">Ground Speed:</span>
                  <span className="value">{telemetryData.flight_data.velocity.ground_speed.toFixed(1)} m/s</span>
                </div>
                <div className="telemetry-item">
                  <span className="label">Attitude (R/P/Y):</span>
                  <span className="value">
                    {telemetryData.flight_data.attitude.roll.toFixed(1)}° / 
                    {telemetryData.flight_data.attitude.pitch.toFixed(1)}° / 
                    {telemetryData.flight_data.attitude.yaw.toFixed(1)}°
                  </span>
                </div>
              </div>
              
              <div className="telemetry-section">
                <h3>Battery</h3>
                <div className="telemetry-item">
                  <span className="label">Voltage:</span>
                  <span className="value">{telemetryData.sensor_data.battery.voltage.toFixed(1)}V</span>
                </div>
                <div className="telemetry-item">
                  <span className="label">Current:</span>
                  <span className="value">{telemetryData.sensor_data.battery.current.toFixed(1)}A</span>
                </div>
                <div className="telemetry-item">
                  <span className="label">Remaining:</span>
                  <span className="value">{telemetryData.sensor_data.battery.remaining}%</span>
                </div>
              </div>
              
              <div className="telemetry-section">
                <h3>System</h3>
                <div className="telemetry-item">
                  <span className="label">CPU Usage:</span>
                  <span className="value">{telemetryData.system_status.cpu_usage.toFixed(1)}%</span>
                </div>
                <div className="telemetry-item">
                  <span className="label">Memory:</span>
                  <span className="value">{telemetryData.system_status.memory_usage.toFixed(1)}%</span>
                </div>
                <div className="telemetry-item">
                  <span className="label">Temperature:</span>
                  <span className="value">{telemetryData.system_status.temperature.toFixed(1)}°C</span>
                </div>
                <div className="telemetry-item">
                  <span className="label">Uptime:</span>
                  <span className="value">{telemetryData.system_status.uptime}</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="loading">Loading telemetry data...</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
