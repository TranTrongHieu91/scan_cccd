import customtkinter as ctk
from PIL import Image
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class CameraPanel:
    """Camera display panel with camera selection and full frame preview"""
    
    def __init__(self, main_app):
        self.app = main_app
    
    def create_camera_panel(self, parent):
        """Create the adaptive camera panel with camera selection"""
        self.app.camera_panel = ctk.CTkFrame(
            parent,
            fg_color="#1a1a1a",
            corner_radius=12,
            border_width=2,
            border_color="#00FFFF"
        )
        self.app.camera_panel.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        
        # Responsive grid configuration
        self.app.camera_panel.grid_rowconfigure(0, weight=0, minsize=50)  # Header
        self.app.camera_panel.grid_rowconfigure(1, weight=1)             # Camera display
        self.app.camera_panel.grid_rowconfigure(2, weight=0, minsize=80) # Controls (increased for dropdown)
        self.app.camera_panel.grid_columnconfigure(0, weight=1)
        
        # Panel header
        header = ctk.CTkFrame(self.app.camera_panel, fg_color="#333333", corner_radius=8)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Header content
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.app.camera_title = ctk.CTkLabel(
            header_content,
            text="📹 CAMERA WORKSPACE - FULL FRAME",
            font=("Arial", 18, "bold"),
            text_color="#00FFFF"
        )
        self.app.camera_title.pack(side="left")
        
        # Camera status indicator with current camera info
        self.app.camera_status = ctk.CTkLabel(
            header_content,
            text="⭕ OFFLINE",
            font=("Arial", 12, "bold"),
            text_color="#FF6666"
        )
        self.app.camera_status.pack(side="right")
        
        # Main camera display
        self.app.cam_panel = ctk.CTkLabel(
            self.app.camera_panel,
            fg_color="#000000",
            corner_radius=8,
            text="🎥 CAMERA READY - FULL FRAME MODE\n\nChọn camera từ dropdown bên dưới\nClick 'START CAMERA' to begin\n\n• Full camera frame display\n• No cropping or zoom\n• Complete camera view\n• Multi-camera support",
            font=("Arial", 14),
            text_color="#FFFFFF"
        )
        self.app.cam_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=0)
        
        # Camera controls (now includes camera selection)
        self.app.camera_buttons.create_camera_controls(self.app.camera_panel)
    
    def update_camera_status_with_info(self, status: str, camera_info: str = ""):
        """Update camera status with current camera information"""
        if camera_info:
            status_text = f"{status} | {camera_info}"
        else:
            status_text = status
        self.app.camera_status.configure(text=status_text)
    
    def update_video_display(self, display_frame: np.ndarray):
        """Update video display with full frame - no cropping"""
        try:
            # Get current camera panel size
            panel_width = self.app.cam_panel.winfo_width()
            panel_height = self.app.cam_panel.winfo_height()
            
            # Only resize if we have valid dimensions
            if panel_width > 100 and panel_height > 100:
                cv2image = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                
                # Get original frame dimensions
                original_width, original_height = img.size
                aspect_ratio = original_width / original_height
                
                # Calculate available space with minimal padding for full frame view
                padding = 10  # Minimal padding to see frame borders
                available_width = panel_width - (padding * 2)
                available_height = panel_height - (padding * 2)
                
                # Calculate new size while maintaining aspect ratio
                # Fit the entire frame within the panel
                if aspect_ratio > available_width / available_height:
                    # Frame is wider - fit to width
                    new_width = available_width
                    new_height = int(available_width / aspect_ratio)
                else:
                    # Frame is taller - fit to height
                    new_height = available_height
                    new_width = int(available_height * aspect_ratio)
                
                # Ensure minimum readable size
                min_width = max(320, int(panel_width * 0.6))
                min_height = max(240, int(panel_height * 0.6))
                
                # Apply minimum size if calculated size is too small
                if new_width < min_width or new_height < min_height:
                    if aspect_ratio > min_width / min_height:
                        new_width = min_width
                        new_height = int(min_width / aspect_ratio)
                    else:
                        new_height = min_height
                        new_width = int(min_height * aspect_ratio)
                
                # Ensure we don't exceed panel bounds
                new_width = min(new_width, available_width)
                new_height = min(new_height, available_height)
                
                # Resize image using high-quality resampling
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Create CTk image
                ctk_image = ctk.CTkImage(
                    light_image=img_resized,
                    dark_image=img_resized,
                    size=(new_width, new_height)
                )
                
                self.app.root.after(0, self._update_camera_label, ctk_image)
                
            else:
                # Fallback with responsive default sizes
                window_width = self.app.root.winfo_width()
                
                # Adaptive default sizes based on window size
                if window_width < 1600:
                    default_size = (480, 360)  # 4:3 ratio
                elif window_width < 2000:
                    default_size = (640, 480)  # 4:3 ratio
                else:
                    default_size = (800, 600)  # 4:3 ratio
                
                cv2image = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                
                # Maintain aspect ratio for fallback
                original_width, original_height = img.size
                aspect_ratio = original_width / original_height
                target_width, target_height = default_size
                
                if aspect_ratio > target_width / target_height:
                    # Wider frame
                    new_width = target_width
                    new_height = int(target_width / aspect_ratio)
                else:
                    # Taller frame
                    new_height = target_height
                    new_width = int(target_height * aspect_ratio)
                
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                ctk_image = ctk.CTkImage(
                    light_image=img_resized,
                    dark_image=img_resized,
                    size=(new_width, new_height)
                )
                
                self.app.root.after(0, self._update_camera_label, ctk_image)
                
        except Exception as e:
            logger.error(f"Error updating video display: {e}")
    
    def _update_camera_label(self, ctk_image):
        """Thread-safe camera label update"""
        if self.app.cam_panel and self.app.scanning:
            self.app.cam_panel.configure(image=ctk_image, text="")
    
    def get_display_info(self):
        """Get current display information for debugging"""
        try:
            panel_width = self.app.cam_panel.winfo_width()
            panel_height = self.app.cam_panel.winfo_height()
            return f"Panel: {panel_width}x{panel_height}"
        except:
            return "Panel: Unknown size"