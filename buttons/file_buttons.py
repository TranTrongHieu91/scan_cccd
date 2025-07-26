import customtkinter as ctk
import os
from datetime import datetime
from tkinter import messagebox
from core.file_manager import FileManager
import logging

logger = logging.getLogger(__name__)


class FileButtons:
    """File management buttons functionality"""
    
    def __init__(self, main_app):
        self.app = main_app
    
    def create_docs_button(self, parent):
        """Create documents folder button"""
        docs_btn = ctk.CTkButton(
            parent,
            text="📁 DOCUMENTS",
            command=self.open_docs_folder,
            width=130,
            height=40,
            fg_color="#FF8C00",
            hover_color="#FF6600",
            font=("Arial", 11, "bold")
        )
        return docs_btn
    
    def create_images_button(self, parent):
        """Create images folder button"""
        images_btn = ctk.CTkButton(
            parent,
            text="📂 IMAGES",
            command=self.open_images_folder,
            width=120,
            height=40,
            fg_color="#FFB800",
            hover_color="#FF9900",
            font=("Arial", 11, "bold")
        )
        return images_btn
    
    def open_docs_folder(self):
        """Open Word documents folder"""
        try:
            folder_path = os.path.abspath(self.app.config.OUTPUT_DIR)
            if os.name == 'nt':
                os.startfile(folder_path)
            elif os.name == 'posix':
                os.system(f'open "{folder_path}"')
            
            stats = FileManager.get_folder_stats(folder_path)
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"📁 [{timestamp}] Đã mở thư mục Word Documents\n📂 Đường dẫn: {folder_path}\n📊 Thống kê: {stats['total_files']} files, {stats['total_size_mb']} MB"
            self.app._update_content_log(message, append=True)
        except Exception as e:
            logger.error(f"Failed to open folder: {e}")
            messagebox.showerror("Lỗi", f"Không thể mở thư mục: {str(e)}")
    
    def open_images_folder(self):
        """Open images and JSON folder"""
        try:
            folder_path = os.path.abspath(self.app.config.SCAN_DIR)
            
            if os.name == 'nt':
                os.startfile(folder_path)
            elif os.name == 'posix':
                os.system(f'open "{folder_path}"')
            
            stats = FileManager.get_folder_stats(folder_path)
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"📂 [{timestamp}] Đã mở thư mục Images & JSON\n📁 Đường dẫn: {folder_path}\n📊 Thống kê: {stats['total_files']} files, {stats['total_size_mb']} MB"
            self.app._update_content_log(message, append=True)
        except Exception as e:
            logger.error(f"Failed to open images folder: {e}")
            messagebox.showerror("Lỗi", f"Không thể mở thư mục: {str(e)}")