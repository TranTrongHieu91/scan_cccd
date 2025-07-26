import customtkinter as ctk
import numpy as np
from datetime import datetime
from tkinter import messagebox
import logging

logger = logging.getLogger(__name__)


class CaptureButtons:
    """Image capture buttons functionality"""
    
    def __init__(self, main_app):
        self.app = main_app
    
    def create_capture_controls(self, parent):
        """Create adaptive capture controls"""
        capture_frame = ctk.CTkFrame(parent, fg_color="#333333")
        capture_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # Configure responsive grid
        capture_frame.grid_rowconfigure(0, weight=0)
        capture_frame.grid_rowconfigure(1, weight=1)
        capture_frame.grid_columnconfigure(0, weight=1)
        capture_frame.grid_columnconfigure(1, weight=1)
        
        capture_title = ctk.CTkLabel(
            capture_frame,
            text="📸 CAPTURE CONTROLS",
            font=("Arial", 12, "bold"),
            text_color="#FFAA00"
        )
        capture_title.grid(row=0, column=0, columnspan=2, pady=5)
        
        self.app.front_btn = ctk.CTkButton(
            capture_frame,
            text="📸 FRONT",
            command=self.capture_front,
            height=35,
            fg_color="#0088FF",
            hover_color="#0066CC",
            font=("Arial", 10, "bold"),
            state="disabled"
        )
        self.app.front_btn.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.app.back_btn = ctk.CTkButton(
            capture_frame,
            text="📸 BACK",
            command=self.capture_back,
            height=35,
            fg_color="#0088FF",
            hover_color="#0066CC",
            font=("Arial", 10, "bold"),
            state="disabled"
        )
        self.app.back_btn.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    
    def capture_front(self):
        """Capture front image of CCCD"""
        if self.app.current_frame is not None and isinstance(self.app.current_frame, np.ndarray) and self.app.current_frame.size > 0:
            self.app.front_image = self.app.current_frame.copy()
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"📸 [{timestamp}] Đã chụp mặt trước CCCD!"
            self.app._update_content_log(message, append=True)
            
            self.app.front_btn.configure(state="disabled", text="✅ ĐÃ CHỤP TRƯỚC")
            self.app._check_complete_status()
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng mở camera trước khi chụp!")
    
    def capture_back(self):
        """Capture back image of CCCD"""
        if self.app.current_frame is not None and isinstance(self.app.current_frame, np.ndarray) and self.app.current_frame.size > 0:
            self.app.back_image = self.app.current_frame.copy()
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"📸 [{timestamp}] Đã chụp mặt sau CCCD!"
            self.app._update_content_log(message, append=True)
            
            self.app.back_btn.configure(state="disabled", text="✅ ĐÃ CHỤP SAU")
            self.app._check_complete_status()
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng mở camera trước khi chụp!")
    
    def update_capture_ui_state(self, scanning: bool):
        """Update capture button states based on scanning status"""
        if scanning:
            # Enable capture buttons based on current state
            if self.app.front_image is None:
                self.app.front_btn.configure(state="normal", text="📸 FRONT")
            else:
                self.app.front_btn.configure(state="disabled", text="✅ FRONT OK")
            
            if self.app.back_image is None:
                self.app.back_btn.configure(state="normal", text="📸 BACK")
            else:
                self.app.back_btn.configure(state="disabled", text="✅ BACK OK")
        else:
            self.app.front_btn.configure(state="disabled", text="📸 FRONT")
            self.app.back_btn.configure(state="disabled", text="📸 BACK")
    
    def reset_capture_state(self):
        """Reset capture button states"""
        self.app.front_image = None
        self.app.back_image = None
        
        if self.app.scanning:
            self.app.front_btn.configure(state="normal", text="📸 FRONT")
            self.app.back_btn.configure(state="normal", text="📸 BACK")
        else:
            self.app.front_btn.configure(state="disabled", text="📸 FRONT")
            self.app.back_btn.configure(state="disabled", text="📸 BACK")