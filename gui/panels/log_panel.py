import customtkinter as ctk
import logging

logger = logging.getLogger(__name__)

class LogPanel:
    """Activity log panel"""
    
    def __init__(self, main_app):
        self.app = main_app
    
    def create_log_panel(self, parent):
        """Create adaptive activity log panel"""
        self.app.log_panel = ctk.CTkFrame(
            parent,
            fg_color="#1a1a1a",
            corner_radius=12,
            border_width=2,
            border_color="#9966FF"
        )
        self.app.log_panel.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="nsew")
        
        # Responsive grid configuration
        self.app.log_panel.grid_rowconfigure(0, weight=0, minsize=50)  # Header
        self.app.log_panel.grid_rowconfigure(1, weight=1)             # Log content
        self.app.log_panel.grid_columnconfigure(0, weight=1)
        
        # Panel header
        header = ctk.CTkFrame(self.app.log_panel, fg_color="#333333", corner_radius=8)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.app.log_title = ctk.CTkLabel(
            header,
            text="📊 ACTIVITY LOG",
            font=("Arial", 14, "bold"),
            text_color="#AA77FF"
        )
        self.app.log_title.pack(pady=10)
        
        # Log content with adaptive font sizing
        self.app.content_text = ctk.CTkTextbox(
            self.app.log_panel,
            fg_color="#000000",
            text_color="#00FF88",
            font=("Consolas", 9),
            corner_radius=8,
            wrap="word"
        )
        self.app.content_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Bind text widget to auto-adjust font size based on panel width
        self.app.content_text.bind('<Configure>', self._adjust_log_font)
    
    def _adjust_log_font(self, event=None):
        """Adjust log font size based on panel width"""
        try:
            if hasattr(self.app, 'log_panel'):
                panel_width = self.app.log_panel.winfo_width()
                
                # Dynamic font sizing based on panel width
                if panel_width < 200:
                    font_size = 8
                elif panel_width < 300:
                    font_size = 9
                elif panel_width < 400:
                    font_size = 10
                else:
                    font_size = 11
                
                # Update font if changed
                current_font = self.app.content_text.cget("font")
                if isinstance(current_font, tuple) and len(current_font) >= 2:
                    if current_font[1] != font_size:
                        self.app.content_text.configure(font=("Consolas", font_size))
                        
        except Exception as e:
            logger.error(f"Error adjusting log font: {e}")