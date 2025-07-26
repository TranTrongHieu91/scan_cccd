import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox
import logging

logger = logging.getLogger(__name__)


class SearchButtons:
    """Database search functionality"""
    
    def __init__(self, main_app):
        self.app = main_app
    
    def create_search_button(self, parent):
        """Create search database button"""
        search_btn = ctk.CTkButton(
            parent,
            text="🔍 SEARCH DB",
            command=self.show_search_dialog,
            width=130,
            height=40,
            fg_color="#9966FF",
            hover_color="#7744DD",
            font=("Arial", 11, "bold")
        )
        return search_btn
    
    def show_search_dialog(self):
        """Show enhanced search dialog for CCCD records - NOW FUNCTIONAL!"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"🔍 [{timestamp}] Mở Database Search...\n📊 Tìm kiếm trong tất cả records đã lưu"
            self.app._update_content_log(message, append=True)
            
            # Import and create search dialog
            from gui.dialogs.search_dialog import SearchDialog
            SearchDialog(self.app.root)
            
        except Exception as e:
            logger.error(f"Error opening search dialog: {e}")
            messagebox.showerror("Lỗi", f"Không thể mở Search Dialog: {str(e)}")