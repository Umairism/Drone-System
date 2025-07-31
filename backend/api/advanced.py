"""
API endpoints for Logs, Celebrations, and Mobile compatibility.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json

# Create blueprints
logs_bp = Blueprint('logs', __name__, url_prefix='/api/logs')
celebrations_bp = Blueprint('celebrations', __name__, url_prefix='/api/celebrations')
mobile_bp = Blueprint('mobile', __name__, url_prefix='/api/mobile')


# =============================================================================
# LOGS API ENDPOINTS
# =============================================================================

@logs_bp.route('/system', methods=['GET'])
def get_system_logs():
    """Get system logs with filtering options."""
    from utils.logger import get_logger
    
    logger = get_logger()
    if not logger:
        return jsonify({"error": "Logger not initialized"}), 500
    
    # Get query parameters
    log_type = request.args.get('type')
    limit = int(request.args.get('limit', 100))
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')
    
    # Parse time filters
    start_time = None
    end_time = None
    
    if start_time_str:
        try:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid start_time format"}), 400
    
    if end_time_str:
        try:
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid end_time format"}), 400
    
    # Convert log_type string to enum
    from utils.logger import LogType
    log_type_enum = None
    if log_type:
        try:
            log_type_enum = LogType(log_type)
        except ValueError:
            return jsonify({"error": f"Invalid log type: {log_type}"}), 400
    
    # Get logs
    try:
        logs = logger.get_logs(log_type_enum, start_time, end_time, limit)
        return jsonify({
            "success": True,
            "logs": logs,
            "count": len(logs),
            "filters": {
                "type": log_type,
                "start_time": start_time_str,
                "end_time": end_time_str,
                "limit": limit
            }
        })
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve logs: {str(e)}"}), 500


@logs_bp.route('/summary', methods=['GET'])
def get_log_summary():
    """Get log summary statistics."""
    from utils.logger import get_logger
    
    logger = get_logger()
    if not logger:
        return jsonify({"error": "Logger not initialized"}), 500
    
    try:
        summary = logger.get_log_summary()
        return jsonify({
            "success": True,
            "summary": summary
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get log summary: {str(e)}"}), 500


@logs_bp.route('/export', methods=['POST'])
def export_logs():
    """Export logs for download."""
    from utils.logger import get_logger
    import zipfile
    import io
    from flask import send_file
    
    logger = get_logger()
    if not logger:
        return jsonify({"error": "Logger not initialized"}), 500
    
    data = request.get_json() or {}
    log_types = data.get('log_types', [])
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    try:
        # Create zip file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            from utils.logger import LogType
            
            # Export requested log types
            for log_type_str in log_types:
                try:
                    log_type = LogType(log_type_str)
                    logs = logger.get_logs(log_type, limit=10000)
                    
                    # Convert to JSON
                    log_data = json.dumps(logs, indent=2, default=str)
                    zip_file.writestr(f"{log_type_str}_logs.json", log_data)
                except ValueError:
                    continue
        
        zip_buffer.seek(0)
        
        return send_file(
            io.BytesIO(zip_buffer.read()),
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'drone_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        )
    
    except Exception as e:
        return jsonify({"error": f"Failed to export logs: {str(e)}"}), 500


# =============================================================================
# CELEBRATIONS API ENDPOINTS
# =============================================================================

@celebrations_bp.route('/achievements', methods=['GET'])
def get_achievements():
    """Get available achievements."""
    from utils.celebrations import get_celebration_system
    
    celebration_system = get_celebration_system()
    if not celebration_system:
        return jsonify({"error": "Celebration system not initialized"}), 500
    
    achievement_type = request.args.get('type')
    earned_only = request.args.get('earned_only', 'false').lower() == 'true'
    user_id = request.args.get('user_id', 'default_user')
    
    try:
        from utils.celebrations import AchievementType
        type_filter = None
        if achievement_type:
            try:
                type_filter = AchievementType(achievement_type)
            except ValueError:
                return jsonify({"error": f"Invalid achievement type: {achievement_type}"}), 400
        
        achievements = celebration_system.get_achievements_by_type(
            type_filter, earned_only, user_id
        )
        
        # Convert to dict format
        achievements_data = []
        for achievement in achievements:
            # Handle enum conversion safely
            achievement_type = achievement.type
            if hasattr(achievement_type, 'value'):
                type_value = achievement_type.value
            else:
                # Handle string format like "AchievementType.FLIGHT"
                type_value = str(achievement_type).split('.')[-1].lower() if '.' in str(achievement_type) else str(achievement_type)
                
            achievement_tier = achievement.tier
            if hasattr(achievement_tier, 'value'):
                tier_value = achievement_tier.value
            else:
                # Handle string format like "AchievementTier.BRONZE"
                tier_value = str(achievement_tier).split('.')[-1].lower() if '.' in str(achievement_tier) else str(achievement_tier)
            
            ach_dict = {
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "type": type_value,
                "tier": tier_value,
                "reward_points": achievement.reward_points,
                "icon": achievement.icon,
                "hidden": achievement.hidden
            }
            achievements_data.append(ach_dict)
        
        return jsonify({
            "success": True,
            "achievements": achievements_data,
            "count": len(achievements_data)
        })
    
    except Exception as e:
        return jsonify({"error": f"Failed to get achievements: {str(e)}"}), 500


@celebrations_bp.route('/user/<user_id>/progress', methods=['GET'])
def get_user_progress(user_id):
    """Get user progress and achievements."""
    from utils.celebrations import get_celebration_system
    
    celebration_system = get_celebration_system()
    if not celebration_system:
        return jsonify({"error": "Celebration system not initialized"}), 500
    
    try:
        dashboard = celebration_system.get_user_dashboard(user_id)
        return jsonify({
            "success": True,
            "dashboard": dashboard
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get user progress: {str(e)}"}), 500


@celebrations_bp.route('/user/<user_id>/stats', methods=['POST'])
def update_user_stats(user_id):
    """Update user statistics and check for new achievements."""
    from utils.celebrations import get_celebration_system
    
    celebration_system = get_celebration_system()
    if not celebration_system:
        return jsonify({"error": "Celebration system not initialized"}), 500
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        new_achievements = celebration_system.update_user_stats(user_id, data)
        
        # Convert achievements to dict format
        achievements_data = []
        for achievement in new_achievements:
            achievements_data.append({
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "tier": achievement.tier.value,
                "reward_points": achievement.reward_points,
                "icon": achievement.icon
            })
        
        return jsonify({
            "success": True,
            "new_achievements": achievements_data,
            "achievements_count": len(achievements_data)
        })
    
    except Exception as e:
        return jsonify({"error": f"Failed to update user stats: {str(e)}"}), 500


@celebrations_bp.route('/user/<user_id>/celebrations', methods=['GET'])
def get_pending_celebrations(user_id):
    """Get pending celebrations for user."""
    from utils.celebrations import get_celebration_system
    
    celebration_system = get_celebration_system()
    if not celebration_system:
        return jsonify({"error": "Celebration system not initialized"}), 500
    
    try:
        celebrations = celebration_system.get_pending_celebrations(user_id)
        return jsonify({
            "success": True,
            "celebrations": celebrations,
            "count": len(celebrations)
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get celebrations: {str(e)}"}), 500


@celebrations_bp.route('/celebration/<celebration_id>/mark-shown', methods=['POST'])
def mark_celebration_shown(celebration_id):
    """Mark celebration as shown."""
    from utils.celebrations import get_celebration_system
    
    celebration_system = get_celebration_system()
    if not celebration_system:
        return jsonify({"error": "Celebration system not initialized"}), 500
    
    try:
        celebration_system.mark_celebration_shown(celebration_id)
        return jsonify({"success": True, "message": "Celebration marked as shown"})
    except Exception as e:
        return jsonify({"error": f"Failed to mark celebration: {str(e)}"}), 500


@celebrations_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get user leaderboard."""
    from utils.celebrations import get_celebration_system
    
    celebration_system = get_celebration_system()
    if not celebration_system:
        return jsonify({"error": "Celebration system not initialized"}), 500
    
    limit = int(request.args.get('limit', 10))
    
    try:
        leaderboard = celebration_system.get_leaderboard(limit)
        return jsonify({
            "success": True,
            "leaderboard": leaderboard,
            "count": len(leaderboard)
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get leaderboard: {str(e)}"}), 500


# =============================================================================
# MOBILE API ENDPOINTS
# =============================================================================

@mobile_bp.route('/register', methods=['POST'])
def register_mobile_session():
    """Register a new mobile session."""
    from utils.mobile import get_mobile_compatibility
    
    mobile_system = get_mobile_compatibility()
    if not mobile_system:
        return jsonify({"error": "Mobile system not initialized"}), 500
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No device info provided"}), 400
    
    user_id = data.get('user_id', 'default_user')
    device_info = data.get('device_info', {})
    
    try:
        session_id = mobile_system.register_mobile_session(user_id, device_info)
        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Mobile session registered successfully"
        })
    except Exception as e:
        return jsonify({"error": f"Failed to register session: {str(e)}"}), 500


@mobile_bp.route('/status', methods=['GET'])
def get_mobile_status():
    """Get drone status optimized for mobile."""
    from utils.mobile import get_mobile_compatibility
    
    mobile_system = get_mobile_compatibility()
    if not mobile_system:
        return jsonify({"error": "Mobile system not initialized"}), 500
    
    try:
        status = mobile_system.get_mobile_optimized_status()
        return jsonify({
            "success": True,
            "status": status
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get mobile status: {str(e)}"}), 500


@mobile_bp.route('/telemetry', methods=['GET'])
def get_mobile_telemetry():
    """Get telemetry optimized for mobile."""
    from utils.mobile import get_mobile_compatibility
    
    mobile_system = get_mobile_compatibility()
    if not mobile_system:
        return jsonify({"error": "Mobile system not initialized"}), 500
    
    try:
        telemetry = mobile_system.get_mobile_optimized_telemetry()
        return jsonify({
            "success": True,
            "telemetry": telemetry
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get mobile telemetry: {str(e)}"}), 500


@mobile_bp.route('/dashboard/<session_id>', methods=['GET'])
def get_mobile_dashboard(session_id):
    """Get mobile dashboard data."""
    from utils.mobile import get_mobile_compatibility
    
    mobile_system = get_mobile_compatibility()
    if not mobile_system:
        return jsonify({"error": "Mobile system not initialized"}), 500
    
    try:
        dashboard = mobile_system.get_mobile_dashboard(session_id)
        return jsonify({
            "success": True,
            "dashboard": dashboard
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get mobile dashboard: {str(e)}"}), 500


@mobile_bp.route('/video-config', methods=['GET'])
def get_mobile_video_config():
    """Get video configuration for mobile."""
    from utils.mobile import get_mobile_compatibility
    
    mobile_system = get_mobile_compatibility()
    if not mobile_system:
        return jsonify({"error": "Mobile system not initialized"}), 500
    
    device_type = request.args.get('device_type', 'android')
    network_quality = request.args.get('network_quality', 'good')
    
    try:
        config = mobile_system.get_mobile_video_config(device_type, network_quality)
        return jsonify({
            "success": True,
            "video_config": config
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get video config: {str(e)}"}), 500


@mobile_bp.route('/control-layout', methods=['GET'])
def get_mobile_control_layout():
    """Get control layout for mobile."""
    from utils.mobile import get_mobile_compatibility
    
    mobile_system = get_mobile_compatibility()
    if not mobile_system:
        return jsonify({"error": "Mobile system not initialized"}), 500
    
    device_type = request.args.get('device_type', 'android')
    
    try:
        layout = mobile_system.get_mobile_control_layout(device_type)
        return jsonify({
            "success": True,
            "control_layout": layout
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get control layout: {str(e)}"}), 500


@mobile_bp.route('/mission/<mission_id>/offline', methods=['GET'])
def get_offline_mission_data(mission_id):
    """Get mission data for offline use."""
    from utils.mobile import get_mobile_compatibility
    
    mobile_system = get_mobile_compatibility()
    if not mobile_system:
        return jsonify({"error": "Mobile system not initialized"}), 500
    
    try:
        offline_data = mobile_system.get_offline_mission_data(mission_id)
        return jsonify({
            "success": True,
            "offline_data": offline_data
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get offline data: {str(e)}"}), 500


@mobile_bp.route('/settings/<session_id>', methods=['GET'])
def get_mobile_settings(session_id):
    """Get mobile app settings."""
    from utils.mobile import get_mobile_compatibility
    
    mobile_system = get_mobile_compatibility()
    if not mobile_system:
        return jsonify({"error": "Mobile system not initialized"}), 500
    
    try:
        settings = mobile_system.get_mobile_settings(session_id)
        return jsonify({
            "success": True,
            "settings": settings
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get settings: {str(e)}"}), 500


@mobile_bp.route('/settings/<session_id>', methods=['POST'])
def update_mobile_settings(session_id):
    """Update mobile app settings."""
    from utils.mobile import get_mobile_compatibility
    
    mobile_system = get_mobile_compatibility()
    if not mobile_system:
        return jsonify({"error": "Mobile system not initialized"}), 500
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No settings provided"}), 400
    
    try:
        success = mobile_system.update_mobile_settings(session_id, data)
        if success:
            return jsonify({
                "success": True,
                "message": "Settings updated successfully"
            })
        else:
            return jsonify({"error": "Failed to update settings"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update settings: {str(e)}"}), 500


@mobile_bp.route('/notification', methods=['POST'])
def create_mobile_notification():
    """Create a mobile push notification."""
    from utils.mobile import get_mobile_compatibility
    
    mobile_system = get_mobile_compatibility()
    if not mobile_system:
        return jsonify({"error": "Mobile system not initialized"}), 500
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No notification data provided"}), 400
    
    user_id = data.get('user_id', 'default_user')
    title = data.get('title', '')
    body = data.get('body', '')
    notification_type = data.get('type', 'info')
    priority = data.get('priority', 'normal')
    extra_data = data.get('data', {})
    
    try:
        notification_id = mobile_system.create_mobile_notification(
            user_id, title, body, notification_type, priority, extra_data
        )
        return jsonify({
            "success": True,
            "notification_id": notification_id,
            "message": "Notification created successfully"
        })
    except Exception as e:
        return jsonify({"error": f"Failed to create notification: {str(e)}"}), 500


def register_advanced_api_routes(app):
    """Register all advanced API routes."""
    app.register_blueprint(logs_bp)
    app.register_blueprint(celebrations_bp)
    app.register_blueprint(mobile_bp)
