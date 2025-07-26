import os
import json
import glob
import re
from datetime import datetime
from typing import Dict, List, Any
from config import Config
import logging

logger = logging.getLogger(__name__)

class SearchManager:
    """Enhanced search functionality for CCCD records"""
    
    @staticmethod
    def search_records(query: str, search_type: str = "all") -> List[Dict[str, Any]]:
        """Search CCCD records by different criteria"""
        results = []
        
        try:
            # Get all JSON files
            json_files = glob.glob(os.path.join(Config.SCAN_DIR, "*_data.json")) + \
                        glob.glob(os.path.join(Config.SCAN_DIR, "*.json"))
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Check if this record matches the search
                    if SearchManager._matches_search(data, query, search_type):
                        record = SearchManager._build_record_info(json_file, data)
                        results.append(record)
                        
                except Exception as e:
                    logger.warning(f"Error reading {json_file}: {e}")
                    continue
            
            # Sort results by creation date (newest first)
            results.sort(key=lambda x: x.get('created_timestamp', 0), reverse=True)
            
        except Exception as e:
            logger.error(f"Error searching records: {e}")
        
        return results
    
    @staticmethod
    def _matches_search(data: Dict[str, Any], query: str, search_type: str) -> bool:
        """Check if a record matches search criteria"""
        query_lower = query.lower().strip()
        
        if not query_lower:
            return True  # Empty query returns all
        
        # Extract searchable fields
        name = data.get("Họ và tên", "").lower()
        cccd = data.get("Số CCCD", "").lower()
        cmnd = data.get("Số CMND", "").lower()
        birth_date = data.get("Ngày tháng năm sinh", "").lower()
        address = data.get("Địa chỉ", "").lower()
        gender = data.get("Giới tính", "").lower()
        issue_date = data.get("Ngày cấp CCCD", "").lower()
        expiry_date = data.get("Ngày đến hạn CCCD", "").lower()
        
        if search_type == "all":
            # Search in all fields
            searchable_text = f"{name} {cccd} {cmnd} {birth_date} {address} {gender} {issue_date} {expiry_date}"
            return query_lower in searchable_text
        elif search_type == "name":
            return query_lower in name
        elif search_type == "cccd":
            return query_lower in cccd
        elif search_type == "cmnd":
            return query_lower in cmnd
        elif search_type == "date":
            return query_lower in birth_date or query_lower in issue_date or query_lower in expiry_date
        elif search_type == "expiry":
            return query_lower in expiry_date

        return False
    
    @staticmethod
    def _build_record_info(json_file: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive record information"""
        base_name = json_file.replace('_data.json', '').replace('.json', '')
        
        record = {
            'json_path': json_file,
            'data': data,
            'name': data.get("Họ và tên", "N/A"),
            'cccd': data.get("Số CCCD", "N/A"),
            'cmnd': data.get("Số CMND", "N/A"),
            'birth_date': data.get("Ngày tháng năm sinh", "N/A"),
            'address': data.get("Địa chỉ", "N/A"),
            'gender': data.get("Giới tính", "N/A"),
            'issue_date': data.get("Ngày cấp CCCD", "N/A"),
        }
        
        # File timestamps
        try:
            created_time = os.path.getmtime(json_file)
            record['created_timestamp'] = created_time
            record['created'] = datetime.fromtimestamp(created_time).strftime("%d/%m/%Y %H:%M:%S")
        except:
            record['created'] = "N/A"
            record['created_timestamp'] = 0
        
        # Associated files
        record['front_image'] = None
        record['back_image'] = None
        record['word_path'] = None
        
        # Find front and back images
        possible_front_patterns = [
            f"{base_name}_F.jpg", f"{base_name}_front.jpg", 
            f"{base_name}_F.png", f"{base_name}_front.png"
        ]
        possible_back_patterns = [
            f"{base_name}_B.jpg", f"{base_name}_back.jpg",
            f"{base_name}_B.png", f"{base_name}_back.png"
        ]
        
        for pattern in possible_front_patterns:
            if os.path.exists(pattern):
                record['front_image'] = pattern
                break
        
        for pattern in possible_back_patterns:
            if os.path.exists(pattern):
                record['back_image'] = pattern
                break
        
        # Find Word document
        safe_name = re.sub(r'[^\w\s-]', '', record['name']).strip()
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        
        doc_patterns = [
            f"CCCD_COMPLETE_{safe_name}*.docx",
            f"CCCD_{safe_name}*.docx",
            f"*{safe_name}*.docx"
        ]
        
        for pattern in doc_patterns:
            doc_files = glob.glob(os.path.join(Config.OUTPUT_DIR, pattern))
            if doc_files:
                record['word_path'] = doc_files[0]
                break
        
        # Calculate file sizes
        record['total_size'] = 0
        for file_path in [record['json_path'], record['front_image'], record['back_image'], record['word_path']]:
            if file_path and os.path.exists(file_path):
                try:
                    record['total_size'] += os.path.getsize(file_path)
                except:
                    pass
        
        record['size_mb'] = round(record['total_size'] / (1024 * 1024), 2)
        
        return record
    
    @staticmethod
    def get_statistics() -> Dict[str, Any]:
        """Get database statistics"""
        stats = {
            'total_records': 0,
            'total_size_mb': 0,
            'records_with_word': 0,
            'records_with_images': 0,
            'oldest_record': None,
            'newest_record': None
        }
        
        try:
            records = SearchManager.search_records("", "all")
            stats['total_records'] = len(records)
            
            total_size = 0
            for record in records:
                total_size += record.get('total_size', 0)
                
                if record.get('word_path'):
                    stats['records_with_word'] += 1
                
                if record.get('front_image') or record.get('back_image'):
                    stats['records_with_images'] += 1
            
            stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            
            if records:
                stats['oldest_record'] = records[-1]['created']
                stats['newest_record'] = records[0]['created']
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
        
        return stats
