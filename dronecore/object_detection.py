"""
Object Detection Module
Handles AI-powered object detection using YOLO models.
"""

import asyncio
import logging
import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
import os
from datetime import datetime

# Try to import YOLO from ultralytics
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("Ultralytics YOLO not available. Using mock implementation.")

logger = logging.getLogger(__name__)

class Detection:
    """Represents a detected object."""
    
    def __init__(self, class_name: str, confidence: float, bbox: Tuple[int, int, int, int]):
        """Initialize detection.
        
        Args:
            class_name: Name of detected class
            confidence: Detection confidence (0-1)
            bbox: Bounding box (x1, y1, x2, y2)
        """
        self.class_name = class_name
        self.confidence = confidence
        self.bbox = bbox
        self.timestamp = datetime.now()
        self.id = None  # For tracking
    
    def to_dict(self) -> Dict:
        """Convert detection to dictionary."""
        return {
            'class_name': self.class_name,
            'confidence': self.confidence,
            'bbox': self.bbox,
            'timestamp': self.timestamp.isoformat(),
            'id': self.id
        }
    
    def get_center_point(self) -> Tuple[int, int]:
        """Get center point of bounding box."""
        x1, y1, x2, y2 = self.bbox
        return (int((x1 + x2) / 2), int((y1 + y2) / 2))
    
    def get_area(self) -> int:
        """Get area of bounding box."""
        x1, y1, x2, y2 = self.bbox
        return (x2 - x1) * (y2 - y1)

class ObjectDetector:
    """Object detection using YOLO models."""
    
    def __init__(self, model_name: str = 'yolov8n', confidence_threshold: float = 0.5, device: str = 'cpu'):
        """Initialize object detector.
        
        Args:
            model_name: YOLO model name
            confidence_threshold: Minimum confidence for detections
            device: Device to run inference on ('cpu', 'cuda', etc.)
        """
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.device = device
        self.model = None
        self.class_names = []
        self.detection_classes = self._parse_detection_classes()
        self.mock_mode = not YOLO_AVAILABLE
        self.detection_history = []
        
        logger.info(f"Initialized ObjectDetector - Model: {model_name}, Threshold: {confidence_threshold}, Device: {device}")
    
    def _parse_detection_classes(self) -> List[str]:
        """Parse detection classes from environment variable."""
        classes_str = os.getenv('DETECTION_CLASSES', 'person,car,truck,motorcycle,bicycle')
        return [cls.strip() for cls in classes_str.split(',')]
    
    async def start(self):
        """Initialize the object detection model."""
        try:
            if self.mock_mode:
                await self._start_mock_mode()
            else:
                await self._load_yolo_model()
                
        except Exception as e:
            logger.error(f"Failed to start object detector: {e}")
            self.mock_mode = True
            await self._start_mock_mode()
    
    async def _load_yolo_model(self):
        """Load YOLO model."""
        try:
            # Download and load model
            self.model = YOLO(self.model_name)
            
            # Move model to specified device
            if self.device != 'cpu':
                self.model.to(self.device)
            
            # Get class names
            self.class_names = self.model.names
            
            logger.info(f"YOLO model {self.model_name} loaded successfully")
            logger.info(f"Available classes: {len(self.class_names)} classes")
            
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise
    
    async def _start_mock_mode(self):
        """Start mock mode for testing."""
        logger.info("Starting object detection in mock mode")
        # Common COCO class names for mock mode
        self.class_names = {
            0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane',
            5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light'
        }
    
    async def detect(self, frame: np.ndarray) -> List[Detection]:
        """Detect objects in frame.
        
        Args:
            frame: Input image frame
            
        Returns:
            List[Detection]: List of detected objects
        """
        try:
            if self.mock_mode:
                return await self._mock_detect(frame)
            else:
                return await self._yolo_detect(frame)
                
        except Exception as e:
            logger.error(f"Error in object detection: {e}")
            return []
    
    async def _yolo_detect(self, frame: np.ndarray) -> List[Detection]:
        """Perform YOLO detection on frame.
        
        Args:
            frame: Input image frame
            
        Returns:
            List[Detection]: List of detected objects
        """
        if not self.model:
            return []
        
        try:
            # Run inference
            results = self.model(frame, conf=self.confidence_threshold, verbose=False)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Extract detection data
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        
                        class_name = self.class_names.get(class_id, f'class_{class_id}')
                        
                        # Filter by detection classes if specified
                        if self.detection_classes and class_name not in self.detection_classes:
                            continue
                        
                        detection = Detection(
                            class_name=class_name,
                            confidence=confidence,
                            bbox=(int(x1), int(y1), int(x2), int(y2))
                        )
                        detections.append(detection)
            
            # Update detection history
            self.detection_history.append({
                'timestamp': datetime.now(),
                'count': len(detections),
                'detections': [d.to_dict() for d in detections]
            })
            
            # Keep history limited
            if len(self.detection_history) > 100:
                self.detection_history.pop(0)
            
            return detections
            
        except Exception as e:
            logger.error(f"Error in YOLO detection: {e}")
            return []
    
    async def _mock_detect(self, frame: np.ndarray) -> List[Detection]:
        """Mock detection for testing without model.
        
        Args:
            frame: Input image frame
            
        Returns:
            List[Detection]: Mock detected objects
        """
        import random
        
        detections = []
        height, width = frame.shape[:2]
        
        # Generate random detections
        num_detections = random.randint(0, 3)
        
        for _ in range(num_detections):
            # Random class from detection classes
            class_name = random.choice(self.detection_classes) if self.detection_classes else 'person'
            confidence = random.uniform(0.6, 0.95)
            
            # Random bounding box
            x1 = random.randint(0, width - 100)
            y1 = random.randint(0, height - 100)
            x2 = random.randint(x1 + 50, min(width, x1 + 200))
            y2 = random.randint(y1 + 50, min(height, y1 + 200))
            
            detection = Detection(
                class_name=class_name,
                confidence=confidence,
                bbox=(x1, y1, x2, y2)
            )
            detections.append(detection)
        
        return detections
    
    def draw_detections(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """Draw detection boxes and labels on frame.
        
        Args:
            frame: Input image frame
            detections: List of detections to draw
            
        Returns:
            np.ndarray: Frame with drawn detections
        """
        output_frame = frame.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection.bbox
            class_name = detection.class_name
            confidence = detection.confidence
            
            # Choose color based on class
            color = self._get_class_color(class_name)
            
            # Draw bounding box
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # Background for label
            cv2.rectangle(output_frame, 
                         (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), 
                         color, -1)
            
            # Label text
            cv2.putText(output_frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Draw detection count
        count_text = f"Detections: {len(detections)}"
        cv2.putText(output_frame, count_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return output_frame
    
    def _get_class_color(self, class_name: str) -> Tuple[int, int, int]:
        """Get color for class visualization.
        
        Args:
            class_name: Name of the class
            
        Returns:
            Tuple[int, int, int]: BGR color tuple
        """
        colors = {
            'person': (0, 255, 0),      # Green
            'car': (255, 0, 0),         # Blue
            'truck': (0, 0, 255),       # Red
            'motorcycle': (255, 255, 0), # Cyan
            'bicycle': (255, 0, 255),   # Magenta
            'bus': (0, 255, 255),       # Yellow
            'airplane': (128, 0, 128),  # Purple
            'boat': (255, 165, 0),      # Orange
        }
        return colors.get(class_name, (255, 255, 255))  # White as default
    
    async def get_detection_stats(self) -> Dict:
        """Get detection statistics.
        
        Returns:
            Dict: Detection statistics
        """
        if not self.detection_history:
            return {}
        
        recent_detections = self.detection_history[-10:]  # Last 10 frames
        
        total_detections = sum(d['count'] for d in recent_detections)
        avg_detections = total_detections / len(recent_detections) if recent_detections else 0
        
        # Class frequency
        class_counts = {}
        for detection_frame in recent_detections:
            for detection in detection_frame['detections']:
                class_name = detection['class_name']
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        return {
            'total_detections': total_detections,
            'average_per_frame': avg_detections,
            'class_distribution': class_counts,
            'detection_classes': self.detection_classes,
            'confidence_threshold': self.confidence_threshold,
            'model_name': self.model_name
        }
    
    async def update_config(self, config: Dict) -> bool:
        """Update detector configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            bool: Success status
        """
        try:
            if 'confidence_threshold' in config:
                self.confidence_threshold = float(config['confidence_threshold'])
                logger.info(f"Updated confidence threshold to {self.confidence_threshold}")
            
            if 'detection_classes' in config:
                self.detection_classes = config['detection_classes']
                logger.info(f"Updated detection classes to {self.detection_classes}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update detector config: {e}")
            return False
    
    async def is_healthy(self) -> bool:
        """Check if object detector is healthy.
        
        Returns:
            bool: Health status
        """
        return self.model is not None or self.mock_mode
    
    async def stop(self):
        """Stop object detector and cleanup resources."""
        try:
            if self.model:
                # YOLO model cleanup if needed
                self.model = None
            
            self.detection_history.clear()
            logger.info("Object detector stopped")
            
        except Exception as e:
            logger.error(f"Error stopping object detector: {e}")
