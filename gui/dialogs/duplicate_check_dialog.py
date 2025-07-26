import customtkinter as ctk
import os
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class DuplicateCheckDialog(ctk.CTkToplevel):
    """Dialog for handling duplicate person detection"""
    
    def __init__(self, parent, person_info: Dict[str, str], existing_files: List[Dict[str, str]]):
        super().__init__(parent)
        self.title("⚠️ Phát hiện trùng người")
        self.geometry("700x500")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.person_info = person_info
        self.existing_files = existing_files
        self.result = None  # Will store user choice: 'overwrite', 'new', or 'cancel'
        
        self._create_ui()
        
        # Center the dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_ui(self):
        """Create duplicate check UI"""
        # Title
        title_label = ctk.CTkLabel(
            self, 
            text="⚠️ PHÁT HIỆN THÔNG TIN TRÙNG", 
            font=("Arial", 24, "bold"),
            text_color="#FF8800"
        )
        title_label.pack(pady=20)
        
        # Current person info
        info_frame = ctk.CTkFrame(self, fg_color="#333333")
        info_frame.pack(pady=10, padx=20, fill="x")
        
        current_label = ctk.CTkLabel(
            info_frame,
            text="📋 THÔNG TIN ĐANG QUÉT:",
            font=("Arial", 16, "bold"),
            text_color="#00FFFF"
        )
        current_label.pack(pady=10)
        
        person_name = self.person_info.get("Họ và tên", "N/A")
        person_cccd = self.person_info.get("Số CCCD", self.person_info.get("Số CMND", "N/A"))
        
        info_text = f"👤 Họ tên: {person_name}\n🆔 Số CCCD/CMND: {person_cccd}"
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Arial", 14),
            text_color="#FFFFFF",
            justify="left"
        )
        info_label.pack(pady=10)
        
        # Existing files info
        existing_frame = ctk.CTkFrame(self, fg_color="#444444")
        existing_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        existing_label = ctk.CTkLabel(
            existing_frame,
            text="📁 ĐÃ TÌM THẤY FILE CŨ:",
            font=("Arial", 16, "bold"),
            text_color="#FF6666"
        )
        existing_label.pack(pady=10)
        
        # Display existing files info
        for i, file_info in enumerate(self.existing_files):
            file_frame = ctk.CTkFrame(existing_frame, fg_color="#555555")
            file_frame.pack(fill="x", pady=5, padx=10)
            
            file_text = f"📅 Ngày tạo: {file_info['created']}\n"
            if 'word_path' in file_info:
                file_text += f"📄 Word: {os.path.basename(file_info['word_path']) if file_info['word_path'] else 'Không có'}"
            
            file_label = ctk.CTkLabel(
                file_frame,
                text=file_text,
                font=("Arial", 12),
                text_color="#CCCCCC",
                justify="left"
            )
            file_label.pack(pady=5, padx=10, anchor="w")
        
        # Question
        question_label = ctk.CTkLabel(
            self,
            text="❓ BẠN MUỐN LÀM GÌ?",
            font=("Arial", 18, "bold"),
            text_color="#FFFF00"
        )
        question_label.pack(pady=20)
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)
        
        # Overwrite button
        overwrite_btn = ctk.CTkButton(
            button_frame,
            text="🔄 LƯU ĐÈ FILE CŨ",
            command=self._choose_overwrite,
            width=200,
            height=40,
            fg_color="#FF6600",
            hover_color="#CC4400"
        )
        overwrite_btn.pack(side="left", padx=10)
        
        # New file button
        new_btn = ctk.CTkButton(
            button_frame,
            text="➕ TẠO FILE MỚI",
            command=self._choose_new,
            width=200,
            height=40,
            fg_color="#00AA00",
            hover_color="#008800"
        )
        new_btn.pack(side="left", padx=10)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ HỦY BỎ",
            command=self._choose_cancel,
            width=200,
            height=40,
            fg_color="#FF4444",
            hover_color="#CC3333"
        )
        cancel_btn.pack(side="left", padx=10)
        
        # Note
        note_label = ctk.CTkLabel(
            self,
            text="💡 Lưu ý: File mới luôn được tạo với tên unique. Lưu đè = Tạo mới + Xóa cũ",
            font=("Arial", 11),
            text_color="#FFAA00"
        )
        note_label.pack(pady=10)
    
    def _choose_overwrite(self):
        """User chose to overwrite"""
        self.result = 'overwrite'
        self.destroy()
    
    def _choose_new(self):
        """User chose to create new file"""
        self.result = 'new'
        self.destroy()
    
    def _choose_cancel(self):
        """User chose to cancel"""
        self.result = 'cancel'
        self.destroy()