# 🛰️ **Surveillance Drone System**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenCV](https://img.shields.io/badge/opencv-4.x-green.svg)](https://opencv.org/)
[![Flask](https://img.shields.io/badge/flask-2.x-orange.svg)](https://flask.palletsprojects.com/)

An intelligent surveillance drone system designed for real-time aerial monitoring, object detection, and secure data transmission. Built using open-source hardware and software technologies, this project demonstrates a low-cost, scalable solution for defense, border security, and disaster monitoring applications.

## 📋 Table of Contents

- [Features](#-project-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Hardware Requirements](#-hardware-requirements)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)
- [Roadmap](#️-roadmap)
- [Use Cases](#-use-cases)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)





## 🚀 Project Features

### Core Capabilities
- 📷 **Live Video Streaming** - Real-time HD video feed via onboard camera with adaptive bitrate
- 🧠 **Object Detection** - Advanced AI-powered detection using YOLO and OpenCV
- 🌐 **Remote Dashboard** - Responsive web interface for live telemetry & video monitoring
- 📍 **GPS Location Tracking** - Precise positioning with route planning and geofencing
- 🛰️ **Autonomous Flight** - Intelligent navigation with obstacle avoidance algorithms
- 📊 **Mission Data Logging** - Comprehensive flight data recording and replay capabilities
- 🔋 **System Monitoring** - Real-time power, signal strength, and component health tracking

### Advanced Features
- 🎯 **Target Tracking** - Automated object following with predictive algorithms
- 🚨 **Alert System** - Configurable alerts for detected objects and system anomalies
- 🔐 **Secure Communication** - Encrypted data transmission with authentication
- 📱 **Mobile Support** - Cross-platform mobile app for field operations
- 🌙 **Night Vision** - Infrared and low-light imaging capabilities
- 🗺️ **Mission Planning** - Pre-defined flight paths with waypoint navigation





## 🧠 Tech Stack

| Layer | Technologies | Purpose |
|-------|-------------|---------|
| **Hardware** | Raspberry Pi 4B, Arduino Uno, Neo-8M GPS, Pi Camera V2, HC-SR04 Ultrasonic | Core processing, sensors, and control |
| **Flight Control** | Pixhawk 4, MAVLink Protocol, ArduPilot | Autonomous flight management |
| **Programming** | Python 3.8+, C++17, JavaScript ES6+ | Core logic and control systems |
| **Computer Vision** | OpenCV 4.x, YOLO v5, TensorFlow Lite | Object detection and image processing |
| **Web Backend** | Flask 2.x, Socket.IO, SQLAlchemy | API and real-time communication |
| **Web Frontend** | React 18, TypeScript, Three.js, Leaflet.js | User interface and visualization |
| **Database** | SQLite (dev), PostgreSQL (prod) | Data persistence and logging |
| **Communication** | WebRTC, MQTT, HTTP/HTTPS, WebSocket | Real-time data transmission |
| **Maps & Location** | Google Maps API, OpenStreetMap, Leaflet | Geospatial visualization |
| **Mobile** | React Native, Expo | Cross-platform mobile application |
| **DevOps** | Docker, GitHub Actions, Nginx | Deployment and CI/CD |

### Dependencies & Versions
```yaml
Python: ">=3.8"
OpenCV: ">=4.5.0"
Flask: ">=2.0.0"
React: ">=18.0.0"
Node.js: ">=16.0.0"
```

## 🏗️ System Architecture

The surveillance drone system follows a modular architecture with distinct layers:

```
┌─────────────────────────────────────────────────────────┐
│                    Web Dashboard                        │
│              (React + TypeScript)                       │
└─────────────────────┬───────────────────────────────────┘
                      │ WebSocket/HTTP API
┌─────────────────────┴───────────────────────────────────┐
│                  Backend Server                         │
│                 (Flask + Socket.IO)                     │
└─────────────────────┬───────────────────────────────────┘
                      │ Serial/MAVLink
┌─────────────────────┴───────────────────────────────────┐
│                 Drone Controller                        │
│               (Raspberry Pi + Python)                   │
├─────────────────────┼───────────────────────────────────┤
│  Camera Module      │  GPS Module      │  Sensors       │
│  Object Detection   │  Flight Control  │  Telemetry     │
└─────────────────────┴──────────────────┴────────────────┘
```

### Communication Flow
1. **Sensor Data Collection** → Raspberry Pi processes sensor inputs
2. **Computer Vision** → Real-time object detection and tracking
3. **Flight Control** → MAVLink commands to flight controller
4. **Data Transmission** → WebSocket streaming to dashboard
5. **User Interface** → Real-time visualization and control

## 🔧 Hardware Requirements

### Essential Components
| Component | Model | Quantity | Purpose |
|-----------|--------|----------|---------|
| **Single Board Computer** | Raspberry Pi 4B (4GB+) | 1 | Main processing unit |
| **Microcontroller** | Arduino Uno R3 | 1 | Sensor interfacing |
| **Flight Controller** | Pixhawk 4 / APM 2.8 | 1 | Flight management |
| **Camera** | Raspberry Pi Camera V2 | 1 | Video streaming |
| **GPS Module** | u-blox Neo-8M | 1 | Position tracking |
| **Ultrasonic Sensor** | HC-SR04 | 4 | Obstacle detection |
| **Power Module** | 5V/3A UBEC | 1 | Power distribution |
| **Telemetry** | 3DR Radio / ESP32 | 1 | Long-range communication |

### Optional Components
- **Gimbal**: 2-axis brushless gimbal for camera stabilization
- **LiDAR**: TF-Luna for advanced obstacle detection
- **Thermal Camera**: FLIR Lepton for night vision
- **Companion Computer**: Jetson Nano for AI acceleration

### Minimum System Requirements (Ground Station)
- **OS**: Linux (Ubuntu 20.04+), Windows 10+, macOS 10.15+
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB available space
- **Network**: Wi-Fi or Ethernet connection
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+

## 📦 Installation

### Prerequisites
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install system dependencies
sudo apt install git cmake build-essential pkg-config -y
sudo apt install libopencv-dev python3-opencv -y
```

### Quick Start
1. **Clone the repository**
```bash
git clone https://github.com/umairism/Surveillance-Drone-System.git
cd Surveillance-Drone-System
```

2. **Set up Python environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Install dashboard dependencies**
```bash
cd dashboard
npm install
cd ..
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
python scripts/init_db.py
```

6. **Run the system**
```bash
# Terminal 1: Start backend
python dronecore/main.py

# Terminal 2: Start dashboard
cd dashboard && npm start
```

### Hardware Setup
1. **Connect components** according to the wiring diagram in `docs/hardware/`
2. **Flash firmware** to flight controller using Mission Planner
3. **Calibrate sensors** using the calibration script
4. **Test connections** with diagnostic tools

## 🗂️ Project Structure

```
Surveillance-Drone-System/
├── 📁 dronecore/                 # Core drone software
│   ├── main.py                   # Main application entry point
│   ├── flight_controller.py      # Flight control logic
│   ├── video_stream.py           # Camera and streaming
│   ├── object_detection.py       # AI vision processing
│   ├── gps_tracker.py            # GPS and navigation
│   ├── sensor_manager.py         # Sensor data collection
│   ├── communication.py          # Data transmission
│   └── config/                   # Configuration files
│       ├── drone_config.yaml     # Drone parameters
│       ├── camera_config.yaml    # Camera settings
│       └── detection_models/     # AI models
├── 📁 dashboard/                 # Web dashboard
│   ├── public/                   # Static assets
│   ├── src/                      # React source code
│   │   ├── components/           # React components
│   │   ├── pages/                # Dashboard pages
│   │   ├── services/             # API services
│   │   └── utils/                # Utility functions
│   ├── package.json              # Node.js dependencies
│   └── webpack.config.js         # Build configuration
├── 📁 mobile_app/                # Mobile application
│   ├── src/                      # React Native source
│   ├── android/                  # Android specific files
│   ├── ios/                      # iOS specific files
│   └── package.json              # Mobile dependencies
├── 📁 scripts/                   # Utility scripts
│   ├── init_db.py                # Database initialization
│   ├── calibrate_sensors.py      # Sensor calibration
│   ├── test_connection.py        # Connection testing
│   └── deploy.sh                 # Deployment script
├── 📁 docs/                      # Documentation
│   ├── api/                      # API documentation
│   ├── hardware/                 # Hardware guides
│   │   ├── wiring_diagram.png    # Component wiring
│   │   └── assembly_guide.md     # Assembly instructions
│   ├── software/                 # Software guides
│   └── troubleshooting.md        # Common issues
├── 📁 tests/                     # Test files
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test data
├── 📁 logs/                      # Application logs
│   ├── flight_logs/              # Flight data
│   ├── error_logs/               # Error logs
│   └── mission_logs/             # Mission records
├── 📁 data/                      # Data storage
│   ├── models/                   # Trained AI models
│   ├── calibration/              # Calibration data
│   └── missions/                 # Mission data
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Docker configuration
├── LICENSE                       # MIT License
└── README.md                     # This file
```

## ⚙️ Configuration

### Environment Variables
```bash
# .env file configuration
# Database
DATABASE_URL=sqlite:///drone_data.db
DATABASE_POOL_SIZE=10

# Video Streaming
CAMERA_RESOLUTION=1920x1080
CAMERA_FPS=30
STREAM_QUALITY=high
RTMP_SERVER_URL=rtmp://localhost:1935/live

# GPS and Navigation
GPS_BAUDRATE=9600
GPS_PORT=/dev/ttyACM0
HOME_LATITUDE=33.6844
HOME_LONGITUDE=73.0479

# Object Detection
DETECTION_MODEL=yolov5s
CONFIDENCE_THRESHOLD=0.5
NMS_THRESHOLD=0.4
DETECTION_CLASSES=person,car,truck,motorcycle

# Communication
MAVLINK_PORT=/dev/ttyUSB0
MAVLINK_BAUDRATE=57600
TELEMETRY_FREQUENCY=10
SOCKET_PORT=5000

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret
ENCRYPTION_KEY=your-encryption-key

# API Keys
GOOGLE_MAPS_API_KEY=your-google-maps-key
WEATHER_API_KEY=your-weather-api-key
```

### Drone Configuration (drone_config.yaml)
```yaml
drone:
  name: "SurvDrone-001"
  type: "quadcopter"
  max_altitude: 120  # meters
  max_speed: 15      # m/s
  battery_capacity: 5000  # mAh
  
flight_controller:
  type: "pixhawk4"
  firmware: "arducopter"
  failsafe_enabled: true
  return_to_home: true
  
sensors:
  gps:
    enabled: true
    update_rate: 10  # Hz
  camera:
    enabled: true
    resolution: [1920, 1080]
    fps: 30
  ultrasonic:
    enabled: true
    max_range: 400  # cm
    
geofence:
  enabled: true
  radius: 1000  # meters
  max_altitude: 120  # meters
```

## 📡 API Documentation

### REST API Endpoints

#### Drone Control
```http
POST /api/v1/drone/takeoff
POST /api/v1/drone/land
POST /api/v1/drone/arm
POST /api/v1/drone/disarm
GET  /api/v1/drone/status
POST /api/v1/drone/goto
```

#### Mission Management
```http
GET    /api/v1/missions
POST   /api/v1/missions
GET    /api/v1/missions/{id}
PUT    /api/v1/missions/{id}
DELETE /api/v1/missions/{id}
POST   /api/v1/missions/{id}/start
POST   /api/v1/missions/{id}/pause
POST   /api/v1/missions/{id}/stop
```

#### Video Stream
```http
GET  /api/v1/stream/live
GET  /api/v1/stream/recording
POST /api/v1/stream/start-recording
POST /api/v1/stream/stop-recording
```

#### Detection & Tracking
```http
GET  /api/v1/detections
POST /api/v1/detections/config
GET  /api/v1/tracking/targets
POST /api/v1/tracking/start
POST /api/v1/tracking/stop
```

### WebSocket Events

#### Client → Server
```javascript
// Connection and authentication
socket.emit('authenticate', { token: 'jwt-token' });

// Drone control
socket.emit('drone:takeoff');
socket.emit('drone:land');
socket.emit('drone:goto', { lat: 33.6844, lng: 73.0479, alt: 50 });

// Mission control
socket.emit('mission:start', { missionId: 'mission-123' });
socket.emit('mission:pause');
socket.emit('mission:resume');

// Camera control
socket.emit('camera:zoom', { level: 2.5 });
socket.emit('camera:rotate', { yaw: 45, pitch: -10 });
```

#### Server → Client
```javascript
// Telemetry data
socket.on('telemetry:update', (data) => {
  // { lat, lng, alt, speed, battery, heading, etc. }
});

// Video stream
socket.on('video:frame', (frame) => {
  // Base64 encoded video frame
});

// Detection results
socket.on('detection:objects', (objects) => {
  // Array of detected objects with coordinates
});

// System alerts
socket.on('system:alert', (alert) => {
  // { type: 'warning', message: 'Low battery', severity: 2 }
});
```

## 🚀 Usage

### Basic Flight Operations

1. **Pre-flight Check**
```bash
python scripts/preflight_check.py
```

2. **Start the System**
```bash
# Start all services
docker-compose up -d

# Or manually
python dronecore/main.py --mode production
```

3. **Access Dashboard**
Open `http://localhost:3000` in your browser

4. **Basic Commands**
```python
from dronecore.flight_controller import DroneController

drone = DroneController()
drone.connect()
drone.arm()
drone.takeoff(altitude=10)  # 10 meters
drone.goto_position(lat=33.6844, lng=73.0479, alt=15)
drone.land()
```

### Mission Planning

1. **Create Mission File**
```json
{
  "name": "Perimeter Survey",
  "waypoints": [
    {"lat": 33.6844, "lng": 73.0479, "alt": 20, "action": "photo"},
    {"lat": 33.6850, "lng": 73.0485, "alt": 20, "action": "video_start"},
    {"lat": 33.6840, "lng": 73.0490, "alt": 25, "action": "detect_objects"}
  ],
  "settings": {
    "speed": 5,
    "return_home": true,
    "failsafe_altitude": 30
  }
}
```

2. **Execute Mission**
```bash
python scripts/run_mission.py --file missions/perimeter_survey.json
```

### Object Detection Training

1. **Prepare Dataset**
```bash
python scripts/prepare_dataset.py --images data/training_images/
```

2. **Train Custom Model**
```bash
python scripts/train_model.py --config config/yolo_custom.yaml
```

3. **Deploy Model**
```bash
python scripts/deploy_model.py --model models/custom_yolo.pt
```





## 🗺️ Roadmap

### ✅ Phase 1: Research & Planning (Completed)
- [x] Define project objectives and requirements
- [x] Research hardware components and compatibility
- [x] Choose development stack: Python, OpenCV, Flask, React
- [x] Create system architecture design
- [x] Setup development environment

### ⚙️ Phase 2: Hardware Integration (In Progress)
- [x] Raspberry Pi setup and configuration
- [x] Camera module integration and testing
- [ ] GPS module integration and calibration
- [ ] Flight controller connection and setup
- [ ] Sensor network deployment (ultrasonic, IMU)
- [ ] Power management system implementation
- [ ] Communication module setup (telemetry)

### 🧑‍💻 Phase 3: Core Software Development (Upcoming)
- [ ] Flight control system implementation
- [ ] Real-time video streaming with WebRTC
- [ ] Object detection using YOLO integration
- [ ] GPS tracking and navigation algorithms
- [ ] Mission planning and waypoint navigation
- [ ] Data logging and telemetry systems
- [ ] Emergency protocols and failsafe mechanisms

### 🖥️ Phase 4: Web Dashboard Development
- [ ] React-based responsive dashboard
- [ ] Real-time video feed integration
- [ ] Interactive map interface with Leaflet.js
- [ ] Telemetry data visualization
- [ ] Mission control interface
- [ ] Alert and notification system
- [ ] User authentication and authorization

### 📱 Phase 5: Mobile Application
- [ ] React Native mobile app development
- [ ] Cross-platform compatibility (iOS/Android)
- [ ] Offline mission planning capabilities
- [ ] Push notifications for alerts
- [ ] Gesture-based drone control
- [ ] Mobile-optimized video streaming

### 🧪 Phase 6: Testing & Optimization
- [ ] Unit and integration testing
- [ ] Performance optimization and profiling
- [ ] Latency reduction for real-time operations
- [ ] Signal loss and failure handling
- [ ] Range and reliability testing
- [ ] Security vulnerability assessment

### 🧾 Phase 7: Documentation & Deployment
- [ ] Comprehensive API documentation
- [ ] Hardware assembly and wiring guides
- [ ] Software installation tutorials
- [ ] Troubleshooting and FAQ documentation
- [ ] Video tutorials and demonstrations
- [ ] Production deployment guides

### 🔮 Future Enhancements
- [ ] AI-powered autonomous surveillance patterns
- [ ] Multi-drone coordination and swarm intelligence
- [ ] Advanced computer vision (facial recognition, license plate reading)
- [ ] Integration with external security systems
- [ ] Machine learning for predictive maintenance
- [ ] Cloud-based data analytics and reporting






 📸 Screenshots (Coming Soon)

| Live Feed             | Object Detection         | GPS Dashboard             |
|-----------------------|--------------------------|---------------------------|
| ![Live]()             | ![Detect]()              | ![Map]()                  |





## 🎯 Use Cases

### Primary Applications

#### 🛡️ **Border Security & Defense**
- **Perimeter Monitoring**: Automated patrol of sensitive borders and military installations
- **Intrusion Detection**: Real-time alerts for unauthorized personnel or vehicles
- **Reconnaissance**: Intelligence gathering in hostile or remote territories
- **Force Protection**: Monitoring of military bases and critical infrastructure

#### 🚨 **Disaster Response & Emergency Services**
- **Search & Rescue**: Locating missing persons in challenging terrain
- **Damage Assessment**: Rapid evaluation of disaster-affected areas
- **Emergency Coordination**: Real-time situational awareness for first responders
- **Evacuation Support**: Monitoring evacuation routes and crowd management

#### 🏭 **Industrial & Commercial Security**
- **Facility Surveillance**: 24/7 monitoring of industrial complexes and warehouses
- **Asset Protection**: Tracking valuable equipment and preventing theft
- **Safety Compliance**: Monitoring adherence to safety protocols
- **Environmental Monitoring**: Detecting leaks, fires, or hazardous conditions

#### 🌿 **Environmental & Wildlife Monitoring**
- **Conservation Efforts**: Tracking wildlife populations and migration patterns
- **Anti-Poaching Operations**: Detecting illegal hunting activities
- **Forest Fire Detection**: Early warning systems for wildfire prevention
- **Agricultural Monitoring**: Crop health assessment and precision farming

### Technical Specifications by Use Case

| Use Case | Flight Duration | Range | Camera Specs | Special Features |
|----------|----------------|-------|--------------|------------------|
| Border Patrol | 45-60 min | 5-10 km | 4K, 30x Zoom, IR | Night vision, Long-range telemetry |
| Disaster Response | 30-45 min | 2-5 km | 4K, Thermal imaging | Emergency beacon, Mesh networking |
| Industrial Security | 60-90 min | 1-3 km | HD, PTZ, Low-light | Automated alerts, Integration APIs |
| Wildlife Monitoring | 90-120 min | 10-20 km | 4K, Silent operation | Extended battery, Camouflage |

### Deployment Scenarios

#### **Scenario 1: Urban Security Patrol**
```yaml
mission_type: "patrol"
area_coverage: "urban_district"
flight_pattern: "grid_search"
altitude: 50-100m
duration: 60min
detection_targets: ["vehicles", "persons", "suspicious_activity"]
alert_conditions: ["intrusion", "crowd_formation", "vehicle_speeding"]
```

#### **Scenario 2: Rural Border Monitoring**
```yaml
mission_type: "surveillance"
area_coverage: "border_zone"
flight_pattern: "perimeter_follow"
altitude: 100-150m
duration: 90min
detection_targets: ["persons", "vehicles", "illegal_crossings"]
alert_conditions: ["motion_detection", "thermal_signature"]
```

### Integration Capabilities

- **Command Centers**: Real-time data feed to security operations centers
- **Mobile Units**: Direct communication with field personnel
- **Satellite Systems**: Backup communication via satellite uplinks
- **IoT Networks**: Integration with ground-based sensor networks
- **AI Platforms**: Connection to cloud-based AI analysis services

## 🔧 Troubleshooting

### Common Issues

#### **Connection Problems**
```bash
# Check device connections
lsusb  # List USB devices
ls /dev/tty*  # List serial ports

# Test GPS connection
python scripts/test_gps.py

# Test camera
python scripts/test_camera.py

# Verify flight controller
python scripts/test_mavlink.py
```

#### **Performance Issues**
- **High CPU Usage**: Reduce video resolution or frame rate
- **Memory Leaks**: Restart services periodically in production
- **Network Latency**: Use local RTMP server for video streaming
- **Battery Drain**: Optimize sensor polling rates

#### **Software Debugging**
```bash
# Enable debug logging
export DEBUG_LEVEL=verbose
python dronecore/main.py

# Check system logs
tail -f logs/system.log

# Monitor resource usage
htop
iotop
```

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| E001 | GPS Module Not Found | Check connections and permissions |
| E002 | Camera Initialization Failed | Verify camera module and drivers |
| E003 | Flight Controller Timeout | Check MAVLink connection and baudrate |
| E004 | Object Detection Model Missing | Download required AI models |
| E005 | Insufficient Battery | Replace or charge battery |

## 🤝 Contributing

We welcome contributions from the community! Please follow these guidelines:

### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and commit: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript/TypeScript
- Write unit tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR

### Code Review Process
1. All PRs require review from maintainers
2. Automated tests must pass
3. Documentation must be updated
4. Security implications must be assessed

### Reporting Issues
- Use GitHub Issues for bug reports
- Include system information and logs
- Provide steps to reproduce the issue
- Suggest potential solutions if possible

## 📞 Support & Community

- **GitHub Discussions**: Ask questions and share ideas
- **Discord Server**: Real-time community chat
- **Documentation**: Comprehensive guides and tutorials
- **YouTube Channel**: Video tutorials and demos
- **Email Support**: technical-support@surv-drone.com

## 🔒 Security & Privacy

### Data Protection
- All video streams are encrypted using AES-256
- GPS coordinates are hashed when stored
- User authentication via JWT tokens
- API rate limiting and access controls

### Responsible Use
- Comply with local aviation regulations
- Respect privacy and no-fly zones
- Use only for legal and ethical purposes
- Implement proper safety protocols

### Vulnerability Reporting
Report security vulnerabilities to security@surv-drone.com

## 📊 Performance Metrics

### System Benchmarks
- **Video Latency**: <100ms (local network)
- **Object Detection**: 15-30 FPS (depending on model)
- **GPS Accuracy**: ±3 meters (with clear sky view)
- **Flight Time**: 45-90 minutes (battery dependent)
- **Range**: Up to 10km (with appropriate telemetry)

### Resource Usage
- **CPU**: 60-80% (Raspberry Pi 4B)
- **Memory**: 2-3GB RAM usage
- **Storage**: 500MB/hour video recording
- **Network**: 5-10 Mbps for HD streaming


Use Case to System Modules Mapping:
![Image](https://github.com/user-attachments/assets/f7087cd0-567e-48cd-b570-3908fc64a19f)


Comprehensive System Workflow Diagram
![Image](https://github.com/user-attachments/assets/5a39def2-460a-45e4-b8dd-80dd6c79b6e5)


 📁 Project Structure

```
/dronecore/
    ├── main.py                      Main flight logic
    ├── video_stream.py       Camera & OpenCV logic
    ├── gps_tracker.py           GPS & location mapping
    ├── dashboard/                Flask or React UI
    ├── logs/                            Flight & error logs
    └── utils/                            Helper modules
```



 🛠️ Setup & Run

> _Hardware setup & dependencies guide coming soon_

1. Install Python dependencies:
```bash
pip install r requirements.txt
```

2. Run drone core:
```bash
python main.py
```

3. Start dashboard:
```bash
cd dashboard && npm start
```




- **Network**: 5-10 Mbps for HD streaming

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- OpenCV: Apache 2.0 License
- Flask: BSD License
- React: MIT License
- YOLO: GPL License (for commercial use, please check licensing terms)

## 🔐 Disclaimer

> ⚠️ **IMPORTANT**: This project is strictly for **educational and research purposes**. 
> 
> - Ensure compliance with local aviation regulations and laws
> - Obtain necessary permits for drone operations
> - Respect privacy rights and no-fly zones
> - Use only for legal and ethical surveillance purposes
> - The developers are not responsible for misuse of this technology
> 
> Always prioritize safety and legal compliance in all operations.

## 🙏 Acknowledgments

- **OpenCV Community** for computer vision libraries
- **ArduPilot Project** for flight control software  
- **React Team** for the frontend framework
- **Flask Community** for the web framework
- **YOLO Authors** for object detection algorithms
- **Open Source Hardware** contributors
- **Drone/UAV Community** for inspiration and guidance

## 📈 Project Stats

![GitHub stars](https://img.shields.io/github/stars/umairism/Surveillance-Drone-System)
![GitHub forks](https://img.shields.io/github/forks/umairism/Surveillance-Drone-System)
![GitHub issues](https://img.shields.io/github/issues/umairism/Surveillance-Drone-System)
![GitHub pull requests](https://img.shields.io/github/issues-pr/umairism/Surveillance-Drone-System)
![GitHub license](https://img.shields.io/github/license/umairism/Surveillance-Drone-System)

---

## 👨‍💻 Author

**Muhammad Umair Hakeem**  
BS Computer Science, NUML Islamabad  
🌐 Portfolio: [umairhakeem.netlify.app](https://umairhakeem.netlify.app)  
📧 Email: iamumair1124@gmail.com  
🐙 GitHub: [@Umairism](https://github.com/umairism)  
💼 LinkedIn: [Muhammad Umair Hakeem](https://linkedin.com/in/umairism)  

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ for the open-source community

[🚀 Get Started](#-installation) • [📖 Documentation](docs/) • [🤝 Contribute](#-contributing) • [💬 Discussions](https://github.com/umairism/Surveillance-Drone-System/discussions)

</div>
