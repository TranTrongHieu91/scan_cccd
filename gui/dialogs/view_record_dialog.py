import customtkinter as ctk
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ViewRecordDialog(ctk.CTkToplevel):
    """Dialog for viewing detailed record information"""
    
    def __init__(self, parent, record: Dict[str, Any]):
        super().__init__(parent)
        self.title(f"👁️ Chi tiết - {record['name']}")
        self.geometry("800x600")
        self.resizable(True, True)
        
        self.transient(parent)
        self.grab_set()
        
        self.record = record
        
        self._create_ui()
        
        # Center dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_ui(self):
        """Create detailed view interface"""
        main_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="#333333")
        header_frame.pack(fill="x", padx=10, pady=10)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"👤 {self.record['name']}",
            font=("Arial", 20, "bold"),
            text_color="#00FFFF"
        )