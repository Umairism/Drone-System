#!/usr/bin/env python3
"""
Simple Flask test script
"""

print("Starting Flask test...")

try:
    import sys
    import os
    print(f"Python path: {sys.path}")
    print(f"Current directory: {os.getcwd()}")
    
    from flask import Flask
    print("Flask imported successfully")
    
    from app import create_app
    print("App module imported successfully")
    
    app, socketio = create_app('development')
    print("App created successfully")
    
    print("Starting server on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
