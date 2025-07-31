# 🛰️ GPS Integration Guide for Surveillance Drone System

## Overview
This guide explains how to integrate a real GPS module with your surveillance drone system to display accurate location data on maps.

## 🔧 Hardware Requirements

### GPS Modules (Recommended)
1. **NEO-8M GPS Module** (Budget Option)
   - Price: ~$15-25
   - Accuracy: 2.5m
   - Update Rate: 1-10 Hz
   - Interface: UART

2. **NEO-9M GPS Module** (Better Performance)
   - Price: ~$30-40
   - Accuracy: 1.5m
   - Update Rate: 1-25 Hz
   - Multi-constellation support

3. **RTK GPS (High Precision)**
   - Price: ~$200-500
   - Accuracy: Centimeter level
   - For professional applications

### Connection Hardware
- Flight Controller (Pixhawk, APM, etc.)
- USB-to-TTL Converter (for direct PC connection)
- Jumper wires
- Antenna (usually included)

## 🔌 Hardware Connection Schemes

### Option 1: Direct to Computer (Testing)
```
GPS Module → USB-TTL Converter → Computer
VCC → 3.3V/5V
GND → GND
TX  → RX (USB-TTL)
RX  → TX (USB-TTL)
```

### Option 2: Through Flight Controller
```
GPS Module → Flight Controller → Computer/Telemetry
VCC → GPS Port VCC
GND → GPS Port GND
TX  → GPS Port RX
RX  → GPS Port TX
```

### Option 3: Raspberry Pi Integration
```
GPS Module → Raspberry Pi → Network → Drone System
VCC → 3.3V Pin
GND → GND Pin
TX  → GPIO Pin (RX)
RX  → GPIO Pin (TX)
```

## 💻 Software Implementation

### 1. Python GPS Reader (for direct connection)

```python
# gps_reader.py
import serial
import pynmea2
import json
import requests
import time
from threading import Thread

class GPSReader:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.current_location = {}
        self.running = False
        
    def connect(self):
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"GPS connected on {self.port}")
            return True
        except Exception as e:
            print(f"GPS connection failed: {e}")
            return False
    
    def read_gps_data(self):
        while self.running:
            try:
                line = self.serial_conn.readline().decode('ascii', errors='replace')
                if line.startswith('$GPGGA') or line.startswith('$GNGGA'):
                    msg = pynmea2.parse(line)
                    if msg.latitude and msg.longitude:
                        self.current_location = {
                            'lat': float(msg.latitude),
                            'lng': float(msg.longitude),
                            'altitude': float(msg.altitude) if msg.altitude else 0,
                            'satellites': int(msg.num_sats) if msg.num_sats else 0,
                            'fix_quality': int(msg.gps_qual) if msg.gps_qual else 0,
                            'timestamp': time.time()
                        }
                        # Send to drone system
                        self.send_to_drone_system()
            except Exception as e:
                print(f"GPS read error: {e}")
                time.sleep(1)
    
    def send_to_drone_system(self):
        try:
            requests.post('http://localhost:5000/api/gps/update', 
                         json=self.current_location, timeout=1)
        except:
            pass  # Fail silently if drone system not available
    
    def start(self):
        if self.connect():
            self.running = True
            Thread(target=self.read_gps_data, daemon=True).start()
    
    def stop(self):
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()

# Usage
if __name__ == "__main__":
    gps = GPSReader('/dev/ttyUSB0')  # Adjust port as needed
    gps.start()
    
    try:
        while True:
            print(f"Location: {gps.current_location}")
            time.sleep(5)
    except KeyboardInterrupt:
        gps.stop()
```

### 2. Add GPS API Endpoint to Flask Backend

```python
# Add to backend/api/routes.py or create new gps.py

from flask import Blueprint, request, jsonify
import json
import os
from datetime import datetime

gps_bp = Blueprint('gps', __name__)

# Store current GPS location
current_gps_location = {
    'lat': 0,
    'lng': 0,
    'altitude': 0,
    'satellites': 0,
    'fix_quality': 0,
    'timestamp': None
}

@gps_bp.route('/update', methods=['POST'])
def update_gps_location():
    """Receive GPS updates from external GPS reader."""
    global current_gps_location
    
    try:
        data = request.get_json()
        current_gps_location.update(data)
        current_gps_location['timestamp'] = datetime.now().isoformat()
        
        # Log GPS update
        from utils.logger import get_drone_logger
        logger = get_drone_logger()
        if logger:
            logger.log_gps_event(
                event_type="location_update",
                location=current_gps_location,
                message=f"GPS location updated: {data.get('lat'):.6f}, {data.get('lng'):.6f}"
            )
        
        # Broadcast to connected clients via Socket.IO
        from flask import current_app
        if hasattr(current_app, 'socketio'):
            current_app.socketio.emit('gps_location_update', current_gps_location)
        
        return jsonify({
            'success': True,
            'message': 'GPS location updated'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@gps_bp.route('/current', methods=['GET'])
def get_current_location():
    """Get current GPS location."""
    return jsonify({
        'success': True,
        'location': current_gps_location
    })

@gps_bp.route('/history', methods=['GET'])
def get_location_history():
    """Get GPS location history."""
    # Read from log files or database
    try:
        from utils.logger import get_drone_logger
        logger = get_drone_logger()
        if logger:
            logs = logger.get_logs(log_type='gps', limit=100)
            return jsonify({
                'success': True,
                'history': logs
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Logger not available'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

### 3. Update Dynamic Data Manager

```python
# Add to backend/dynamic_data.py

def update_gps_location(self, lat, lng, altitude=None, satellites=0):
    """Update GPS location from external source."""
    self.current_position = {
        'lat': lat,
        'lng': lng,
        'alt': altitude or self.current_position.get('alt', 0)
    }
    self.gps_satellites = satellites
    self.last_gps_update = time.time()

def get_gps_status(self):
    """Get GPS status information."""
    return {
        'location': self.current_position,
        'satellites': getattr(self, 'gps_satellites', 0),
        'fix_quality': getattr(self, 'gps_fix_quality', 0),
        'last_update': getattr(self, 'last_gps_update', 0),
        'accuracy': self.calculate_gps_accuracy()
    }

def calculate_gps_accuracy(self):
    """Calculate GPS accuracy based on satellite count."""
    satellites = getattr(self, 'gps_satellites', 0)
    if satellites >= 8:
        return 'High (< 3m)'
    elif satellites >= 6:
        return 'Medium (< 5m)'
    elif satellites >= 4:
        return 'Low (< 10m)'
    else:
        return 'Poor (> 10m)'
```

## 🗺️ Map Integration Options

### Option 1: OpenStreetMap (Free)
```javascript
function initializeMap(lat, lng) {
    const mapContainer = document.getElementById('map');
    mapContainer.innerHTML = `
        <iframe 
            src="https://www.openstreetmap.org/export/embed.html?bbox=${lng-0.01},${lat-0.01},${lng+0.01},${lat+0.01}&layer=mapnik&marker=${lat},${lng}"
            style="width: 100%; height: 100%; border: none;">
        </iframe>
    `;
}
```

### Option 2: Google Maps (Requires API Key)
```javascript
function initializeGoogleMap(lat, lng) {
    const map = new google.maps.Map(document.getElementById('map'), {
        zoom: 15,
        center: { lat: lat, lng: lng }
    });
    
    const droneMarker = new google.maps.Marker({
        position: { lat: lat, lng: lng },
        map: map,
        title: 'Drone Location',
        icon: {
            url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
                    <text y="30" font-size="30">🚁</text>
                </svg>
            `),
            scaledSize: new google.maps.Size(40, 40)
        }
    });
}
```

### Option 3: Leaflet (Recommended)
```html
<!-- Add to HTML head -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
function initializeLeafletMap(lat, lng) {
    const map = L.map('map').setView([lat, lng], 15);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Custom drone icon
    const droneIcon = L.divIcon({
        html: '🚁',
        iconSize: [30, 30],
        className: 'drone-marker-leaflet'
    });
    
    const droneMarker = L.marker([lat, lng], {icon: droneIcon}).addTo(map);
    
    // Add flight path tracking
    const flightPath = L.polyline([], {color: 'red'}).addTo(map);
    
    return { map, marker: droneMarker, path: flightPath };
}
</script>
```

## 🚀 Installation Steps

### 1. Install Required Python Packages
```bash
pip install pyserial pynmea2 requests
```

### 2. Connect GPS Module
- Connect GPS module to USB-TTL converter
- Connect to computer via USB
- Note the COM port (Windows) or /dev/ttyUSB* (Linux)

### 3. Test GPS Connection
```bash
python gps_reader.py
```

### 4. Update Backend
- Add GPS API endpoints
- Update dynamic data manager
- Register GPS blueprint

### 5. Update Frontend
- Add map container to dashboard
- Implement map initialization
- Add GPS update listeners

## 🔧 Troubleshooting

### Common Issues
1. **No GPS data**: Check connections and baud rate
2. **Permission denied**: Use `sudo` or add user to dialout group (Linux)
3. **Weak signal**: Move to open area, check antenna connection
4. **Map not loading**: Check internet connection and API keys

### Testing Commands
```bash
# List serial ports
python -m serial.tools.list_ports

# Test GPS module directly
screen /dev/ttyUSB0 9600  # Linux
# Or use PuTTY on Windows

# Check GPS NMEA sentences
cat /dev/ttyUSB0  # Should show $GPGGA, $GPRMC, etc.
```

## 📊 Expected Accuracy

| GPS Type | Accuracy | Cost | Use Case |
|----------|----------|------|----------|
| Standard GPS | 2-5m | $15-40 | Hobby/Testing |
| DGPS | 1-3m | $50-100 | Professional |
| RTK GPS | 1cm-10cm | $200-500 | Survey/Precision |

## 🔄 Real-time Updates

The system will:
1. Read GPS data every second
2. Update drone location in real-time
3. Log GPS events for tracking
4. Display location on interactive map
5. Track flight path and waypoints
6. Calculate distance and speed metrics

This integration will give you precise, real-time GPS tracking of your drone with professional-grade mapping capabilities!
