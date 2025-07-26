import customtkinter as ctk

class DataPanel:
    """Data display and capture panel"""
    
    def __init__(self, main_app):
        self.app = main_app
    
    def create_data_panel(self, parent):
        """Create adaptive data display and capture panel"""
        self.app.data_panel = ctk.CTkFrame(
            parent,
            fg_color="#1a1a1a", 
            corner_radius=12,
            border_width=2,
            border_color="#FF6600"
        )
        self.app.data_panel.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
        
        # Responsive grid configuration
        self.app.data_panel.grid_rowconfigure(0, weight=0, minsize=50)  # Header
        self.app.data_panel.grid_rowconfigure(1, weight=1)             # Data content
        self.app.data_panel.grid_rowconfigure(2, weight=0, minsize=80) # Capture controls
        self.app.data_panel.grid_columnconfigure(0, weight=1)
        
        # Panel header
        header = ctk.CTkFrame(self.app.data_panel, fg_color="#333333", corner_radius=8)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.app.data_title = ctk.CTkLabel(
            header,
            text="📄 ID INFORMATION",
            font=("Arial", 16, "bold"),
            text_color="#FF8800"
        )
        self.app.data_title.pack(pady=10)
        
        # QR Data section
        self._create_data_fields()
        
        # Capture controls
        self.app.capture_buttons.create_capture_controls(self.app.data_panel)
    
    def _create_data_fields(self):
        """Create adaptive data fields"""
        qr_frame = ctk.CTkFrame(self.app.data_panel, fg_color="#2a2a2a", corner_radius=8)
        qr_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Data fields in scrollable frame
        data_scroll = ctk.CTkScrollableFrame(qr_frame, fg_color="transparent")
        data_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create data fields
        fields = [
            "Họ và tên", "Số CCCD", "Số CMND", "Ngày tháng năm sinh", 
            "Giới tính", "Địa chỉ", "Ngày cấp CCCD", "Ngày đến hạn CCCD" 
        ]
        
        self.app.data_labels = {}
        for field in fields:
            field_container = ctk.CTkFrame(data_scroll, fg_color="#333333")
            field_container.pack(fill="x", pady=2)
            
            # Configure responsive grid
            field_container.grid_rowconfigure(0, weight=1)
            field_container.grid_rowconfigure(1, weight=1)
            field_container.grid_columnconfigure(0, weight=1)
            
            # Field label with special color for expiry date
            label_color = "#FF6666" if field == "Ngày đến hạn CCCD" else "#00DDDD"
            label = ctk.CTkLabel(
                field_container,
                text=field,
                font=("Arial", 10, "bold"),
                text_color=label_color,
                anchor="w"
            )
            label.grid(row=0, column=0, sticky="ew", padx=10, pady=2)
            
            # Field value
            value_label = ctk.CTkLabel(
                field_container,
                text="Chưa có dữ liệu",
                font=("Arial", 11),
                text_color="#FFFFFF",
                anchor="w"
            )
            value_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
            
            self.app.data_labels[field] = value_label