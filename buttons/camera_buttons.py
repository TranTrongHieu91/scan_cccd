import customtkinter as ctk
import threading
from datetime import datetime
from tkinter import messagebox
import logging

logger = logging.getLogger(__name__)


class CameraButtons:
    """Camera control buttons functionality with camera selection"""
    
    def __init__(self, main_app):
        self.app = main_app
        
    def create_camera_controls(self, parent):
        """Create adaptive camera controls with camera selection"""
        cam_controls = ctk.CTkFrame(parent, fg_color="#333333")
        cam_controls.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # Configure responsive grid for controls
        cam_controls.grid_columnconfigure(0, weight=1)
        cam_controls.grid_columnconfigure(1, weight=1) 
        cam_controls.grid_columnconfigure(2, weight=1)
        cam_controls.grid_rowconfigure(0, weight=0)  # Camera selection row
        cam_controls.grid_rowconfigure(1, weight=1)  # Control buttons row
        
        # Camera selection section
        self._create_camera_selection(cam_controls)
        
        # Control buttons section
        self._create_control_buttons(cam_controls)
    
    def _create_camera_selection(self, parent):
        """Create camera selection dropdown"""
        selection_frame = ctk.CTkFrame(parent, fg_color="#444444")
        selection_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Configure grid
        selection_frame.grid_columnconfigure(1, weight=1)
        
        # Label
        camera_label = ctk.CTkLabel(
            selection_frame,
            text="📹 Camera:",
            font=("Arial", 11, "bold"),
            text_color="#00FFFF"
        )
        camera_label.grid(row=0, column=0, padx=(10, 5), pady=8, sticky="w")
        
        # Dropdown for camera selection
        self.app.camera_dropdown = ctk.CTkOptionMenu(
            selection_frame,
            values=self.app.camera_manager.get_camera_list_for_dropdown(),
            command=self._on_camera_selection_changed,
            font=("Arial", 10),
            dropdown_font=("Arial", 10)
        )
        self.app.camera_dropdown.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            selection_frame,
            text="🔄",
            command=self._refresh_camera_list,
            width=30,
            height=28,
            fg_color="#666666",
            hover_color="#555555",
            font=("Arial", 12)
        )
        refresh_btn.grid(row=0, column=2, padx=(5, 10), pady=8)
        
        # Set initial selection
        current_cameras = self.app.camera_manager.get_camera_list_for_dropdown()
        if current_cameras:
            self.app.camera_dropdown.set(current_cameras[0])
    
    def _create_control_buttons(self, parent):
        """Create camera control buttons"""
        # Camera control buttons with adaptive sizing
        self.app.camera_btn = ctk.CTkButton(
            parent,
            text="🎥 START CAMERA",
            command=self.toggle_camera,
            height=40,
            fg_color="#00AA00",
            hover_color="#008800",
            font=("Arial", 11, "bold")
        )
        self.app.camera_btn.grid(row=1, column=0, padx=5, pady=10, sticky="ew")
        
        self.app.zoom_btn = ctk.CTkButton(
            parent,
            text="🔍 QR FOCUS",
            command=self.toggle_qr_focus,
            height=40,
            fg_color="#FF6600",
            hover_color="#CC4400",
            font=("Arial", 10, "bold"),
            state="disabled"
        )
        self.app.zoom_btn.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        
        self.app.rescan_btn = ctk.CTkButton(
            parent,
            text="🔄 RESCAN QR",
            command=self.unlock_qr_scan,
            height=40,
            fg_color="#9966FF",
            hover_color="#7744DD",
            font=("Arial", 10, "bold"),
            state="disabled"
        )
        self.app.rescan_btn.grid(row=1, column=2, padx=5, pady=10, sticky="ew")
    
    def _on_camera_selection_changed(self, selection: str):
        """Handle camera selection change"""
        try:
            # Extract camera index from selection (format: "0: Camera Name")
            camera_index = int(selection.split(":")[0])
            
            # Update camera manager
            if self.app.camera_manager.set_camera_index(camera_index):
                timestamp = datetime.now().strftime("%H:%M:%S")
                camera_info = self.app.camera_manager.get_current_camera_info()
                message = f"📹 [{timestamp}] Đã chọn camera: {camera_info}"
                self.app._update_content_log(message, append=True)
                
                # If camera is currently running, restart with new camera
                if self.app.scanning:
                    self.app._update_content_log(f"🔄 [{timestamp}] Đang khởi động lại với camera mới...", append=True)
                    self.stop_scanning()
                    # Delay restart to ensure proper cleanup
                    self.app.root.after(500, self.start_scanning)
            else:
                messagebox.showwarning("Cảnh báo", f"Không thể chọn camera {camera_index}")
                
        except Exception as e:
            logger.error(f"Error changing camera selection: {e}")
            messagebox.showerror("Lỗi", f"Lỗi khi chọn camera: {str(e)}")
    
    def _refresh_camera_list(self):
        """Refresh the camera list"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.app._update_content_log(f"🔄 [{timestamp}] Đang quét lại danh sách camera...", append=True)
            
            # Stop camera if running
            was_scanning = self.app.scanning
            if was_scanning:
                self.stop_scanning()
            
            # Refresh camera list
            self.app.camera_manager.refresh_camera_list()
            
            # Update dropdown
            new_camera_list = self.app.camera_manager.get_camera_list_for_dropdown()
            self.app.camera_dropdown.configure(values=new_camera_list)
            
            if new_camera_list:
                self.app.camera_dropdown.set(new_camera_list[0])
                self.app._update_content_log(f"✅ [{timestamp}] Tìm thấy {len(new_camera_list)} camera", append=True)
            else:
                self.app._update_content_log(f"❌ [{timestamp}] Không tìm thấy camera nào", append=True)
            
            # Restart camera if it was running
            if was_scanning:
                self.app.root.after(1000, self.start_scanning)
                
        except Exception as e:
            logger.error(f"Error refreshing camera list: {e}")
            messagebox.showerror("Lỗi", f"Lỗi khi quét camera: {str(e)}")
    
    def toggle_camera(self):
        """Toggle camera on/off"""
        if not self.app.scanning:
            self.start_scanning()
        else:
            self.stop_scanning()
    
    def start_scanning(self):
        """Start camera and QR scanning with retry mechanism"""
        try:
            self.app.camera_retry_count = 0
            
            # Show current camera info
            camera_info = self.app.camera_manager.get_current_camera_info()
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.app._update_content_log(f"📹 [{timestamp}] Đang khởi động camera: {camera_info}", append=True)
            
            if not self.app.camera_manager.start():
                self.handle_camera_error()
                return
            
            self.app.scanning = True
            self.update_scan_ui_state(True)
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"✅ [{timestamp}] Camera đã được mở thành công!\n🔍 Đang tìm kiếm mã QR code...\n📱 Đưa CCCD có mã QR vào khung hình\n🗄️ Database search sẵn sàng!\n📹 Camera: {camera_info}"
            self.app._update_content_log(message, append=True)
            
            self.app.stop_video_event.clear()
            self.app.video_thread = threading.Thread(target=self.app._video_loop, daemon=True)
            self.app.video_thread.start()
            
        except Exception as e:
            logger.error(f"Failed to start camera: {e}")
            self.handle_camera_error()
    
    def handle_camera_error(self):
        """Handle camera startup errors"""
        self.app.camera_retry_count += 1
        
        camera_info = self.app.camera_manager.get_current_camera_info()
        error_message = f"""❌ Không thể mở camera {camera_info}! (Lần thử {self.app.camera_retry_count}/{self.app.max_camera_retries})

🔍 Đang kiểm tra nguyên nhân..."""
        self.app._update_content_log(error_message)
        
        if self.app.camera_retry_count < self.app.max_camera_retries:
            error_detail = f"""
🔧 ĐỀ XUẤT KHẮC PHỤC:
1. Thử chọn camera khác từ dropdown
2. Nhấn nút 🔄 để quét lại danh sách camera
3. Đóng các ứng dụng khác (Skype, Zoom, Teams)
4. Nhấn 'KHẮC PHỤC CAMERA' để xem hướng dẫn chi tiết

⏳ Sẽ tự động thử lại sau 3 giây..."""
            self.app._update_content_log(error_detail, append=True)
            self.app.root.after(3000, self.auto_retry_camera)
        else:
            final_error = f"""
❌ ĐÃ THỬ {self.app.max_camera_retries} LẦN NHƯNG VẪN KHÔNG THỂ MỞ CAMERA!

📋 VUI LÒNG THỬ:
1. Chọn camera khác từ dropdown
2. Nhấn 🔄 để quét lại camera
3. Nhấn 'KHẮC PHỤC CAMERA' và làm theo hướng dẫn
4. Restart máy tính
5. Chạy ứng dụng với quyền Administrator"""
            self.app._update_content_log(final_error, append=True)
            
            response = messagebox.askyesno(
                "Lỗi Camera",
                f"Không thể mở camera {camera_info} sau nhiều lần thử.\n\n"
                "Bạn có muốn:\n"
                "• Thử camera khác\n"
                "• Xem hướng dẫn khắc phục\n\n"
                "Chọn Yes để xem hướng dẫn, No để hủy."
            )
            if response:
                from gui.dialogs.camera_fix_dialog import CameraFixDialog
                CameraFixDialog(self.app.root)
    
    def auto_retry_camera(self):
        """Auto retry camera connection"""
        if not self.app.scanning and self.app.camera_retry_count < self.app.max_camera_retries:
            self.start_scanning()
    
    def stop_scanning(self):
        """Stop camera and scanning"""
        self.app.scanning = False
        self.app.stop_video_event.set()
        
        if self.app.video_thread and self.app.video_thread.is_alive():
            self.app.video_thread.join(timeout=1.0)
        
        self.app.camera_manager.stop()
        self.update_scan_ui_state(False)
        
        self.app.cam_panel.configure(
            image="", 
            text="🎥 CAMERA READY\n\nChọn camera từ dropdown\nClick 'START CAMERA' to begin\n\n• Adaptive workspace size\n• Auto-scaling video display\n• Responsive to window changes\n• Advanced search database"
        )
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"🛑 [{timestamp}] Camera đã được dừng"
        self.app._update_content_log(message, append=True)
    
    def update_scan_ui_state(self, scanning: bool):
        """Update UI state with modern status indicators"""
        if scanning:
            self.app.camera_btn.configure(
                text="🛑 STOP CAMERA", 
                fg_color="#FF3333",
                hover_color="#CC2222"
            )
            self.app.camera_status.configure(
                text="🟢 ONLINE",
                text_color="#00FF88"
            )
            self.app.status_label.configure(
                text="🟢 SCANNING",
                text_color="#00FF88"
            )
            
            # Disable camera selection while running
            self.app.camera_dropdown.configure(state="disabled")
            
            # Enable other camera controls
            if hasattr(self.app, 'zoom_btn'):
                self.app.zoom_btn.configure(state="normal")
            if self.app.rescan_btn:
                self.app.rescan_btn.configure(state="normal" if self.app.qr_locked else "disabled")
        else:
            self.app.camera_btn.configure(
                text="🎥 START CAMERA", 
                fg_color="#00AA00",
                hover_color="#008800"
            )
            self.app.camera_status.configure(
                text="⭕ OFFLINE",
                text_color="#FF6666"
            )
            self.app.status_label.configure(
                text="🔴 READY",
                text_color="#FF6666"
            )
            
            # Enable camera selection when stopped
            self.app.camera_dropdown.configure(state="normal")
            
            if hasattr(self.app, 'zoom_btn'):
                self.app.zoom_btn.configure(state="disabled")
                self.app.qr_focus_mode = False
                self.app.zoom_btn.configure(
                    text="🔍 QR FOCUS",
                    fg_color="#FF6600",
                    hover_color="#CC4400"
                )
            if self.app.rescan_btn:
                self.app.rescan_btn.configure(state="disabled")
    
    def toggle_qr_focus(self):
        """Toggle QR focus mode for better small QR detection"""
        self.app.qr_focus_mode = not self.app.qr_focus_mode
        
        if self.app.qr_focus_mode:
            self.app.zoom_btn.configure(
                text="🔍 NORMAL VIEW",
                fg_color="#00FF00",
                hover_color="#00CC00"
            )
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"🔍 [{timestamp}] Chế độ QR Focus: BẬT\n📱 Đưa QR code vào khung vàng ở giữa màn hình\n🎯 Giữ camera ổn định để nhận diện tốt hơn"
            self.app._update_content_log(message, append=True)
        else:
            self.app.zoom_btn.configure(
                text="🔍 QR FOCUS",
                fg_color="#FF6600",
                hover_color="#CC4400"
            )
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"👁️ [{timestamp}] Chế độ Normal View: BẬT\n📺 Hiển thị toàn bộ khung hình camera"
            self.app._update_content_log(message, append=True)
    
    def unlock_qr_scan(self):
        """Unlock QR scanning to allow new QR detection"""
        self.app.qr_locked = False
        self.app.detected_qrs.clear()  # Clear previous QR data
        
        # Reset data display
        for field in self.app.data_labels:
            self.app.data_labels[field].configure(text="Chưa có dữ liệu")
        
        # Reset images
        self.app.front_image = None
        self.app.back_image = None
        
        # Reset capture buttons - Cho phép chụp lại
        if self.app.scanning:  # Chỉ enable khi camera đang bật
            self.app.front_btn.configure(state="normal", text="📸 FRONT")
            self.app.back_btn.configure(state="normal", text="📸 BACK")
        
        # Update button states
        self.app.rescan_btn.configure(state="disabled")
        self.app.current_id_info = None
        self.app._check_complete_status()  # This will disable save button if needed
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"🔄 [{timestamp}] Đã mở khóa quét QR - Sẵn sàng quét QR mới!\n📱 Đưa CCCD có mã QR vào khung hình để quét lại\n📸 Có thể chụp ảnh mặt trước và sau lại"
        self.app._update_content_log(message, append=True)