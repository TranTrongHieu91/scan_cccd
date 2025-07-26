import customtkinter as ctk
import threading
import numpy as np
from typing import Optional, Dict, Any
from datetime import datetime
import logging
import os
import sys

# Add current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import configuration
from config import Config

# Import core components  
from core.camera_manager import CameraManager
from core.qr_processor import QRProcessor
from core.id_parser import IDDataParser
from core.file_manager import FileManager

# Import UI components
from gui.panels.camera_panel import CameraPanel
from gui.panels.data_panel import DataPanel
from gui.panels.log_panel import LogPanel

# Import button handlers
from buttons.camera_buttons import CameraButtons
from buttons.capture_buttons import CaptureButtons
from buttons.save_buttons import SaveButtons
from buttons.search_buttons import SearchButtons
from buttons.file_buttons import FileButtons
from buttons.utility_buttons import UtilityButtons

logger = logging.getLogger(__name__)


class VietnameseIDScannerGUI:
    """Main application class with modular architecture and camera selection"""
    
    def __init__(self):
        self.config = Config()
        
        # Initialize file manager and create directories
        FileManager.ensure_directories()
        
        # Setup CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = self._setup_root()
        
        # Core components
        self.camera_manager = CameraManager(self.config.CAMERA_WIDTH, self.config.CAMERA_HEIGHT)
        self.qr_processor = QRProcessor()
        self.id_parser = IDDataParser()
        
        # Application state
        self.scanning = False
        self.detected_qrs = set()
        self.current_frame: Optional[np.ndarray] = None
        self.front_image: Optional[np.ndarray] = None
        self.back_image: Optional[np.ndarray] = None
        self.current_id_info: Optional[Dict[str, str]] = None
        self.qr_focus_mode = False
        self.qr_locked = False
        
        # UI components will be initialized by panels
        self.cam_panel: Optional[ctk.CTkLabel] = None
        self.content_text: Optional[ctk.CTkTextbox] = None
        self.data_labels: Dict[str, ctk.CTkLabel] = {}
        
        # Control buttons will be initialized by button handlers
        self.camera_btn: Optional[ctk.CTkButton] = None
        self.front_btn: Optional[ctk.CTkButton] = None
        self.back_btn: Optional[ctk.CTkButton] = None
        self.save_btn: Optional[ctk.CTkButton] = None
        self.zoom_btn: Optional[ctk.CTkButton] = None
        self.rescan_btn: Optional[ctk.CTkButton] = None
        
        # Camera dropdown - NEW
        self.camera_dropdown: Optional[ctk.CTkOptionMenu] = None
        
        # Status labels
        self.status_label: Optional[ctk.CTkLabel] = None
        self.camera_status: Optional[ctk.CTkLabel] = None
        
        # Initialize button handlers
        self.camera_buttons = CameraButtons(self)
        self.capture_buttons = CaptureButtons(self)
        self.save_buttons = SaveButtons(self)
        self.search_buttons = SearchButtons(self)
        self.file_buttons = FileButtons(self)
        self.utility_buttons = UtilityButtons(self)
        
        # Initialize UI panels
        self.camera_panel_handler = CameraPanel(self)
        self.data_panel_handler = DataPanel(self)
        self.log_panel_handler = LogPanel(self)
        
        # Setup GUI
        self._setup_gui()
        
        # Video thread
        self.video_thread: Optional[threading.Thread] = None
        self.stop_video_event = threading.Event()
        
        # Camera retry counter
        self.camera_retry_count = 0
        self.max_camera_retries = 3
    
    def _setup_root(self) -> ctk.CTk:
        """Setup main window with fullscreen and manual multi-monitor support"""
        root = ctk.CTk()
        root.title(self.config.APP_TITLE)
        
        # Set fullscreen mode
        root.attributes('-fullscreen', True)
        
        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Manual multi-monitor support
        offset_x = 0  # Mặc định hiển thị trên màn hình chính
        offset_y = 0
        
        # Set geometry
        root.geometry(f'{screen_width}x{screen_height}+{offset_x}+{offset_y}')
        root.resizable(True, True)
        
        # Enhanced grid layout
        root.grid_rowconfigure(0, weight=0, minsize=80)
        root.grid_rowconfigure(1, weight=1)
        root.grid_rowconfigure(2, weight=0, minsize=120)
        root.grid_columnconfigure(0, weight=1)
        
        # Bind events
        root.bind('<Configure>', self._on_window_resize)
        root.bind('<Escape>', self._toggle_fullscreen)
        
        return root
    
    def _toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode with ESC key"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
        
        if not current_state:  # Switching to fullscreen
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.root.geometry(f'{screen_width}x{screen_height}+0+0')
        else:  # Switching to windowed mode
            window_width = 1400
            window_height = 900
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width // 2) - (window_width // 2)
            y = (screen_height // 2) - (window_height // 2)
            self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    def _on_window_resize(self, event):
        """Handle window resize events for dynamic layout adjustments"""
        if event.widget == self.root:
            try:
                current_width = self.root.winfo_width()
                current_height = self.root.winfo_height()
                
                self._adjust_panel_proportions(current_width, current_height)
                
                if hasattr(self, 'cam_panel') and self.scanning:
                    self.root.after(100, self._update_camera_size)
                    
            except Exception as e:
                logger.error(f"Error handling window resize: {e}")
    
    def _adjust_panel_proportions(self, width: int, height: int):
        """Dynamically adjust panel proportions based on window size"""
        try:
            if width < 1600:
                camera_weight = 2
                data_weight = 1
                log_weight = 1
            elif width < 2000:
                camera_weight = 3
                data_weight = 2
                log_weight = 1
            else:
                camera_weight = 4
                data_weight = 2
                log_weight = 1
            
            if hasattr(self, 'workspace'):
                self.workspace.grid_columnconfigure(0, weight=camera_weight)
                self.workspace.grid_columnconfigure(1, weight=data_weight)
                self.workspace.grid_columnconfigure(2, weight=log_weight)
                
        except Exception as e:
            logger.error(f"Error adjusting panel proportions: {e}")
    
    def _update_camera_size(self):
        """Update camera display size based on current panel size"""
        try:
            if hasattr(self, 'cam_panel') and self.cam_panel.winfo_exists():
                self.cam_panel.update_idletasks()
        except Exception as e:
            logger.error(f"Error updating camera size: {e}")
    
    def _setup_gui(self):
        """Setup responsive GUI with CustomTkinter"""
        # Header section - row 0
        self._create_header()
        
        # Main content - row 1 (expandable)
        self._create_main_content()
        
        # Control buttons - row 2
        self._create_control_buttons()
        
        # Show welcome message with camera info
        self._show_welcome_message()
    
    def _create_header(self):
        """Create modern application header"""
        header_frame = ctk.CTkFrame(
            self.root, 
            fg_color="#1e1e1e", 
            height=80,
            corner_radius=0
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_propagate(False)
        
        # Header content container
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - App info
        left_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        left_frame.pack(side="left", fill="y")
        
        title_label = ctk.CTkLabel(
            left_frame, 
            text="🆔 AGRIBANK ID SCANNER + CAMERA SELECTION", 
            font=("Arial Black", 24, "bold"), 
            text_color="#00FFFF"
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            left_frame, 
            text=f"Professional QR Scanner v{self.config.VERSION} - Multi-Camera Support + Advanced Search", 
            font=("Arial", 12), 
            text_color="#AAAAAA"
        )
        subtitle_label.pack(anchor="w")
        
        # Right side - Quick status
        right_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        right_frame.pack(side="right", fill="y")
        
        self.status_label = ctk.CTkLabel(
            right_frame,
            text="🔴 READY",
            font=("Arial", 14, "bold"),
            text_color="#FF6666"
        )
        self.status_label.pack(anchor="e", pady=5)
    
    def _create_main_content(self):
        """Create adaptive 3-panel workspace layout"""
        self.workspace = ctk.CTkFrame(
            self.root, 
            fg_color="#2a2a2a", 
            corner_radius=15
        )
        self.workspace.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Dynamic 3-column layout
        self.workspace.grid_rowconfigure(0, weight=1)
        self.workspace.grid_columnconfigure(0, weight=3)  # Camera
        self.workspace.grid_columnconfigure(1, weight=2)  # Data  
        self.workspace.grid_columnconfigure(2, weight=1)  # Log
        
        # Create the three main panels using panel handlers
        self.camera_panel_handler.create_camera_panel(self.workspace)
        self.data_panel_handler.create_data_panel(self.workspace)
        self.log_panel_handler.create_log_panel(self.workspace)
        
        # Initial proportion adjustment
        self.root.after(100, lambda: self._adjust_panel_proportions(
            self.root.winfo_width(), self.root.winfo_height()
        ))
    
    def _create_control_buttons(self):
        """Create modern bottom control bar"""
        # Control bar container
        control_bar = ctk.CTkFrame(
            self.root,
            fg_color="#1e1e1e",
            height=120,
            corner_radius=0
        )
        control_bar.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        control_bar.grid_propagate(False)
        
        # Main controls section
        main_controls = ctk.CTkFrame(control_bar, fg_color="#2a2a2a", corner_radius=10)
        main_controls.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Controls grid
        controls_container = ctk.CTkFrame(main_controls, fg_color="transparent")
        controls_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Row 1: Main workflow buttons
        workflow_frame = ctk.CTkFrame(controls_container, fg_color="transparent")
        workflow_frame.pack(fill="x", pady=(0, 8))
        
        # Create buttons using button handlers
        self.save_btn = self.save_buttons.create_save_button(workflow_frame)
        self.save_btn.pack(side="left", padx=5)
        
        reset_btn = self.utility_buttons.create_reset_button(workflow_frame)
        reset_btn.pack(side="left", padx=5)
        
        # File management buttons
        file_frame = ctk.CTkFrame(workflow_frame, fg_color="transparent")
        file_frame.pack(side="right")
        
        docs_btn = self.file_buttons.create_docs_button(file_frame)
        docs_btn.pack(side="left", padx=3)
        
        images_btn = self.file_buttons.create_images_button(file_frame)
        images_btn.pack(side="left", padx=3)
        
        search_btn = self.search_buttons.create_search_button(file_frame)
        search_btn.pack(side="left", padx=3)
        
        cleanup_btn = self.utility_buttons.create_cleanup_button(file_frame)
        cleanup_btn.pack(side="left", padx=3)
        
        # Row 2: Status and help
        status_frame = ctk.CTkFrame(controls_container, fg_color="#333333", corner_radius=8)
        status_frame.pack(fill="x")
        
        status_content = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_content.pack(fill="x", padx=15, pady=8)
        
        # Status info with camera count
        camera_count = len(self.camera_manager.get_available_cameras())
        status_text = f"🎯 Multi-Camera v{self.config.VERSION} | 📹 {camera_count} Cameras | 🔍 Advanced Search | ⚡ Professional Design"
        status_label = ctk.CTkLabel(
            status_content,
            text=status_text,
            font=("Arial", 10),
            text_color="#AAAAAA"
        )
        status_label.pack(side="left")
        
        # Help button
        help_btn = self.utility_buttons.create_help_button(status_content)
        help_btn.pack(side="right")
    
    def _show_welcome_message(self):
        """Show welcome message with camera selection info"""
        camera_count = len(self.camera_manager.get_available_cameras())
        available_cameras = self.camera_manager.get_available_cameras()
        
        camera_list_text = ""
        for index, name in available_cameras.items():
            camera_list_text += f"  📹 Camera {index}: {name}\n"
        
        welcome_text = f"""🚀 Welcome to AGRIBANK ID Scanner Professional v{self.config.VERSION}!

🏗️ FULL FRAME CAMERA + MULTI-CAMERA SUPPORT + ADVANCED SEARCH:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📹 **FULL FRAME CAMERA FEATURES**:
• 🖼️ **Full Frame Display** - Hiển thị đầy đủ khung camera, không crop
• 📱 **Complete View** - Xem toàn bộ góc nhìn camera
• 🎯 **No Zoom/Crop** - Giữ nguyên tỷ lệ và size gốc
• 📏 **Aspect Ratio Preserved** - Tỷ lệ khung hình được bảo toàn
• 🔍 **Enhanced Guidance** - Guidance overlay tối ưu cho full frame

📹 **CAMERA SELECTION FEATURES**:
• 🔍 **Auto Camera Detection** - Tự động quét và phát hiện camera có sẵn
• 📱 **Multi-Camera Support** - Hỗ trợ nhiều camera cùng lúc
• 🔄 **Dynamic Switch** - Chuyển đổi camera trong khi chạy
• 🎯 **Smart Detection** - Phát hiện resolution và backend camera
• ⚡ **Real-time Refresh** - Làm mới danh sách camera real-time

📊 **CAMERA DETECTED**: {camera_count} camera(s) found
{camera_list_text}

📐 **DYNAMIC 3-PANEL LAYOUT**: 
┌─────────────────────┬───────────────┬──────────────┐
│   📹 CAMERA (50%)    │  📄 DATA (33%) │ 📊 LOG (17%) │
│                     │               │              │
│  • Full frame view  │ • QR Info     │ • Activity   │
│  • Camera dropdown  │ • Capture     │ • Status     │
│  • Complete preview │ • Controls    │ • Messages   │
└─────────────────────┴───────────────┴──────────────┘

🎮 **FULL FRAME CONTROLS**:
📹 **Camera Selection**: Dropdown để chọn camera
🔄 **Refresh Button**: Quét lại danh sách camera
🎥 **Start/Stop**: Bật/tắt camera đã chọn (full frame)
🖼️ **Full Preview**: Hiển thị toàn bộ khung camera
🔍 **QR Focus**: Focus mode cho QR code nhỏ
🔄 **Rescan QR**: Quét lại QR code mới

🖼️ **FULL FRAME ADVANTAGES**:
• 📐 **Complete Field of View** - Nhìn thấy toàn bộ góc quay camera
• 🎯 **Better QR Detection** - QR code ở bất kỳ vị trí nào đều được detect
• 📏 **True Aspect Ratio** - Không bị méo hình do crop
• 🔍 **Enhanced Visibility** - Thấy rõ context xung quanh QR code
• 📱 **Professional View** - Giao diện chuyên nghiệp như camera monitor

🔍 **ADVANCED SEARCH DATABASE v{self.config.VERSION}**:
• 🗄️ **Comprehensive Search** - Tìm kiếm theo tên, CCCD, CMND, ngày tháng
• 📊 **Database Statistics** - Thống kê tổng quan và phân tích dữ liệu
• 👁️ **Detailed View** - Xem chi tiết từng record với đầy đủ thông tin
• 🔄 **Smart Duplicate Detection** - Phát hiện và xử lý trùng lặp thông minh
• 📁 **File Management** - Quản lý file Word, ảnh, JSON tập trung
• 📋 **Export to CSV** - Xuất dữ liệu ra CSV cho báo cáo

🎯 **FULL FRAME CAMERA WORKFLOW v{self.config.VERSION}**:
1️⃣ Chọn camera từ dropdown → Camera được nhận diện tự động
2️⃣ Click 'START CAMERA' → Full frame preview bắt đầu
3️⃣ Xem toàn bộ khung camera → Không bị crop hay zoom
4️⃣ Position QR code → QR guidance overlay trên full frame
5️⃣ Auto-detection QR → Detect QR ở bất kỳ vị trí nào
6️⃣ System locks QR data → Duplicate check trong database
7️⃣ Capture FRONT/BACK → Full frame images được lưu
8️⃣ Save document → Auto-add vào searchable database

💡 **FULL FRAME TIPS**:
🖼️ Full frame hiển thị toàn bộ góc nhìn camera
📐 Aspect ratio được bảo toàn hoàn toàn
🎯 QR code có thể ở bất kỳ vị trí nào trong frame
🔍 Guidance overlay tối ưu cho full frame view
📱 Camera selection tự động detect resolution
⚡ Preview không bị méo hay crop
🎨 UI tự động scale theo camera resolution

🆕 **NEW FULL FRAME FEATURES v{self.config.VERSION}**:
🖼️ Complete camera frame display - no cropping
📐 True aspect ratio preservation
🎯 Enhanced QR detection area coverage
📏 Frame size indicator overlay
⚡ Optimized guidance for full frame
🎨 Professional camera monitor experience

🔧 **READY TO START**: 
1. Chọn camera từ dropdown (full frame mode)
2. Click 'START CAMERA' để xem toàn bộ khung hình
3. Hoặc 'SEARCH DB' để tìm kiếm!

🎨 **Experience the most advanced full-frame multi-camera CCCD scanner!**"""
        
        self._update_content_log(welcome_text)
    
    def _update_content_log(self, message: str, append: bool = False):
        """Update system log with auto-scroll"""
        try:
            if append:
                current_content = self.content_text.get("0.0", "end-1c")
                if current_content.strip():
                    new_content = current_content + "\n" + "─" * 30 + "\n" + message
                else:
                    new_content = message
            else:
                new_content = message
            
            self.content_text.delete("0.0", "end")
            self.content_text.insert("0.0", new_content)
            self.content_text.see("end")
            self.root.update_idletasks()
        except Exception as e:
            logger.error(f"Error updating content log: {e}")
    
    def _check_complete_status(self):
        """Check if all data is ready for document generation"""
        self.save_buttons.check_complete_status()
    
    def _video_loop(self):
        """Video processing loop with QR detection"""
        frame_error_count = 0
        max_frame_errors = 10
        
        while self.scanning and not self.stop_video_event.is_set():
            frame = self.camera_manager.read_frame()
            if frame is None:
                frame_error_count += 1
                if frame_error_count > max_frame_errors:
                    self.root.after(0, self._handle_video_stream_error)
                    break
                continue
            
            frame_error_count = 0
            self.current_frame = frame.copy()
            display_frame = frame.copy()
            
            # Apply guidance overlay
            display_frame = self.qr_processor.draw_guidance_overlay(display_frame)
            
            # QR detection - only if not locked
            if not self.qr_locked:
                barcodes = self.qr_processor.detect_qr_codes(frame)
                for barcode in barcodes:
                    display_frame = self.qr_processor.draw_detection(display_frame, barcode)
                    
                    try:
                        barcode_data = barcode.data.decode('utf-8')
                        if barcode_data not in self.detected_qrs:
                            self.detected_qrs.add(barcode_data)
                            self.root.after(0, self._process_qr_data, barcode_data)
                    except UnicodeDecodeError:
                        logger.warning("Failed to decode QR data")
            else:
                # Show QR locked indicator
                import cv2
                cv2.putText(display_frame, "QR LOCKED - Du lieu da duoc giu", (20, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display_frame, "Nhan 'QUET LAI QR' de quet moi", (20, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            self.camera_panel_handler.update_video_display(display_frame)
    
    def _handle_video_stream_error(self):
        """Handle video stream errors"""
        if self.scanning:
            error_msg = f"""⚠️ Mất kết nối với camera {self.camera_manager.get_current_camera_info()}!

Đang thử kết nối lại..."""
            self._update_content_log(error_msg, append=True)
            
            self.camera_buttons.stop_scanning()
            self.root.after(1000, self.camera_buttons.start_scanning)
    
    def _process_qr_data(self, qr_content: str):
        """Process detected QR data with duplicate check"""
        try:
            id_info = self.id_parser.parse(qr_content)
            self.current_id_info = id_info
            
            # Check for existing person
            exists, existing_files = FileManager.check_existing_person(id_info)
            
            if exists:
                # Show duplicate dialog
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_text = f"⚠️ [{timestamp}] Phát hiện thông tin người này đã có trong database!\n"
                log_text += f"👤 Họ tên: {id_info.get('Họ và tên', 'N/A')}\n"
                log_text += f"🆔 Số CCCD: {id_info.get('Số CCCD', 'N/A')}\n"
                log_text += f"📁 Số file đã lưu: {len(existing_files)}\n"
                log_text += f"⏳ Đang hiển thị hộp thoại xác nhận..."
                self._update_content_log(log_text, append=True)
                
                # Create and show duplicate dialog
                try:
                    from gui.dialogs.duplicate_check_dialog import DuplicateCheckDialog
                    dialog = DuplicateCheckDialog(self.root, id_info, existing_files)
                    self.root.wait_window(dialog)
                    
                    # Process user choice
                    if dialog.result == 'cancel':
                        self.qr_locked = False
                        self.detected_qrs.clear()
                        self.current_id_info = None
                        
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        message = f"❌ [{timestamp}] Đã hủy bỏ - Sẵn sàng quét QR mới"
                        self._update_content_log(message, append=True)
                        return
                    elif dialog.result == 'overwrite':
                        self._existing_file_to_overwrite = existing_files[0]
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        message = f"🔄 [{timestamp}] Đã chọn LƯU ĐÈ - File cũ sẽ bị thay thế khi lưu"
                        self._update_content_log(message, append=True)
                    else:  # 'new'
                        self._existing_file_to_overwrite = None
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        message = f"➕ [{timestamp}] Đã chọn TẠO MỚI - File mới sẽ được tạo riêng"
                        self._update_content_log(message, append=True)
                except ImportError:
                    # Fallback if dialog not available
                    self._existing_file_to_overwrite = None
                    from tkinter import messagebox
                    messagebox.showinfo("Trùng lặp", f"Đã tìm thấy {len(existing_files)} file của người này.\nSẽ tạo file mới.")
            else:
                self._existing_file_to_overwrite = None
            
            # Lock QR detection after successful scan
            self.qr_locked = True
            
            # Update data display
            for field, value in id_info.items():
                if field in self.data_labels:
                    self.data_labels[field].configure(text=value)
            
            # Enable rescan button
            if self.rescan_btn:
                self.rescan_btn.configure(state="normal")
            
            # Update log
            timestamp = datetime.now().strftime("%H:%M:%S")
            camera_info = self.camera_manager.get_current_camera_info()
            log_text = f"🎉 [{timestamp}] QR Code được nhận diện thành công từ {camera_info}!\n\n"
            log_text += f"👤 Họ tên: {id_info.get('Họ và tên', 'N/A')}\n"
            log_text += f"🆔 Số CCCD: {id_info.get('Số CCCD', 'N/A')}\n"
            log_text += f"🎂 Ngày sinh: {id_info.get('Ngày tháng năm sinh', 'N/A')}\n\n"
            
            if not exists:
                log_text += "✅ Không có trùng lặp - Đây là người mới\n"
            
            log_text += "🔒 QR đã được khóa - Thông tin sẽ được giữ nguyên\n"
            log_text += "📸 Bây giờ hãy chụp ảnh mặt trước và mặt sau CCCD!\n"
            log_text += "🔄 Nhấn 'QUÉT LẠI QR' nếu muốn quét QR mới\n"
            log_text += "🔍 Sau khi lưu có thể tìm kiếm trong database"
            
            self._update_content_log(log_text, append=True)
            self._check_expiry_warning(id_info)
            self._check_complete_status()
            
        except Exception as e:
            logger.error(f"Error processing QR data: {e}")
            timestamp = datetime.now().strftime("%H:%M:%S")
            error_message = f"❌ [{timestamp}] Lỗi xử lý QR code: {str(e)}"
            self._update_content_log(error_message, append=True)

    def _check_expiry_warning(self, id_info: Dict[str, str]):
        """Kiểm tra và hiển thị cảnh báo hết hạn"""
        expiry_date_str = id_info.get("Ngày đến hạn CCCD", "")
        
        if expiry_date_str not in ["N/A", "Không hết hạn", "Không xác định"]:
            try:
                from datetime import timedelta
                
                expiry_date = datetime.strptime(expiry_date_str, "%d/%m/%Y")
                current_date = datetime.now()
                days_until_expiry = (expiry_date - current_date).days
                
                if days_until_expiry < 0:
                    warning_msg = f"⚠️ CCCD ĐÃ HẾT HẠN từ {abs(days_until_expiry)} ngày trước!"
                    self._update_content_log(warning_msg, append=True)
                    from tkinter import messagebox
                    messagebox.showwarning("Cảnh báo hết hạn", f"CCCD đã hết hạn từ ngày {expiry_date_str}")
                elif days_until_expiry <= 365:
                    warning_msg = f"⚠️ CCCD sẽ hết hạn sau {days_until_expiry} ngày ({expiry_date_str})"
                    self._update_content_log(warning_msg, append=True)
                    
            except Exception as e:
                logger.error(f"Error checking expiry: {e}")
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        try:
            self.root.mainloop()
        finally:
            self._cleanup()
    
    def _on_closing(self):
        """Handle application closing"""
        if self.scanning:
            self.camera_buttons.stop_scanning()
        self._cleanup()
        self.root.destroy()
    
    def _cleanup(self):
        """Cleanup resources"""
        try:
            self.camera_manager.stop()
            if self.video_thread and self.video_thread.is_alive():
                self.stop_video_event.set()
                self.video_thread.join(timeout=2.0)
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")