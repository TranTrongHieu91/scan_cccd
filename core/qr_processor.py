import cv2
import numpy as np
from pyzbar import pyzbar
import logging

logger = logging.getLogger(__name__)

class QRProcessor:
    """Advanced QR code processing with multi-scale detection and full frame guidance"""
    
    @staticmethod
    def detect_qr_codes(frame: np.ndarray) -> list:
        """Enhanced QR detection with multiple preprocessing strategies including low-light"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Check if image is dark and needs low-light enhancement
        mean_brightness = np.mean(gray)
        is_low_light = mean_brightness < 80
        
        # Strategy 1: Direct detection on original
        barcodes = pyzbar.decode(gray)
        if barcodes:
            return barcodes
        
        # Strategy 2: Enhanced contrast with CLAHE
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        barcodes = pyzbar.decode(enhanced)
        if barcodes:
            return barcodes
        
        # Strategy 3: Low-light specific enhancements
        if is_low_light:
            # Gamma correction for dark images
            gamma_corrected = QRProcessor._adjust_gamma(gray, gamma=0.5)
            barcodes = pyzbar.decode(gamma_corrected)
            if barcodes:
                return barcodes
            
            # Brightness enhancement
            brightness_enhanced = cv2.convertScaleAbs(gray, alpha=1.5, beta=30)
            barcodes = pyzbar.decode(brightness_enhanced)
            if barcodes:
                return barcodes
            
            # Combined low-light enhancement
            low_light_enhanced = QRProcessor._enhance_low_light(gray)
            barcodes = pyzbar.decode(low_light_enhanced)
            if barcodes:
                return barcodes
        
        # Strategy 4: Sharpening filter
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        barcodes = pyzbar.decode(sharpened)
        if barcodes:
            return barcodes
        
        # Strategy 5: Adaptive thresholding with multiple parameters
        for block_size in [11, 15, 21]:
            for c_value in [2, 5, 10]:
                adaptive_thresh = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c_value
                )
                barcodes = pyzbar.decode(adaptive_thresh)
                if barcodes:
                    return barcodes
        
        return []
    
    @staticmethod
    def _adjust_gamma(image, gamma=1.0):
        """Adjust gamma correction for low-light images"""
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(image, table)
    
    @staticmethod
    def _enhance_low_light(image):
        """Comprehensive low-light image enhancement"""
        # Step 1: Gamma correction
        gamma_corrected = QRProcessor._adjust_gamma(image, gamma=0.6)
        
        # Step 2: CLAHE with aggressive settings for dark images
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4,4))
        clahe_enhanced = clahe.apply(gamma_corrected)
        
        # Step 3: Brightness and contrast adjustment
        alpha = 1.3  # Contrast control
        beta = 20    # Brightness control
        enhanced = cv2.convertScaleAbs(clahe_enhanced, alpha=alpha, beta=beta)
        
        # Step 4: Bilateral filter to reduce noise while preserving edges
        bilateral = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        return bilateral
    
    @staticmethod
    def draw_detection(frame: np.ndarray, barcode) -> np.ndarray:
        """Draw detection rectangle with guidance overlay"""
        (x, y, w, h) = barcode.rect
        
        # Draw with bright neon green accent for visibility
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 243), 4)
        cv2.putText(frame, "QR DETECTED!", (x, y - 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 243), 3)
        
        # Add success indicator
        cv2.circle(frame, (x + w//2, y + h//2), 15, (0, 255, 0), -1)
        cv2.putText(frame, "OK", (x + w//2 - 15, y + h//2 + 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    @staticmethod
    def draw_guidance_overlay(frame: np.ndarray) -> np.ndarray:
        """Draw guidance overlay optimized for full frame view"""
        height, width = frame.shape[:2]
        
        # Check lighting condition
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        is_low_light = mean_brightness < 80
        
        # Frame info overlay - show full frame size
        cv2.putText(frame, f"Full Frame: {width}x{height}", (10, height - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw center focus area - larger for full frame
        center_x, center_y = width // 2, height // 2
        focus_size = min(width, height) // 2  # Larger focus area for full frame
        
        # Main focus rectangle - different color for low light
        color = (255, 255, 0) if not is_low_light else (0, 255, 255)  # Yellow for normal, Cyan for low light
        
        # Draw main focus rectangle
        cv2.rectangle(frame, 
                     (center_x - focus_size//2, center_y - focus_size//2),
                     (center_x + focus_size//2, center_y + focus_size//2),
                     color, 2)
        
        # Corner markers - larger for full frame
        corner_size = 30
        corners = [
            (center_x - focus_size//2, center_y - focus_size//2),  # Top-left
            (center_x + focus_size//2, center_y - focus_size//2),  # Top-right
            (center_x - focus_size//2, center_y + focus_size//2),  # Bottom-left
            (center_x + focus_size//2, center_y + focus_size//2)   # Bottom-right
        ]
        
        for corner_x, corner_y in corners:
            # L-shaped corner markers
            cv2.line(frame, (corner_x - corner_size, corner_y), 
                    (corner_x - 8, corner_y), color, 4)
            cv2.line(frame, (corner_x, corner_y - corner_size), 
                    (corner_x, corner_y - 8), color, 4)
            cv2.line(frame, (corner_x + corner_size, corner_y), 
                    (corner_x + 8, corner_y), color, 4)
            cv2.line(frame, (corner_x, corner_y + corner_size), 
                    (corner_x, corner_y + 8), color, 4)
        
        # Center crosshair - larger
        cv2.line(frame, (center_x - 25, center_y), (center_x + 25, center_y), color, 3)
        cv2.line(frame, (center_x, center_y - 25), (center_x, center_y + 25), color, 3)
        
        # Add corner frame indicators to show full frame boundaries
        frame_corner_size = 40
        frame_corners = [
            (20, 20),  # Top-left
            (width - 20, 20),  # Top-right
            (20, height - 20),  # Bottom-left
            (width - 20, height - 20)  # Bottom-right
        ]
        
        frame_color = (128, 128, 128)  # Gray for frame corners
        for corner_x, corner_y in frame_corners:
            # L-shaped frame corners
            if corner_x < width // 2:  # Left side
                cv2.line(frame, (corner_x, corner_y), (corner_x + frame_corner_size, corner_y), frame_color, 2)
                if corner_y < height // 2:  # Top
                    cv2.line(frame, (corner_x, corner_y), (corner_x, corner_y + frame_corner_size), frame_color, 2)
                else:  # Bottom
                    cv2.line(frame, (corner_x, corner_y), (corner_x, corner_y - frame_corner_size), frame_color, 2)
            else:  # Right side
                cv2.line(frame, (corner_x, corner_y), (corner_x - frame_corner_size, corner_y), frame_color, 2)
                if corner_y < height // 2:  # Top
                    cv2.line(frame, (corner_x, corner_y), (corner_x, corner_y + frame_corner_size), frame_color, 2)
                else:  # Bottom
                    cv2.line(frame, (corner_x, corner_y), (corner_x, corner_y - frame_corner_size), frame_color, 2)
        
        # Instructions based on lighting - positioned for full frame
        if is_low_light:
            cv2.putText(frame, "CHE DO YEU SANG - FULL FRAME VIEW", (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(frame, "Dat QR vao khung xanh o giua", (20, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        else:
            cv2.putText(frame, "FULL FRAME MODE - Hien thi toan bo camera", (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            cv2.putText(frame, "Dat QR vao khung vang o giua", (20, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add brightness indicator
        brightness_text = f"Brightness: {int(mean_brightness)}"
        cv2.putText(frame, brightness_text, (width - 200, height - 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame