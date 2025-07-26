import os
import sys
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration"""
    CAMERA_WIDTH = 800
    CAMERA_HEIGHT = 600
    
    # Xử lý đường dẫn cho cả .py và .exe
    if getattr(sys, 'frozen', False):
        # Đang chạy từ file exe
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        # Đang chạy từ file .py
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Lưu vào thư mục con cùng với file cài đặt
    OUTPUT_DIR = os.path.join(BASE_DIR, "CCCD_Documents")  # File Word
    SCAN_DIR = os.path.join(BASE_DIR, "CCCD_Images")       # File ảnh và JSON
    
    MAX_FPS = 30
    QR_DETECTION_INTERVAL = 0.1
    APP_TITLE = "🇻🇳 AGRIBANK ID Scanner - Professional UI with Search"
    VERSION = "4.0.0"