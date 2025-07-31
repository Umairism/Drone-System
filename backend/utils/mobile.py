"""
Mobile App Compatibility System
Provides APIs and utilities optimized for mobile applications.
"""

import json
import base64
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import uuid
from flask import jsonify, request
from pathlib import Path


@dataclass
class MobileSession:
    """Mobile app session data."""
    session_id: str
    user_id: str
    device_type: str  # ios, android
    device_id: str
    app_version: str
    last_activity: str
    push_token: Optional[str] = None
    settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.settings is None:
            self.settings = {}


@dataclass
class MobileNotification:
    """Mobile push notification data."""
    id: str
    user_id: str
    title: str
    body: str
    type: str  # alert, achievement, mission, system
    priority: str  # low, normal, high, critical
    data: Dict[str, Any]
    scheduled_at: str
    sent_at: Optional[str] = None
    delivered_at: Optional[str] = None


class MobileCompatibility:
    """Handles mobile app compatibility and optimizations."""
    
    def __init__(self):
        self.data_dir = Path("data/mobile")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.sessions_file = self.data_dir / "sessions.json"
        self.notifications_file = self.data_dir / "notifications.json"
        
        self.active_sessions = self._load_sessions()
        self.notification_queue = self._load_notifications()
    
    def _load_sessions(self) -> Dict[str, MobileSession]:
        """Load mobile sessions."""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r') as f:
                    data = json.load(f)
                    return {
                        sid: MobileSession(**session_data)
                        for sid, session_data in data.items()
                    }
            except Exception:
                pass
        return {}
    
    def _save_sessions(self):
        """Save mobile sessions."""
        data = {sid: asdict(session) for sid, session in self.active_sessions.items()}
        with open(self.sessions_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load_notifications(self) -> List[MobileNotification]:
        """Load notification queue."""
        if self.notifications_file.exists():
            try:
                with open(self.notifications_file, 'r') as f:
                    data = json.load(f)
                    return [MobileNotification(**notif) for notif in data]
            except Exception:
                pass
        return []
    
    def _save_notifications(self):
        """Save notification queue."""
        data = [asdict(notif) for notif in self.notification_queue]
        with open(self.notifications_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def register_mobile_session(self, user_id: str, device_info: Dict[str, Any]) -> str:
        """Register a new mobile session."""
        session_id = str(uuid.uuid4())
        
        session = MobileSession(
            session_id=session_id,
            user_id=user_id,
            device_type=device_info.get("device_type", "unknown"),
            device_id=device_info.get("device_id", "unknown"),
            app_version=device_info.get("app_version", "1.0.0"),
            last_activity=datetime.now(timezone.utc).isoformat(),
            push_token=device_info.get("push_token"),
            settings=device_info.get("settings", {})
        )
        
        self.active_sessions[session_id] = session
        self._save_sessions()
        
        return session_id
    
    def update_session_activity(self, session_id: str):
        """Update session last activity."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].last_activity = datetime.now(timezone.utc).isoformat()
            self._save_sessions()
    
    def get_mobile_optimized_status(self) -> Dict[str, Any]:
        """Get mobile-optimized drone status."""
        try:
            from dynamic_data import drone_data_manager as data_manager
            
            if not data_manager:
                return {"error": "Data manager not available"}
            
            status = data_manager.get_drone_status()
            
            # Mobile-optimized format
            mobile_status = {
                "basic": {
                    "armed": status.get("armed", False),
                    "flying": status.get("flying", False),
                    "battery": status.get("battery_level", 0),
                    "signal": status.get("signals", {}).get("controller", 0),
                    "altitude": round(status.get("altitude", 0), 1),
                    "speed": round(status.get("speed", 0), 1)
                },
                "location": {
                    "lat": status.get("location", {}).get("lat", 0),
                    "lng": status.get("location", {}).get("lng", 0),
                    "heading": status.get("heading", 0)
                },
                "alerts": self._get_mobile_alerts(status.get("alerts", [])),
                "last_updated": status.get("timestamp")
            }
            
            return mobile_status
        except Exception as e:
            return {"error": f"Failed to get mobile status: {str(e)}"}
    
    def _get_mobile_alerts(self, alerts: List[Dict]) -> List[Dict]:
        """Convert alerts to mobile-friendly format."""
        mobile_alerts = []
        
        for alert in alerts[-5:]:  # Last 5 alerts only
            mobile_alerts.append({
                "id": alert.get("id"),
                "type": alert.get("type"),
                "message": alert.get("message")[:100],  # Truncate for mobile
                "severity": alert.get("severity"),
                "time": alert.get("timestamp")
            })
        
        return mobile_alerts
    
    def get_mobile_telemetry(self) -> Dict[str, Any]:
        """Get mobile-optimized telemetry data."""
        try:
            from dynamic_data import drone_data_manager as data_manager
            
            if not data_manager:
                return {"error": "Data manager not available"}
            
            telemetry = data_manager.get_telemetry()
        
            # Mobile-optimized telemetry
            mobile_telemetry = {
                "essential": {
                    "battery_voltage": round(telemetry.get("battery_voltage", 0), 2),
                    "battery_current": round(telemetry.get("battery_current", 0), 2),
                    "battery_remaining": telemetry.get("battery_remaining", 0),
                    "gps_satellites": telemetry.get("gps_satellites", 0),
                    "gps_fix": telemetry.get("gps_fix_type", "No Fix"),
                    "signal_strength": telemetry.get("signal_strength", 0)
                },
                "flight": {
                    "altitude": round(telemetry.get("altitude", 0), 1),
                    "ground_speed": round(telemetry.get("ground_speed", 0), 1),
                    "vertical_speed": round(telemetry.get("vertical_speed", 0), 1),
                    "heading": round(telemetry.get("heading", 0), 1)
                },
                "sensors": {
                    "temperature": round(telemetry.get("temperature", 0), 1),
                    "pressure": round(telemetry.get("pressure", 0), 1),
                    "humidity": round(telemetry.get("humidity", 0), 1)
                },
                "timestamp": telemetry.get("timestamp")
            }
            
            return mobile_telemetry
        except Exception as e:
            return {"error": f"Failed to get mobile telemetry: {str(e)}"}
    
    def get_mobile_mission_summary(self, mission_id: str = None) -> Dict[str, Any]:
        """Get mission summary optimized for mobile."""
        from api.missions import get_missions_data
        
        missions = get_missions_data()
        
        if mission_id:
            mission = next((m for m in missions if m["id"] == mission_id), None)
            if not mission:
                return {"error": "Mission not found"}
            
            return {
                "id": mission["id"],
                "name": mission["name"][:30],  # Truncate for mobile
                "status": mission["status"],
                "progress": mission.get("progress", 0),
                "waypoints_completed": f"{mission.get('current_waypoint', 0)}/{len(mission.get('waypoints', []))}",
                "estimated_time": mission.get("estimated_completion_time"),
                "distance_covered": round(mission.get("distance_covered", 0), 1),
                "objects_detected": mission.get("objects_detected", 0)
            }
        else:
            # Return summary of all missions
            active_missions = [m for m in missions if m["status"] == "active"]
            completed_missions = [m for m in missions if m["status"] == "completed"]
            
            return {
                "active_count": len(active_missions),
                "completed_count": len(completed_missions),
                "total_count": len(missions),
                "active_missions": [
                    {
                        "id": m["id"],
                        "name": m["name"][:20],
                        "progress": m.get("progress", 0),
                        "status": m["status"]
                    }
                    for m in active_missions[:3]  # Show only first 3
                ]
            }
    
    def create_mobile_notification(self, user_id: str, title: str, body: str,
                                 notification_type: str = "info", priority: str = "normal",
                                 data: Dict[str, Any] = None) -> str:
        """Create a mobile push notification."""
        notification_id = str(uuid.uuid4())
        
        notification = MobileNotification(
            id=notification_id,
            user_id=user_id,
            title=title,
            body=body,
            type=notification_type,
            priority=priority,
            data=data or {},
            scheduled_at=datetime.now(timezone.utc).isoformat()
        )
        
        self.notification_queue.append(notification)
        self._save_notifications()
        
        # Try to send immediately
        self._try_send_notification(notification)
        
        return notification_id
    
    def _try_send_notification(self, notification: MobileNotification):
        """Attempt to send push notification (placeholder implementation)."""
        # In a real implementation, this would integrate with:
        # - Firebase Cloud Messaging (FCM) for Android
        # - Apple Push Notification Service (APNs) for iOS
        
        # For now, just mark as sent
        notification.sent_at = datetime.now(timezone.utc).isoformat()
        self._save_notifications()
    
    def get_mobile_video_config(self, device_type: str, network_quality: str = "good") -> Dict[str, Any]:
        """Get video streaming configuration optimized for mobile device."""
        configs = {
            "ios": {
                "good": {
                    "resolution": "1280x720",
                    "fps": 30,
                    "bitrate": 2000,
                    "codec": "h264",
                    "format": "hls"
                },
                "poor": {
                    "resolution": "854x480",
                    "fps": 20,
                    "bitrate": 800,
                    "codec": "h264",
                    "format": "hls"
                }
            },
            "android": {
                "good": {
                    "resolution": "1280x720",
                    "fps": 30,
                    "bitrate": 2000,
                    "codec": "h264",
                    "format": "webrtc"
                },
                "poor": {
                    "resolution": "854x480",
                    "fps": 20,
                    "bitrate": 800,
                    "codec": "h264",
                    "format": "webrtc"
                }
            }
        }
        
        device_config = configs.get(device_type, configs["android"])
        return device_config.get(network_quality, device_config["good"])
    
    def get_mobile_control_layout(self, device_type: str) -> Dict[str, Any]:
        """Get control interface layout optimized for mobile device."""
        layouts = {
            "ios": {
                "primary_controls": [
                    {"id": "arm", "label": "ARM", "type": "toggle", "position": {"x": 0.1, "y": 0.8}},
                    {"id": "takeoff", "label": "TAKEOFF", "type": "button", "position": {"x": 0.9, "y": 0.8}},
                    {"id": "land", "label": "LAND", "type": "button", "position": {"x": 0.9, "y": 0.9}},
                    {"id": "emergency", "label": "EMERGENCY", "type": "button", "position": {"x": 0.5, "y": 0.95}}
                ],
                "joystick": {
                    "enabled": True,
                    "position": {"x": 0.2, "y": 0.6},
                    "size": 120
                },
                "telemetry_panel": {
                    "position": {"x": 0.0, "y": 0.0},
                    "size": {"width": 1.0, "height": 0.3}
                }
            },
            "android": {
                "primary_controls": [
                    {"id": "arm", "label": "ARM", "type": "toggle", "position": {"x": 0.1, "y": 0.85}},
                    {"id": "takeoff", "label": "TAKEOFF", "type": "button", "position": {"x": 0.9, "y": 0.85}},
                    {"id": "land", "label": "LAND", "type": "button", "position": {"x": 0.9, "y": 0.95}},
                    {"id": "emergency", "label": "EMERGENCY", "type": "button", "position": {"x": 0.5, "y": 0.98}}
                ],
                "joystick": {
                    "enabled": True,
                    "position": {"x": 0.15, "y": 0.55},
                    "size": 100
                },
                "telemetry_panel": {
                    "position": {"x": 0.0, "y": 0.0},
                    "size": {"width": 1.0, "height": 0.25}
                }
            }
        }
        
        return layouts.get(device_type, layouts["android"])
    
    def get_offline_mission_data(self, mission_id: str) -> Dict[str, Any]:
        """Get mission data optimized for offline mobile operation."""
        from api.missions import get_missions_data
        
        missions = get_missions_data()
        mission = next((m for m in missions if m["id"] == mission_id), None)
        
        if not mission:
            return {"error": "Mission not found"}
        
        # Optimize for offline use
        offline_data = {
            "id": mission["id"],
            "name": mission["name"],
            "waypoints": mission.get("waypoints", []),
            "settings": mission.get("settings", {}),
            "emergency_procedures": {
                "return_to_home": True,
                "landing_sites": mission.get("emergency_landing_sites", []),
                "contact_info": mission.get("emergency_contact", "")
            },
            "offline_maps": self._prepare_offline_maps(mission.get("waypoints", [])),
            "cached_at": datetime.now(timezone.utc).isoformat()
        }
        
        return offline_data
    
    def _prepare_offline_maps(self, waypoints: List[Dict]) -> Dict[str, Any]:
        """Prepare offline map data for waypoints."""
        if not waypoints:
            return {}
        
        # Calculate bounding box
        lats = [wp.get("lat", 0) for wp in waypoints]
        lngs = [wp.get("lng", 0) for wp in waypoints]
        
        return {
            "bounds": {
                "north": max(lats) + 0.01,
                "south": min(lats) - 0.01,
                "east": max(lngs) + 0.01,
                "west": min(lngs) - 0.01
            },
            "zoom_level": 15,
            "tile_format": "png",
            "cache_size_mb": 50
        }
    
    def get_mobile_settings(self, session_id: str) -> Dict[str, Any]:
        """Get mobile app settings."""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        default_settings = {
            "notifications": {
                "push_enabled": True,
                "alert_types": ["critical", "mission", "achievement"],
                "quiet_hours": {"start": "22:00", "end": "07:00"}
            },
            "display": {
                "theme": "dark",
                "map_type": "satellite",
                "units": "metric",
                "language": "en"
            },
            "controls": {
                "joystick_sensitivity": 0.7,
                "button_haptic": True,
                "gesture_enabled": True,
                "voice_commands": False
            },
            "video": {
                "quality": "auto",
                "auto_record": False,
                "save_to_gallery": True
            },
            "offline": {
                "auto_sync": True,
                "cache_size_mb": 500,
                "download_maps": True
            }
        }
        
        # Merge with user settings
        user_settings = session.settings or {}
        for category, settings in default_settings.items():
            if category in user_settings:
                settings.update(user_settings[category])
        
        return default_settings
    
    def update_mobile_settings(self, session_id: str, settings: Dict[str, Any]) -> bool:
        """Update mobile app settings."""
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        if not session.settings:
            session.settings = {}
        
        # Update settings
        for category, category_settings in settings.items():
            if category not in session.settings:
                session.settings[category] = {}
            session.settings[category].update(category_settings)
        
        self._save_sessions()
        return True
    
    def get_mobile_dashboard(self, session_id: str) -> Dict[str, Any]:
        """Get mobile dashboard data."""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Get celebration system data
        from utils.celebrations import get_celebration_system
        celebration_system = get_celebration_system()
        
        if celebration_system:
            user_dashboard = celebration_system.get_user_dashboard(session.user_id)
        else:
            user_dashboard = {"level": 1, "experience": 0, "total_points": 0}
        
        dashboard = {
            "user": {
                "id": session.user_id,
                "level": user_dashboard.get("level", 1),
                "experience": user_dashboard.get("experience", 0),
                "points": user_dashboard.get("total_points", 0),
                "achievements": user_dashboard.get("achievements_earned", 0)
            },
            "status": self.get_mobile_optimized_status(),
            "missions": self.get_mobile_mission_summary(),
            "notifications": len(self.get_pending_notifications(session.user_id)),
            "celebrations": user_dashboard.get("pending_celebrations", []),
            "quick_actions": [
                {"id": "arm", "label": "Arm Drone", "enabled": True},
                {"id": "mission", "label": "Start Mission", "enabled": True},
                {"id": "video", "label": "Start Recording", "enabled": True}
            ]
        }
        
        return dashboard
    
    def get_pending_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending notifications for user."""
        pending = []
        
        for notification in self.notification_queue:
            if (notification.user_id == user_id and 
                not notification.sent_at):
                pending.append({
                    "id": notification.id,
                    "title": notification.title,
                    "body": notification.body,
                    "type": notification.type,
                    "priority": notification.priority,
                    "data": notification.data
                })
        
        return pending


# Global mobile compatibility instance
mobile_compatibility = None

def init_mobile_compatibility():
    """Initialize the global mobile compatibility system."""
    global mobile_compatibility
    mobile_compatibility = MobileCompatibility()
    return mobile_compatibility

def get_mobile_compatibility():
    """Get the global mobile compatibility instance."""
    return mobile_compatibility
