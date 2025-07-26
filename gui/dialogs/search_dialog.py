import customtkinter as ctk
import os
from datetime import datetime
from tkinter import messagebox, filedialog
from typing import Dict, Any, List
from database.search_manager import SearchManager
from gui.dialogs.view_record_dialog import ViewRecordDialog
import csv
import logging

logger = logging.getLogger(__name__)


class SearchDialog(ctk.CTkToplevel):
    """Advanced search dialog for CCCD records"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("🔍 Tìm kiếm CCCD Records - Database")
        self.geometry("1200x800")
        self.resizable(True, True)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.search_results = []
        
        self._create_ui()
        self._load_initial_data()
        
        # Center the dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_ui(self):
        """Create search interface"""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid
        main_frame.grid_rowconfigure(2, weight=1)  # Results area
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        self._create_header(main_frame)
        
        # Search controls
        self._create_search_controls(main_frame)
        
        # Results area
        self._create_results_area(main_frame)
        
        # Bottom controls
        self._create_bottom_controls(main_frame)
    
    def _create_header(self, parent):
        """Create header section"""
        header_frame = ctk.CTkFrame(parent, fg_color="#333333", corner_radius=10)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Title and stats
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=15)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🔍 CCCD DATABASE SEARCH",
            font=("Arial", 24, "bold"),
            text_color="#00FFFF"
        )
        title_label.pack(side="left")
        
        # Stats
        self.stats_label = ctk.CTkLabel(
            title_frame,
            text="Loading statistics...",
            font=("Arial", 12),
            text_color="#AAAAAA"
        )
        self.stats_label.pack(side="right")
    
    def _create_search_controls(self, parent):
        """Create search controls section"""
        search_frame = ctk.CTkFrame(parent, fg_color="#2a2a2a", corner_radius=10)
        search_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # Search input row
        input_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=15)
        
        # Search type dropdown
        ctk.CTkLabel(input_frame, text="Tìm kiếm:", font=("Arial", 12, "bold")).pack(side="left", padx=(0, 10))
        
        self.search_type = ctk.CTkOptionMenu(
            input_frame,
            values=["Tất cả", "Tên", "Số CCCD", "Số CMND", "Ngày tháng", "Ngày hết hạn"],
            width=120
        )
        self.search_type.pack(side="left", padx=(0, 10))
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Nhập từ khóa tìm kiếm...",
            width=300,
            font=("Arial", 12)
        )
        self.search_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
        self.search_entry.bind("<Return>", lambda e: self._perform_search())
        
        # Search button
        search_btn = ctk.CTkButton(
            input_frame,
            text="🔍 TÌM KIẾM",
            command=self._perform_search,
            width=120,
            height=32,
            fg_color="#0088FF",
            hover_color="#0066CC"
        )
        search_btn.pack(side="left", padx=(0, 10))
        
        # Clear button
        clear_btn = ctk.CTkButton(
            input_frame,
            text="🔄 XÓA BỘ LỌC",
            command=self._clear_search,
            width=120,
            height=32,
            fg_color="#FF6600",
            hover_color="#CC4400"
        )
        clear_btn.pack(side="left")
        
        # Quick stats
        self.result_stats = ctk.CTkLabel(
            search_frame,
            text="",
            font=("Arial", 11),
            text_color="#00FF88"
        )
        self.result_stats.pack(pady=(0, 10))
    
    def _create_results_area(self, parent):
        """Create results display area"""
        results_frame = ctk.CTkFrame(parent, fg_color="#1a1a1a", corner_radius=10)
        results_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Results header
        header_frame = ctk.CTkFrame(results_frame, fg_color="#333333")
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text="📋 KẾT QUẢ TÌM KIẾM",
            font=("Arial", 16, "bold"),
            text_color="#FFFF00"
        ).pack(pady=10)
        
        # Results container with scrollbar
        self.results_container = ctk.CTkScrollableFrame(
            results_frame,
            fg_color="#000000",
            scrollbar_fg_color="#333333"
        )
        self.results_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def _create_bottom_controls(self, parent):
        """Create bottom control buttons"""
        bottom_frame = ctk.CTkFrame(parent, fg_color="#333333", corner_radius=10)
        bottom_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        button_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=15)
        
        # Export button
        export_btn = ctk.CTkButton(
            button_frame,
            text="📊 XUẤT EXCEL",
            command=self._export_results,
            width=150,
            height=40,
            fg_color="#228B22",
            hover_color="#1E7B1E"
        )
        export_btn.pack(side="left", padx=(0, 10))
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            button_frame,
            text="🔄 LÀM MỚI",
            command=self._refresh_data,
            width=150,
            height=40,
            fg_color="#9966FF",
            hover_color="#7744DD"
        )
        refresh_btn.pack(side="left", padx=(0, 10))
        
        # Close button
        close_btn = ctk.CTkButton(
            button_frame,
            text="❌ ĐÓNG",
            command=self.destroy,
            width=150,
            height=40,
            fg_color="#FF4444",
            hover_color="#CC3333"
        )
        close_btn.pack(side="right")
    
    def _load_initial_data(self):
        """Load initial data and statistics"""
        try:
            # Load statistics
            stats = SearchManager.get_statistics()
            stats_text = f"📊 {stats['total_records']} records | 💾 {stats['total_size_mb']} MB | 📄 {stats['records_with_word']} docs | 📷 {stats['records_with_images']} có ảnh"
            self.stats_label.configure(text=stats_text)
            
            # Load all records initially
            self._clear_search()
            
        except Exception as e:
            logger.error(f"Error loading initial data: {e}")
            self.stats_label.configure(text="❌ Lỗi tải dữ liệu")
    
    def _perform_search(self):
        """Perform search based on current criteria"""
        try:
            query = self.search_entry.get().strip()
            
            # Map UI selection to search type
            search_type_map = {
                "Tất cả": "all",
                "Tên": "name", 
                "Số CCCD": "cccd",
                "Số CMND": "cmnd",
                "Ngày tháng": "date",
                "Ngày hết hạn": "expiry"
            }
            
            selected_type = self.search_type.get()
            search_type = search_type_map.get(selected_type, "all")
            
            # Perform search
            self.search_results = SearchManager.search_records(query, search_type)
            
            # Update results display
            self._display_results()
            
            # Update stats
            result_count = len(self.search_results)
            if query:
                self.result_stats.configure(
                    text=f"🔍 Tìm thấy {result_count} kết quả cho '{query}' trong '{selected_type}'"
                )
            else:
                self.result_stats.configure(
                    text=f"📋 Hiển thị tất cả {result_count} records"
                )
            
        except Exception as e:
            logger.error(f"Error performing search: {e}")
            self.result_stats.configure(text="❌ Lỗi tìm kiếm")
    
    def _clear_search(self):
        """Clear search and show all records"""
        self.search_entry.delete(0, "end")
        self.search_type.set("Tất cả")
        self.search_results = SearchManager.search_records("", "all")
        self._display_results()
        
        result_count = len(self.search_results)
        self.result_stats.configure(text=f"📋 Hiển thị tất cả {result_count} records")
    
    def _display_results(self):
        """Display search results"""
        # Clear existing results
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        if not self.search_results:
            no_results_label = ctk.CTkLabel(
                self.results_container,
                text="🔍 Không tìm thấy kết quả nào\n\nThử thay đổi từ khóa tìm kiếm hoặc loại tìm kiếm",
                font=("Arial", 14),
                text_color="#AAAAAA"
            )
            no_results_label.pack(pady=50)
            return
        
        # Display results
        for i, record in enumerate(self.search_results):
            self._create_result_item(record, i)
    
    def _create_result_item(self, record: Dict[str, Any], index: int):
        """Create a result item widget"""
        # Alternating colors
        bg_color = "#1a1a1a" if index % 2 == 0 else "#2a2a2a"
        
        item_frame = ctk.CTkFrame(
            self.results_container,
            fg_color=bg_color,
            corner_radius=8
        )
        item_frame.pack(fill="x", padx=5, pady=2)
        
        # Configure grid
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Left: Person info
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        
        # Name
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"👤 {record['name']}",
            font=("Arial", 14, "bold"),
            text_color="#00FFFF",
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        # ID numbers
        id_text = f"🆔 CCCD: {record['cccd']}"
        if record['cmnd'] != "N/A":
            id_text += f" | CMND: {record['cmnd']}"
        
        id_label = ctk.CTkLabel(
            info_frame,
            text=id_text,
            font=("Arial", 11),
            text_color="#FFFFFF",
            anchor="w"
        )
        id_label.pack(anchor="w")
        
        # Birth date and gender
        personal_text = f"🎂 {record['birth_date']}"
        if record['gender'] != "N/A":
            personal_text += f" | {record['gender']}"
        
        personal_label = ctk.CTkLabel(
            info_frame,
            text=personal_text,
            font=("Arial", 10),
            text_color="#CCCCCC",
            anchor="w"
        )
        personal_label.pack(anchor="w")
        
        # Center: File info
        file_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        file_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        
        # File status
        file_status = []
        if record['word_path'] and os.path.exists(record['word_path']):
            file_status.append("📄 Word")
        if record['front_image'] and os.path.exists(record['front_image']):
            file_status.append("📸 Front")
        if record['back_image'] and os.path.exists(record['back_image']):
            file_status.append("📸 Back")
        
        status_text = " | ".join(file_status) if file_status else "❌ Thiếu file"
        
        status_label = ctk.CTkLabel(
            file_frame,
            text=status_text,
            font=("Arial", 10),
            text_color="#00FF88" if file_status else "#FF6666",
            anchor="w"
        )
        status_label.pack(anchor="w")
        
        # Created date and size
        meta_text = f"📅 {record['created']} | 💾 {record['size_mb']} MB"
        meta_label = ctk.CTkLabel(
            file_frame,
            text=meta_text,
            font=("Arial", 9),
            text_color="#AAAAAA",
            anchor="w"
        )
        meta_label.pack(anchor="w")
        
        # Right: Action buttons
        action_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        action_frame.grid(row=0, column=2, sticky="e", padx=15, pady=10)
        
        # View button
        view_btn = ctk.CTkButton(
            action_frame,
            text="👁️ XEM",
            command=lambda r=record: self._view_record(r),
            width=80,
            height=30,
            fg_color="#0088FF",
            hover_color="#0066CC",
            font=("Arial", 10)
        )
        view_btn.pack(pady=2)
        
        # Open folder button
        folder_btn = ctk.CTkButton(
            action_frame,
            text="📁 FOLDER",
            command=lambda r=record: self._open_record_folder(r),
            width=80,
            height=30,
            fg_color="#FF8800",
            hover_color="#CC6600",
            font=("Arial", 10)
        )
        folder_btn.pack(pady=2)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ XÓA",
            command=lambda r=record: self._delete_record(r),
            width=80,
            height=30,
            fg_color="#FF4444",
            hover_color="#CC3333",
            font=("Arial", 10)
        )
        delete_btn.pack(pady=2)
    
    def _view_record(self, record: Dict[str, Any]):
        """View detailed record information"""
        ViewRecordDialog(self, record)
    
    def _open_record_folder(self, record: Dict[str, Any]):
        """Open folder containing record files"""
        try:
            folder_path = os.path.dirname(record['json_path'])
            if os.name == 'nt':
                os.startfile(folder_path)
            elif os.name == 'posix':
                os.system(f'open "{folder_path}"')
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở thư mục: {str(e)}")
    
    def _delete_record(self, record: Dict[str, Any]):
        """Delete record and associated files"""
        response = messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa record của:\n{record['name']}\n\n"
            "Tất cả file liên quan sẽ bị xóa vĩnh viễn!"
        )
        
        if response:
            try:
                files_to_delete = [
                    record['json_path'],
                    record['front_image'],
                    record['back_image'],
                    record['word_path']
                ]
                
                deleted_count = 0
                for file_path in files_to_delete:
                    if file_path and os.path.exists(file_path):
                        os.remove(file_path)
                        deleted_count += 1
                
                messagebox.showinfo("Thành công", f"Đã xóa {deleted_count} file của {record['name']}")
                
                # Refresh display
                self._perform_search()
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa: {str(e)}")
    
    def _export_results(self):
        """Export search results to Excel"""
        try:
            if not self.search_results:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xuất!")
                return
            
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Lưu file CSV"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Header
                    writer.writerow([
                        "Họ và tên", "Số CCCD", "Số CMND", "Ngày sinh", 
                        "Giới tính", "Địa chỉ", "Ngày cấp", "Ngày tạo", 
                        "Kích thước (MB)", "Có Word", "Có ảnh"
                    ])
                    
                    # Data rows
                    for record in self.search_results:
                        writer.writerow([
                            record['name'],
                            record['cccd'],
                            record['cmnd'],
                            record['birth_date'],
                            record['gender'],
                            record.get('address', 'N/A'),
                            record.get('issue_date', 'N/A'),
                            record['created'],
                            record['size_mb'],
                            "Có" if record['word_path'] else "Không",
                            "Có" if (record['front_image'] or record['back_image']) else "Không"
                        ])
                
                messagebox.showinfo("Thành công", f"Đã xuất {len(self.search_results)} records ra file:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xuất file: {str(e)}")
    
    def _refresh_data(self):
        """Refresh data and statistics"""
        self._load_initial_data()