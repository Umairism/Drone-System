"""
Video Streaming Module
Handles camera operations and video streaming functionality.
"""

import asyncio
import logging
import cv2
import numpy as np
from typing import Optional, Tuple
import base64
import threading
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class VideoStreamer:
    """Video streaming and camera management."""
    
    def __init__(self, camera_id: int = 0, resolution: Tuple[int, int] = (1920, 1080), fps: int = 30):
        """Initialize video streamer.
        
        Args:
            camera_id: Camera device ID
            resolution: Video resolution (width, height)
            fps: Frames per second
        """
        self.camera_id = camera_id
        self.resolution = resolution
        self.fps = fps
        self.capture = None
        self.latest_frame = None
        self.new_frame_available = False
        self.recording = False
        self.video_writer = None
        self.recording_filename = None
        self.frame_lock = threading.Lock()
        self.running = False
        
        # Streaming settings
        self.stream_quality = os.getenv('STREAM_QUALITY', 'high')
        self.encoding_params = self._get_encoding_params()
        
        logger.info(f"Initialized VideoStreamer - Camera: {camera_id}, Resolution: {resolution}, FPS: {fps}")
    
    def _get_encoding_params(self) -> list:
        """Get encoding parameters based on quality setting."""
        quality_settings = {
            'low': [cv2.IMWRITE_JPEG_QUALITY, 50],
            'medium': [cv2.IMWRITE_JPEG_QUALITY, 70],
            'high': [cv2.IMWRITE_JPEG_QUALITY, 95]
        }
        return quality_settings.get(self.stream_quality, quality_settings['high'])
    
    async def start(self):
        """Start the video streaming."""
        try:
            # Initialize camera
            self.capture = cv2.VideoCapture(self.camera_id)
            
            if not self.capture.isOpened():
                # Try alternative camera initialization for Raspberry Pi
                self.capture = cv2.VideoCapture(f'/dev/video{self.camera_id}')
                
            if not self.capture.isOpened():
                logger.error(f"Failed to open camera {self.camera_id}")
                # Use mock mode for testing
                await self._start_mock_mode()
                return
            
            # Configure camera settings
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.capture.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Get actual resolution (may differ from requested)
            actual_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.capture.get(cv2.CAP_PROP_FPS)
            
            logger.info(f"Camera initialized - Resolution: {actual_width}x{actual_height}, FPS: {actual_fps}")
            
            self.running = True
            
            # Start capture loop in thread
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
        except Exception as e:
            logger.error(f"Failed to start video streaming: {e}")
            await self._start_mock_mode()
    
    async def _start_mock_mode(self):
        """Start mock mode with generated frames."""
        logger.info("Starting video streaming in mock mode")
        self.running = True
        self.capture_thread = threading.Thread(target=self._mock_capture_loop, daemon=True)
        self.capture_thread.start()
    
    def _capture_loop(self):
        """Main camera capture loop (runs in separate thread)."""
        while self.running:
            try:
                ret, frame = self.capture.read()
                if not ret:
                    logger.warning("Failed to read frame from camera")
                    continue
                
                # Process frame
                processed_frame = self._process_frame(frame)
                
                # Update latest frame
                with self.frame_lock:
                    self.latest_frame = processed_frame
                    self.new_frame_available = True
                
                # Handle recording
                if self.recording and self.video_writer:
                    self.video_writer.write(processed_frame)
                
                # Control frame rate
                cv2.waitKey(int(1000 / self.fps))
                
            except Exception as e:
                logger.error(f"Error in capture loop: {e}")
                break
    
    def _mock_capture_loop(self):
        """Mock capture loop for testing without camera."""
        frame_count = 0
        
        while self.running:
            try:
                # Generate mock frame
                frame = self._generate_mock_frame(frame_count)
                
                # Update latest frame
                with self.frame_lock:
                    self.latest_frame = frame
                    self.new_frame_available = True
                
                frame_count += 1
                
                # Control frame rate
                import time
                time.sleep(1.0 / self.fps)
                
            except Exception as e:
                logger.error(f"Error in mock capture loop: {e}")
                break
    
    def _generate_mock_frame(self, frame_count: int) -> np.ndarray:
        """Generate a mock frame for testing.
        
        Args:
            frame_count: Current frame number
            
        Returns:
            np.ndarray: Generated frame
        """
        # Create a simple animated frame
        frame = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
        
        # Add background gradient
        for i in range(self.resolution[1]):
            frame[i, :] = [i * 255 // self.resolution[1], 100, 150]
        
        # Add moving circle
        center_x = int(self.resolution[0] // 2 + 200 * np.sin(frame_count * 0.1))
        center_y = int(self.resolution[1] // 2 + 100 * np.cos(frame_count * 0.1))
        cv2.circle(frame, (center_x, center_y), 50, (0, 255, 0), -1)
        
        # Add frame counter text
        cv2.putText(frame, f"Frame: {frame_count}", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
    
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process captured frame.
        
        Args:
            frame: Raw camera frame
            
        Returns:
            np.ndarray: Processed frame
        """
        # Add timestamp overlay
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add system info overlay
        info_text = f"Resolution: {frame.shape[1]}x{frame.shape[0]}"
        cv2.putText(frame, info_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    async def get_latest_frame(self) -> Optional[np.ndarray]:
        """Get the latest captured frame.
        
        Returns:
            Optional[np.ndarray]: Latest frame or None
        """
        with self.frame_lock:
            if self.latest_frame is not None:
                self.new_frame_available = False
                return self.latest_frame.copy()
            return None
    
    def has_new_frame(self) -> bool:
        """Check if a new frame is available.
        
        Returns:
            bool: True if new frame is available
        """
        with self.frame_lock:
            return self.new_frame_available
    
    async def get_frame_as_jpeg(self) -> Optional[bytes]:
        """Get latest frame encoded as JPEG.
        
        Returns:
            Optional[bytes]: JPEG encoded frame
        """
        frame = await self.get_latest_frame()
        if frame is not None:
            _, buffer = cv2.imencode('.jpg', frame, self.encoding_params)
            return buffer.tobytes()
        return None
    
    async def get_frame_as_base64(self) -> Optional[str]:
        """Get latest frame as base64 encoded string.
        
        Returns:
            Optional[str]: Base64 encoded frame
        """
        jpeg_data = await self.get_frame_as_jpeg()
        if jpeg_data:
            return base64.b64encode(jpeg_data).decode('utf-8')
        return None
    
    async def start_recording(self, filename: str = None) -> bool:
        """Start video recording.
        
        Args:
            filename: Output filename (auto-generated if None)
            
        Returns:
            bool: Success status
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"recording_{timestamp}.mp4"
            
            recording_path = os.path.join(os.getenv('RECORDING_PATH', 'data/recordings'), filename)
            os.makedirs(os.path.dirname(recording_path), exist_ok=True)
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                recording_path, fourcc, self.fps, self.resolution
            )
            
            if not self.video_writer.isOpened():
                logger.error("Failed to initialize video writer")
                return False
            
            self.recording = True
            self.recording_filename = recording_path
            logger.info(f"Started recording to {recording_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False
    
    async def stop_recording(self) -> Optional[str]:
        """Stop video recording.
        
        Returns:
            Optional[str]: Recording filename if successful
        """
        try:
            if not self.recording:
                logger.warning("Recording not in progress")
                return None
            
            self.recording = False
            
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            
            filename = self.recording_filename
            self.recording_filename = None
            
            logger.info(f"Stopped recording to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return None
    
    def is_recording(self) -> bool:
        """Check if currently recording.
        
        Returns:
            bool: Recording status
        """
        return self.recording
    
    async def set_camera_settings(self, settings: dict) -> bool:
        """Update camera settings.
        
        Args:
            settings: Dictionary of settings to update
            
        Returns:
            bool: Success status
        """
        try:
            if not self.capture:
                return False
            
            for setting, value in settings.items():
                if setting == 'brightness':
                    self.capture.set(cv2.CAP_PROP_BRIGHTNESS, value)
                elif setting == 'contrast':
                    self.capture.set(cv2.CAP_PROP_CONTRAST, value)
                elif setting == 'saturation':
                    self.capture.set(cv2.CAP_PROP_SATURATION, value)
                elif setting == 'exposure':
                    self.capture.set(cv2.CAP_PROP_EXPOSURE, value)
                elif setting == 'zoom':
                    self.capture.set(cv2.CAP_PROP_ZOOM, value)
            
            logger.info(f"Updated camera settings: {settings}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update camera settings: {e}")
            return False
    
    async def get_camera_info(self) -> dict:
        """Get camera information and capabilities.
        
        Returns:
            dict: Camera information
        """
        if not self.capture:
            return {}
        
        try:
            return {
                'width': int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': self.capture.get(cv2.CAP_PROP_FPS),
                'brightness': self.capture.get(cv2.CAP_PROP_BRIGHTNESS),
                'contrast': self.capture.get(cv2.CAP_PROP_CONTRAST),
                'saturation': self.capture.get(cv2.CAP_PROP_SATURATION),
                'exposure': self.capture.get(cv2.CAP_PROP_EXPOSURE),
                'recording': self.recording,
                'recording_file': self.recording_filename
            }
        except Exception as e:
            logger.error(f"Failed to get camera info: {e}")
            return {}
    
    async def is_healthy(self) -> bool:
        """Check if video streaming is healthy.
        
        Returns:
            bool: Health status
        """
        return (self.running and 
                (self.capture is not None or self.latest_frame is not None))
    
    async def stop(self):
        """Stop video streaming and cleanup resources."""
        try:
            self.running = False
            
            # Stop recording if active
            if self.recording:
                await self.stop_recording()
            
            # Wait for capture thread to finish
            if hasattr(self, 'capture_thread') and self.capture_thread.is_alive():
                self.capture_thread.join(timeout=2)
            
            # Release camera
            if self.capture:
                self.capture.release()
                self.capture = None
            
            logger.info("Video streaming stopped")
            
        except Exception as e:
            logger.error(f"Error stopping video streaming: {e}")
