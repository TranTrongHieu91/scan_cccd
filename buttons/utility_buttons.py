import customtkinter as ctk
import os
import glob
from datetime import datetime
from tkinter import messagebox
from database.search_manager import SearchManager
import logging

logger = logging.getLogger(__name__)


class UtilityButtons:
    """Reset, Cleanup, and Help buttons functionality"""
    
    def __init__(self, main_app):
        self.app = main_app
    
    def create_reset_button(self, parent):
        """Create reset all button"""
        reset_btn = ctk.CTkButton(
            parent,
            text="🔄 RESET ALL",
            command=self.reset_all,
            width=130,
            height=40,
            fg_color="#FF4444",
            hover_color="#CC3333",
            font=("Arial", 12, "bold")
        )
        return reset_btn
    
    def create_cleanup_button(self, parent):
        """Create cleanup button"""
        cleanup_btn = ctk.CTkButton(
            parent,
            text="🧹 CLEANUP",
            command=self.show_cleanup_dialog,
            width=120,
            height=40,
            fg_color="#FF6666",
            hover_color="#CC4444",
            font=("Arial", 11, "bold")
        )
        return cleanup_btn
    
    def create_help_button(self, parent):
        """Create camera help button"""
        help_btn = ctk.CTkButton(
            parent,
            text="🔧 CAMERA HELP",
            command=self.show_camera_fix_dialog,
            width=130,
            height=30,
            fg_color="#666666",
            hover_color="#555555",
            font=("Arial", 10)
        )
        return help_btn
    
    def reset_all(self):
        """Reset all data and UI"""
        # Reset QR detection
        self.app.qr_locked = False
        self.app.detected_qrs.clear()
        self.app.current_id_info = None
        
        # Reset images
        self.app.front_image = None
        self.app.back_image = None
        
        # Reset data display
        for field in self.app.data_labels:
            self.app.data_labels[field].configure(text="Chưa có dữ liệu")
        
        # Reset capture buttons
        if self.app.scanning:  # Chỉ enable khi camera đang bật
            self.app.front_btn.configure(state="normal", text="📸 FRONT")
            self.app.back_btn.configure(state="normal", text="📸 BACK")
        else:
            self.app.front_btn.configure(state="disabled", text="📸 FRONT")
            self.app.back_btn.configure(state="disabled", text="📸 BACK")
        
        # Reset other buttons
        self.app.save_btn.configure(state="disabled")
        self.app.rescan_btn.configure(state="disabled")
        
        # Reset QR focus mode
        self.app.qr_focus_mode = False
        if hasattr(self.app, 'zoom_btn'):
            self.app.zoom_btn.configure(
                text="🔍 QR FOCUS",
                fg_color="#FF6600",
                hover_color="#CC4400"
            )
        
        # Clean up overwrite info
        if hasattr(self.app, '_existing_file_to_overwrite'):
            delattr(self.app, '_existing_file_to_overwrite')
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"🔄 [{timestamp}] Đã reset toàn bộ hệ thống!\n📱 Sẵn sàng cho lần quét mới\n📸 Có thể chụp ảnh mặt trước và sau\n🔍 Database search vẫn hoạt động"
        self.app._update_content_log(message, append=True)
    
    def show_cleanup_dialog(self):
        """Show cleanup management dialog"""
        try:
            # Get current statistics
            stats = SearchManager.get_statistics()
            
            response = messagebox.askyesnocancel(
                "🧹 Cleanup Manager", 
                f"THỐNG KÊ HIỆN TẠI:\n"
                f"📊 Tổng records: {stats['total_records']}\n"
                f"💾 Tổng dung lượng: {stats['total_size_mb']} MB\n"
                f"📄 Có Word document: {stats['records_with_word']}\n"
                f"📸 Có ảnh: {stats['records_with_images']}\n\n"
                f"BẠN MUỐN:\n"
                f"YES = Mở Search để xem và xóa từng file\n"
                f"NO = Xóa tất cả files (NGUY HIỂM!)\n"
                f"CANCEL = Hủy bỏ"
            )
            
            if response is True:
                # Open search dialog
                from buttons.search_buttons import SearchButtons
                search_buttons = SearchButtons(self.app)
                search_buttons.show_search_dialog()
            elif response is False:
                # Dangerous - delete all
                confirm = messagebox.askyesno(
                    "⚠️ XÁC NHẬN XÓA TẤT CẢ",
                    "CẢNH BÁO: Bạn sắp xóa TẤT CẢ dữ liệu CCCD!\n\n"
                    "Điều này sẽ xóa:\n"
                    f"• {stats['total_records']} records\n"
                    f"• {stats['total_size_mb']} MB dữ liệu\n"
                    f"• Tất cả Word documents\n"
                    f"• Tất cả ảnh và JSON\n\n"
                    "KHÔNG THỂ HOÀN TÁC!\n\n"
                    "Bạn có CHẮC CHẮN muốn xóa tất cả?"
                )
                
                if confirm:
                    try:
                        # Delete all files in both directories
                        deleted_count = 0
                        
                        # Delete from SCAN_DIR
                        for file_path in glob.glob(os.path.join(self.app.config.SCAN_DIR, "*")):
                            try:
                                os.remove(file_path)
                                deleted_count += 1
                            except:
                                pass
                        
                        # Delete from OUTPUT_DIR
                        for file_path in glob.glob(os.path.join(self.app.config.OUTPUT_DIR, "*")):
                            try:
                                os.remove(file_path)
                                deleted_count += 1
                            except:
                                pass
                        
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        message = f"🧹 [{timestamp}] CLEANUP HOÀN TẤT!\n🗑️ Đã xóa {deleted_count} files\n💾 Giải phóng {stats['total_size_mb']} MB"
                        self.app._update_content_log(message, append=True)
                        
                        messagebox.showinfo("Hoàn thành", f"Đã xóa {deleted_count} files!\nGiải phóng {stats['total_size_mb']} MB dung lượng.")
                        
                    except Exception as e:
                        messagebox.showerror("Lỗi", f"Lỗi khi cleanup: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error in cleanup dialog: {e}")
            messagebox.showerror("Lỗi", f"Lỗi cleanup manager: {str(e)}")
    
    def show_camera_fix_dialog(self):
        """Show camera troubleshooting dialog"""
        try:
            from gui.dialogs.camera_fix_dialog import CameraFixDialog
            CameraFixDialog(self.app.root)
        except Exception as e:
            logger.error(f"Error opening camera fix dialog: {e}")
            messagebox.showerror("Lỗi", f"Không thể mở Camera Help: {str(e)}")