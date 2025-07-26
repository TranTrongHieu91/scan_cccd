import cv2
import numpy as np
from typing import Optional, List, Dict
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class CameraManager:
    """Enhanced camera management with camera selection support"""
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_active = False
        self.camera_index = 0
        self.available_cameras: Dict[int, str] = {}
        self._scan_available_cameras()
        
    def _scan_available_cameras(self):
        """Scan for available cameras and store their info"""
        self.available_cameras = {}
        
        # Test camera indices 0-9
        for i in range(10):
            try:
                test_cap = cv2.VideoCapture(i)
                if test_cap.isOpened():
                    # Try to read a frame to confirm it's working
                    ret, frame = test_cap.read()
                    if ret and frame is not None:
                        # Get camera name/info if possible
                        backend_name = self._get_backend_name(test_cap)
                        camera_name = f"Camera {i}"
                        
                        # Try to get more info about the camera
                        width = test_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                        height = test_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                        if width > 0 and height > 0:
                            camera_name += f" ({int(width)}x{int(height)})"
                        
                        self.available_cameras[i] = f"{camera_name} - {backend_name}"
                        logger.info(f"Found camera {i}: {self.available_cameras[i]}")
                test_cap.release()
            except Exception as e:
                logger.debug(f"Error testing camera {i}: {e}")
                continue
        
        if not self.available_cameras:
            # Add default camera option even if not detected
            self.available_cameras[0] = "Default Camera (0)"
            logger.warning("No cameras detected, adding default option")
        
        logger.info(f"Total available cameras: {len(self.available_cameras)}")
    
    def _get_backend_name(self, cap) -> str:
        """Get backend name for camera"""
        try:
            backend = cap.getBackendName()
            return backend if backend else "Unknown"
        except:
            return "Unknown"
    
    def get_available_cameras(self) -> Dict[int, str]:
        """Get dictionary of available cameras {index: name}"""
        return self.available_cameras.copy()
    
    def get_camera_list_for_dropdown(self) -> List[str]:
        """Get list of camera names for dropdown widget"""
        camera_list = []
        for index, name in self.available_cameras.items():
            camera_list.append(f"{index}: {name}")
        return camera_list if camera_list else ["0: Default Camera"]
    
    def set_camera_index(self, index: int) -> bool:
        """Set camera index to use"""
        if index in self.available_cameras or index == 0:
            self.camera_index = index
            logger.info(f"Camera index set to: {index}")
            return True
        else:
            logger.warning(f"Invalid camera index: {index}")
            return False
    
    def get_current_camera_info(self) -> str:
        """Get current camera information"""
        return self.available_cameras.get(self.camera_index, f"Camera {self.camera_index}")
    
    def refresh_camera_list(self):
        """Refresh the list of available cameras"""
        logger.info("Refreshing camera list...")
        self._scan_available_cameras()
        
    @contextmanager
    def camera_context(self):
        """Context manager for safe camera operations"""
        try:
            yield self.start()
        finally:
            self.stop()
    
    def test_camera_backends(self) -> Optional[int]:
        """Test different camera backends to find working one"""
        backends = [
            cv2.CAP_DSHOW,     # DirectShow (Windows)
            cv2.CAP_MSMF,      # Microsoft Media Foundation (Windows 10+)
            cv2.CAP_VFW,       # Video for Windows (legacy)
            cv2.CAP_ANY        # Auto-detect
        ]
        
        for backend in backends:
            logger.info(f"Testing camera backend: {backend}")
            try:
                test_cap = cv2.VideoCapture(self.camera_index, backend)
                if test_cap.isOpened():
                    # Test if we can actually read a frame
                    ret, frame = test_cap.read()
                    test_cap.release()
                    if ret and frame is not None:
                        logger.info(f"Camera backend {backend} works!")
                        return backend
            except Exception as e:
                logger.warning(f"Backend {backend} failed: {e}")
                
        return None
    
    def find_available_camera(self) -> Optional[int]:
        """Find first available camera index"""
        # First try the selected camera index
        if self.camera_index in self.available_cameras:
            return self.camera_index
            
        # If selected camera not available, try others
        for index in self.available_cameras.keys():
            try:
                test_cap = cv2.VideoCapture(index)
                if test_cap.isOpened():
                    ret, _ = test_cap.read()
                    test_cap.release()
                    if ret:
                        logger.info(f"Found working camera at index {index}")
                        return index
            except:
                pass
        return None
    
    def start(self) -> bool:
        """Start camera with multiple fallback methods"""
        try:
            logger.info(f"Starting camera with index {self.camera_index}")
            
            # Method 1: Try with backend detection
            backend = self.test_camera_backends()
            if backend is not None:
                self.cap = cv2.VideoCapture(self.camera_index, backend)
            else:
                # Method 2: Try default
                self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                # Method 3: Try finding available camera
                available_index = self.find_available_camera()
                if available_index is not None:
                    self.camera_index = available_index
                    self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera {self.camera_index}")
                return False
                
            # Configure camera settings
            self._configure_camera()
            
            # Verify camera is working
            ret, frame = self.cap.read()
            if not ret or frame is None:
                logger.error("Camera opened but cannot read frames")
                self.cap.release()
                return False
                
            self.is_active = True
            logger.info(f"Camera {self.camera_index} started successfully: {self.get_current_camera_info()}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start camera: {e}")
            return False
    
    def _configure_camera(self):
        """Configure camera settings for optimal performance"""
        if self.cap:
            # Try to set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            # Set FPS
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Reduce buffer size for lower latency
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Set auto exposure if available
            try:
                self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
            except:
                pass
            
            logger.info("Camera configured with optimal settings")
    
    def stop(self):
        """Stop camera and cleanup resources"""
        self.is_active = False
        if self.cap:
            self.cap.release()
            self.cap = None
            logger.info("Camera stopped")
    
    def read_frame(self) -> Optional[np.ndarray]:
        """Read frame with error handling"""
        if not self.is_active or not self.cap:
            return None
            
        try:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                return frame
            else:
                # Try to reconnect if frame read fails
                logger.warning("Failed to read frame, attempting reconnect...")
                self.stop()
                if self.start():
                    ret, frame = self.cap.read()
                    return frame if ret else None
        except Exception as e:
            logger.error(f"Error reading frame: {e}")
            
        return None