import numpy as np
import cv2
from pathlib import Path

def load_image(file_path):
    """
    Loads an image from the file path using OpenCV.
    Returns a numpy array in RGB/RGBA format.
    """
    try:
        # IMREAD_UNCHANGED loads the image as is (including alpha, 16-bit, etc.)
        img = cv2.imread(str(file_path), cv2.IMREAD_UNCHANGED)
        
        if img is None:
            return None

        # Handle Color Conversion BGR -> RGB
        if img.ndim == 3:
            if img.shape[2] == 3:
                # BGR -> RGB
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            elif img.shape[2] == 4:
                # BGRA -> RGBA
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        
        return img
    except Exception as e:
        print(f"Error loading image {file_path}: {e}")
        return None

def normalize_to_16bit(data):
    """
    Converts input data to uint16.
    If uint8, scales by 257.
    """
    if data.dtype == np.uint8:
        return (data.astype(np.uint16) * 257)
    return data.astype(np.uint16)

def normalize_to_8bit(data):
    """
    Converts input data to uint8.
    """
    if data.dtype == np.uint16:
        return (data / 257).astype(np.uint8)
    return data.astype(np.uint8)

def get_channel_data(image_data, channel_index):
    """
    Extracts a specific channel from the image data.
    If image is grayscale (2D), returns it as is.
    If channel_index is out of bounds, returns None.
    """
    if image_data is None:
        return None
        
    if image_data.ndim == 2:
        if channel_index < 3:
            return image_data
        else:
            return None # Alpha not present in grayscale usually
    
    if channel_index < image_data.shape[2]:
        return image_data[:, :, channel_index]
    return None

def create_solid_channel(value, width, height, is_16bit=False):
    """
    Creates a solid color channel.
    value: 0-255 (if 8bit) or 0-65535 (if 16bit).
    """
    dtype = np.uint16 if is_16bit else np.uint8
    return np.full((height, width), value, dtype=dtype)

def merge_channels(channels):
    """
    Merges a list of 4 distinct single-channel arrays/values into one RGBA image.
    channels: List of [R, G, B, A].
    Returns a merged numpy array (H, W, 4).
    """
    target_shape = None
    input_arrays = []
    
    for c in channels:
        if isinstance(c, np.ndarray):
            input_arrays.append(c)
            if target_shape is None:
                target_shape = c.shape[:2]
    
    if target_shape is None:
        return None 
        
    height, width = target_shape
    is_16bit = any(arr.dtype == np.uint16 for arr in input_arrays)
    
    final_channels = []
    
    for c in channels:
        data = None
        if c is None:
            dtype = np.uint16 if is_16bit else np.uint8
            data = np.zeros(target_shape, dtype=dtype)
        elif isinstance(c, (int, float)):
            val = int(c)
            if is_16bit and val <= 255: 
                val = val * 257
            data = create_solid_channel(val, width, height, is_16bit)
        elif isinstance(c, np.ndarray):
            if c.shape[:2] != target_shape:
                print(f"Warning: Channel shape mismatch {c.shape} vs {target_shape}. Using empty.")
                dtype = np.uint16 if is_16bit else np.uint8
                data = np.zeros(target_shape, dtype=dtype)
            else:
                data = c
                if is_16bit:
                    data = normalize_to_16bit(data)
                elif not is_16bit and data.dtype != np.uint8:
                     data = normalize_to_8bit(data)
        
        final_channels.append(data)
        
    merged = np.dstack(final_channels)
    return merged

def save_image(path, data):
    try:
        # Convert RGB/RGBA -> BGR/BGRA for OpenCV
        to_save = data.copy()
        if data.ndim == 3:
            if data.shape[2] == 3:
                to_save = cv2.cvtColor(data, cv2.COLOR_RGB2BGR)
            elif data.shape[2] == 4:
                to_save = cv2.cvtColor(data, cv2.COLOR_RGBA2BGRA)
        
        # cv2.imwrite automatically handles 16-bit if dtype is uint16
        success = cv2.imwrite(str(path), to_save)
        return success
    except Exception as e:
        print(f"Error saving image to {path}: {e}")
        return False
