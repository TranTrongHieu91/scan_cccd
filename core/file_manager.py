import os
import json
import glob
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from config import Config
import logging

logger = logging.getLogger(__name__)

class FileManager:
    """Enhanced file management with duplicate detection and overwrite protection"""
    
    @staticmethod
    def ensure_directories():
        """Ensure all required directories exist"""
        directories = [Config.OUTPUT_DIR, Config.SCAN_DIR]
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Directory ensured: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                raise
    
    @staticmethod
    def check_existing_person(id_info: Dict[str, str]) -> Tuple[bool, List[Dict[str, str]]]:
        """Check if person already exists in system"""
        matching_files = []
        
        try:
            # Get person identifiers
            person_name = id_info.get("Họ và tên", "").strip()
            cccd_number = id_info.get("Số CCCD", "").strip()
            cmnd_number = id_info.get("Số CMND", "").strip()
            
            if not any([person_name, cccd_number, cmnd_number]):
                return False, []
            
            # Check JSON files in scan directory
            json_files = glob.glob(os.path.join(Config.SCAN_DIR, "*_data.json")) + \
                        glob.glob(os.path.join(Config.SCAN_DIR, "*.json"))
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                        
                        # Check for matches
                        matches = False
                        
                        # Match by CCCD number
                        if cccd_number and cccd_number != "N/A":
                            if existing_data.get("Số CCCD", "") == cccd_number:
                                matches = True
                        
                        # Match by CMND number
                        elif cmnd_number and cmnd_number != "N/A":
                            if existing_data.get("Số CMND", "") == cmnd_number:
                                matches = True
                        
                        # Match by name (if no ID numbers)
                        elif person_name and person_name != "N/A":
                            if existing_data.get("Họ và tên", "") == person_name:
                                matches = True
                        
                        if matches:
                            # Get associated files
                            base_name = json_file.replace('_data.json', '').replace('.json', '')
                            file_info = {
                                'json_path': json_file,
                                'front_image': base_name + '_F.jpg',
                                'back_image': base_name + '_B.jpg',
                                'name': existing_data.get("Họ và tên", "N/A"),
                                'cccd': existing_data.get("Số CCCD", "N/A"),
                                'cmnd': existing_data.get("Số CMND", "N/A"),
                                'created': datetime.fromtimestamp(os.path.getmtime(json_file)).strftime("%d/%m/%Y %H:%M:%S")
                            }
                            
                            # Find associated Word document
                            doc_pattern = f"CCCD_COMPLETE_{FileManager._safe_filename(person_name)}*.docx"
                            doc_files = glob.glob(os.path.join(Config.OUTPUT_DIR, doc_pattern))
                            if doc_files:
                                file_info['word_path'] = doc_files[0]
                            
                            matching_files.append(file_info)
                
                except Exception as e:
                    logger.warning(f"Error checking file {json_file}: {e}")
                    continue
            
            return len(matching_files) > 0, matching_files
            
        except Exception as e:
            logger.error(f"Error checking existing person: {e}")
            return False, []
    
    @staticmethod
    def _safe_filename(name: str) -> str:
        """Convert name to safe filename"""
        safe_name = re.sub(r'[^\w\s-]', '', name).strip()
        return re.sub(r'[-\s]+', '_', safe_name)
    
    @staticmethod
    def get_folder_stats(directory: str) -> Dict[str, int]:
        """Get folder statistics"""
        stats = {"total_files": 0, "total_size_mb": 0}
        
        try:
            if os.path.exists(directory):
                total_size = 0
                file_count = 0
                
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.exists(file_path):
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                
                stats["total_files"] = file_count
                stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)
        
        except Exception as e:
            logger.error(f"Error getting folder stats: {e}")
        
        return stats