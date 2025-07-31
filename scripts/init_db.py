#!/usr/bin/env python3
"""
Database Initialization Script
Creates and initializes the database schema for the surveillance drone system.
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATABASE_PATH = PROJECT_ROOT / "data" / "drone_data.db"

def create_tables(conn):
    """Create database tables."""
    
    # Flight logs table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS flight_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_id TEXT UNIQUE NOT NULL,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            duration INTEGER,
            max_altitude REAL,
            max_speed REAL,
            distance_traveled REAL,
            battery_start REAL,
            battery_end REAL,
            waypoints_visited INTEGER,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Telemetry data table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_id TEXT,
            timestamp TIMESTAMP,
            latitude REAL,
            longitude REAL,
            altitude REAL,
            roll REAL,
            pitch REAL,
            yaw REAL,
            velocity_x REAL,
            velocity_y REAL,
            velocity_z REAL,
            battery_voltage REAL,
            battery_current REAL,
            battery_remaining REAL,
            gps_satellites INTEGER,
            gps_hdop REAL,
            FOREIGN KEY (flight_id) REFERENCES flight_logs (flight_id)
        )
    ''')
    
    # Detection logs table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_id TEXT,
            timestamp TIMESTAMP,
            class_name TEXT,
            confidence REAL,
            bbox_x1 INTEGER,
            bbox_y1 INTEGER,
            bbox_x2 INTEGER,
            bbox_y2 INTEGER,
            latitude REAL,
            longitude REAL,
            altitude REAL,
            image_path TEXT,
            FOREIGN KEY (flight_id) REFERENCES flight_logs (flight_id)
        )
    ''')
    
    # Missions table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS missions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            waypoints TEXT,  -- JSON string
            settings TEXT,   -- JSON string
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # System events table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS system_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT,
            severity INTEGER,
            message TEXT,
            details TEXT,  -- JSON string
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User sessions table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            user_agent TEXT,
            remote_addr TEXT,
            connected_at TIMESTAMP,
            disconnected_at TIMESTAMP
        )
    ''')
    
    print("Database tables created successfully")

def create_indexes(conn):
    """Create database indexes for performance."""
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_telemetry_flight_id ON telemetry(flight_id)",
        "CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_detections_flight_id ON detections(flight_id)",
        "CREATE INDEX IF NOT EXISTS idx_detections_timestamp ON detections(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_detections_class ON detections(class_name)",
        "CREATE INDEX IF NOT EXISTS idx_system_events_timestamp ON system_events(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_system_events_type ON system_events(event_type)"
    ]
    
    for index_sql in indexes:
        conn.execute(index_sql)
    
    print("Database indexes created successfully")

def insert_sample_data(conn):
    """Insert sample data for testing."""
    
    # Sample mission
    sample_mission = {
        'mission_id': 'mission_sample_001',
        'name': 'Test Perimeter Patrol',
        'description': 'Sample mission for testing the system',
        'waypoints': '''[
            {"lat": 33.6844, "lng": 73.0479, "alt": 20, "action": "photo"},
            {"lat": 33.6850, "lng": 73.0485, "alt": 20, "action": "video_start"},
            {"lat": 33.6840, "lng": 73.0490, "alt": 25, "action": "detect_objects"}
        ]''',
        'settings': '''{
            "speed": 5,
            "return_home": true,
            "failsafe_altitude": 30
        }''',
        'status': 'planned'
    }
    
    conn.execute('''
        INSERT OR IGNORE INTO missions 
        (mission_id, name, description, waypoints, settings, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        sample_mission['mission_id'],
        sample_mission['name'], 
        sample_mission['description'],
        sample_mission['waypoints'],
        sample_mission['settings'],
        sample_mission['status']
    ))
    
    # Sample system event
    conn.execute('''
        INSERT INTO system_events (event_type, severity, message, details)
        VALUES (?, ?, ?, ?)
    ''', (
        'system_startup',
        1,
        'Drone system initialized successfully',
        '{"version": "1.0.0", "components": ["flight_controller", "camera", "gps"]}'
    ))
    
    print("Sample data inserted successfully")

def main():
    """Initialize the database."""
    try:
        # Create data directory if it doesn't exist
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(DATABASE_PATH)
        
        print(f"Initializing database at: {DATABASE_PATH}")
        
        # Create tables
        create_tables(conn)
        
        # Create indexes
        create_indexes(conn)
        
        # Insert sample data
        insert_sample_data(conn)
        
        # Commit changes
        conn.commit()
        
        print("Database initialization completed successfully!")
        
        # Show database info
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Created tables: {[table[0] for table in tables]}")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
