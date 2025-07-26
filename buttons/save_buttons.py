import customtkinter as ctk
import numpy as np
import os
from datetime import datetime
from tkinter import messagebox
from core.document_generator import DocumentGenerator
import logging

logger = logging.getLogger(__name__)


class SaveButtons:
    """Document save functionality"""
    
    def __init__(self, main_app):
        self.app = main_app
    
    def create_save_button(self, parent):
        """Create save document button"""
        self.app.save_btn = ctk.CTkButton(
            parent,
            text="💾 SAVE DOCUMENT",
            command=self.save_complete_document,
            width=160,
            height=40,
            fg_color="#228B22",
            hover_color="#1E7B1E",
            font=("Arial", 12, "bold"),
            state="disabled"
        )
        return self.app.save_btn
    
    def save_complete_document(self):
        """Save complete document with robust error handling"""
        try:
            # Validate required data
            if not self.app.current_id_info:
                messagebox.showwarning("Cảnh báo", "Chưa có thông tin QR Code!")
                return
                
            if self.app.front_image is None:
                messagebox.showwarning("Cảnh báo", "Chưa chụp ảnh mặt trước!")
                return
                
            if self.app.back_image is None:
                messagebox.showwarning("Cảnh báo", "Chưa chụp ảnh mặt sau!")
                return
            
            # Validate images are valid numpy arrays with content
            try:
                if not isinstance(self.app.front_image, np.ndarray):
                    messagebox.showerror("Lỗi", "Ảnh mặt trước không hợp lệ!")
                    return
                if self.app.front_image.size == 0 or self.app.front_image.shape[0] == 0 or self.app.front_image.shape[1] == 0:
                    messagebox.showerror("Lỗi", "Ảnh mặt trước rỗng!")
                    return
                    
                if not isinstance(self.app.back_image, np.ndarray):
                    messagebox.showerror("Lỗi", "Ảnh mặt sau không hợp lệ!")
                    return
                if self.app.back_image.size == 0 or self.app.back_image.shape[0] == 0 or self.app.back_image.shape[1] == 0:
                    messagebox.showerror("Lỗi", "Ảnh mặt sau rỗng!")
                    return
                    
                logger.info(f"Images validated - Front: {self.app.front_image.shape}, Back: {self.app.back_image.shape}")
                
            except Exception as e:
                logger.error(f"Image validation error: {e}")
                messagebox.showerror("Lỗi", f"Lỗi kiểm tra ảnh: {str(e)}")
                return
            
            qr_content = list(self.app.detected_qrs)[-1] if self.app.detected_qrs else "N/A"
            
            # Check if we need to overwrite
            overwrite = hasattr(self.app, '_existing_file_to_overwrite') and self.app._existing_file_to_overwrite is not None
            
            # Show progress
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.app._update_content_log(f"💾 [{timestamp}] Đang lưu tài liệu...", append=True)
            
            # Create document (always creates new files)
            filename, old_files_to_delete = DocumentGenerator.create_complete_document(
                self.app.current_id_info,
                self.app.front_image,
                self.app.back_image,
                qr_content,
                overwrite=overwrite,
                existing_file_info=self.app._existing_file_to_overwrite if overwrite else None
            )
            
            # If overwrite, delete old files after successful save
            if overwrite and old_files_to_delete:
                deleted_count = 0
                for old_file in old_files_to_delete:
                    try:
                        os.remove(old_file)
                        deleted_count += 1
                        logger.info(f"Deleted old file: {old_file}")
                    except Exception as e:
                        logger.warning(f"Failed to delete {old_file}: {e}")
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                if deleted_count > 0:
                    self.app._update_content_log(f"🗑️ [{timestamp}] Đã xóa {deleted_count} file cũ", append=True)
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if overwrite:
                success_text = f"🔄 [{timestamp}] Đã LƯU ĐÈ tài liệu thành công!\n📁 File mới: {filename}\n📂 Word Documents: {self.app.config.OUTPUT_DIR}\n📷 Images & JSON: {self.app.config.SCAN_DIR}\n\n✨ File mới được tạo với tên unique!\n🗑️ File cũ đã được xóa an toàn\n🔍 Có thể tìm kiếm trong database"
            else:
                success_text = f"💾 [{timestamp}] Lưu tài liệu MỚI thành công!\n📁 File: {filename}\n📂 Word Documents: {self.app.config.OUTPUT_DIR}\n📷 Images & JSON: {self.app.config.SCAN_DIR}\n\n✨ Tài liệu bao gồm đầy đủ thông tin QR code và ảnh CCCD!\n🔍 Đã thêm vào database để tìm kiếm"
            
            self.app._update_content_log(success_text, append=True)
            
            action = "LƯU ĐÈ" if overwrite else "TẠO MỚI"
            messagebox.showinfo("Thành công", f"Đã {action} tài liệu thành công!\nFile: {filename}\n\nCó thể tìm kiếm trong database bằng nút 'SEARCH DB'")
            
            # Clean up
            if hasattr(self.app, '_existing_file_to_overwrite'):
                delattr(self.app, '_existing_file_to_overwrite')
            
            # Reset all after successful save
            from buttons.utility_buttons import UtilityButtons
            utility_buttons = UtilityButtons(self.app)
            utility_buttons.reset_all()
            
        except Exception as e:
            logger.error(f"Failed to save document: {e}")
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.app._update_content_log(f"❌ [{timestamp}] Lỗi khi lưu: {str(e)}", append=True)
            messagebox.showerror("Lỗi", f"Lỗi khi lưu tài liệu: {str(e)}")
    
    def check_complete_status(self):
        """Check if all data is ready for document generation"""
        if (self.app.front_image is not None and 
            isinstance(self.app.front_image, np.ndarray) and 
            self.app.front_image.size > 0 and
            self.app.back_image is not None and 
            isinstance(self.app.back_image, np.ndarray) and
            self.app.back_image.size > 0 and
            self.app.current_id_info is not None):
            self.app.save_btn.configure(state="normal")
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"✅ [{timestamp}] Hoàn tất! Sẵn sàng lưu tài liệu hoàn chỉnh!"
            self.app._update_content_log(message, append=True)
        else:
            self.app.save_btn.configure(state="disabled")