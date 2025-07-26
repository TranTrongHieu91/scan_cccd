#!/usr/bin/env python3
"""
AGRIBANK ID Scanner - Professional CCCD/CMND Scanner with Advanced Search
Version 2.8.0 - Modular Architecture
"""

import sys
import os
import logging
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def show_startup_message():
    """Display startup banner with search features"""
    banner = f"""
╔{'═' * 80}╗
║{' ' * 80}║
║{'🆔 AGRIBANK ID SCANNER + ADVANCED SEARCH DATABASE'.center(80)}║
║{f'Version {Config.VERSION} | Professional Modular Architecture'.center(80)}║
║{' ' * 80}║
║{'🔍 ADVANCED SEARCH FEATURES v2.8.0:'.center(80)}║
║{'• 🗄️ Complete database search engine'.center(80)}║
║{'• 📊 Real-time statistics and analytics'.center(80)}║
║{'• 👁️ Detailed record viewer with file management'.center(80)}║
║{'• 🔄 Smart duplicate detection and handling'.center(80)}║
║{'• 📋 Excel export for data analysis'.center(80)}║
║{'• 🗑️ Safe cleanup and maintenance tools'.center(80)}║
║{'• 📁 Comprehensive file management system'.center(80)}║
║{' ' * 80}║
║{'🏗️ MODULAR ARCHITECTURE:'.center(80)}║
║{'• 📐 Separated UI panels and dialogs'.center(80)}║
║{'• 🎯 Dedicated button functionality modules'.center(80)}║
║{'• 📱 Core components isolation'.center(80)}║
║{'• ⚡ Database and utilities separation'.center(80)}║
║{'• 🖥️ Professional code organization'.center(80)}║
║{'• 📹 Maintainable and scalable design'.center(80)}║
║{'• 🔍 Easy debugging and enhancement'.center(80)}║
║{' ' * 80}║
╚{'═' * 80}╝
"""
    print(banner)


def main():
    """Main application entry point"""
    try:
        # Set high DPI awareness for Windows
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        
        show_startup_message()
        
        # Import and create main application
        from gui.main_window import VietnameseIDScannerGUI
        app = VietnameseIDScannerGUI()
        
        # Run the application
        app.run()
        
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        import tkinter.messagebox as messagebox
        messagebox.showerror("Startup Error", f"Failed to start application: {str(e)}")


if __name__ == "__main__":
    main()