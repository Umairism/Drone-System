"""
Flask Backend Entry Point
Starts the Flask application with SocketIO support.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def main():
    """Main entry point for the Flask backend."""
    
    # Get configuration from environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create Flask app
    app, socketio = create_app(config_name)
    
    # Get host and port from environment or use defaults
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = config_name == 'development'
    
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                  Surveillance Drone System                  ║
    ║                      Backend Server                         ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  Environment: {config_name:<43} ║
    ║  Host:        {host:<43} ║
    ║  Port:        {port:<43} ║
    ║  Debug:       {debug:<43} ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  API URL:     http://{host}:{port}/api                      ║
    ║  Health:      http://{host}:{port}/api/health               ║
    ║  Docs:        http://{host}:{port}/api/docs                 ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Start the server with SocketIO support
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            log_output=True
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
