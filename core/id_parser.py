import re
from datetime import datetime
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class IDDataParser:
    """Enhanced Vietnamese ID data parsing"""
    
    FIELD_MAPPING = {
        "Số CCCD": 0,
        "Số CMND": 1,
        "Họ và tên": 2,
        "Ngày tháng năm sinh": 3,
        "Giới tính": 4,
        "Địa chỉ": 5,
        "Ngày cấp CCCD": 6,
        "Ngày đến hạn CCCD": 7
    }
    
    @classmethod
    def parse(cls, qr_content: str) -> Dict[str, str]:
        """Parse Vietnamese ID QR data with enhanced validation"""
        id_info = {field: "N/A" for field in cls.FIELD_MAPPING.keys()}
        
        try:
            lines = qr_content.split('|')
            
            for field, index in cls.FIELD_MAPPING.items():
                if index < len(lines):
                    value = lines[index].strip()
                    
                    # Special processing for dates
                    if "ngày" in field.lower() and value != "N/A":
                        value = cls._format_date(value)
                    
                    # Validate CCCD number
                    elif field == "Số CCCD" and len(value) == 12 and value.isdigit():
                        id_info[field] = value
                        continue
                    
                    # Validate CMND number
                    elif field == "Số CMND" and value.isdigit():
                        id_info[field] = value
                        continue
                    
                    id_info[field] = value
            
            # Calculate expiry date if missing
            if (id_info["Ngày đến hạn CCCD"] == "N/A" and 
                id_info["Ngày tháng năm sinh"] != "N/A" and 
                id_info["Ngày cấp CCCD"] != "N/A"):
                id_info["Ngày đến hạn CCCD"] = cls._calculate_expiry_date(
                    id_info["Ngày tháng năm sinh"], 
                    id_info["Ngày cấp CCCD"]
                )
                    
        except Exception as e:
            logger.error(f"Error parsing ID data: {e}")
            
        return id_info
    
    @staticmethod
    def _format_date(date_str: str) -> str:
        """Enhanced date formatting with multiple format support"""
        try:
            clean_date = re.sub(r'[^\d]', '', date_str.strip())
            
            if len(clean_date) == 8:
                # Try different date formats
                for fmt in ['%d%m%Y', '%Y%m%d']:
                    try:
                        date_obj = datetime.strptime(clean_date, fmt)
                        return date_obj.strftime('%d/%m/%Y')
                    except ValueError:
                        continue
            
            return date_str
        except Exception:
            return date_str

    @staticmethod
    def _calculate_expiry_date(birth_date_str: str, issue_date_str: str) -> str:
        """Calculate CCCD expiry date according to Vietnamese law"""
        try:
            birth_date = datetime.strptime(birth_date_str, "%d/%m/%Y")
            issue_date = datetime.strptime(issue_date_str, "%d/%m/%Y")
            
            # Calculate age at issue
            age_at_issue = (issue_date - birth_date).days // 365
            
            # Determine expiry age according to regulations
            if 14 <= age_at_issue < 23:
                expiry_age = 25
            elif 23 <= age_at_issue < 38:
                expiry_age = 40
            elif 38 <= age_at_issue < 58:
                expiry_age = 60
            else:
                # From 58 years old, no expiry
                return "Không hết hạn"
            
            # Calculate expiry date
            expiry_year = birth_date.year + expiry_age
            expiry_date = birth_date.replace(year=expiry_year)
            
            return expiry_date.strftime("%d/%m/%Y")
            
        except Exception as e:
            logger.error(f"Error calculating expiry date: {e}")
            return "Không xác định"

