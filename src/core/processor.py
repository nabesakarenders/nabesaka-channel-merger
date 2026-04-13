import os
from pathlib import Path

# Enable OpenEXR support in OpenCV (required for 32-bit EXR files)
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

import cv2
import numpy as np


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
    If float32/float64, assumes [0,1] range and scales to [0,65535].
    """
    if data.dtype == np.uint8:
        return data.astype(np.uint16) * 257
    elif data.dtype in [np.float32, np.float64]:
        return (np.clip(data, 0, 1) * 65535).astype(np.uint16)
    return data.astype(np.uint16)


def normalize_to_8bit(data):
    """
    Converts input data to uint8.
    If uint16, divides by 257.
    If float32/float64, assumes [0,1] range and scales to [0,255].
    """
    if data.dtype == np.uint16:
        return (data / 257).astype(np.uint8)
    elif data.dtype in [np.float32, np.float64]:
        return (np.clip(data, 0, 1) * 255).astype(np.uint8)
    return data.astype(np.uint8)


def normalize_to_32bit(data):
    """
    Converts input data to float32 in [0,1] range.
    If uint8, divides by 255.
    If uint16, divides by 65535.
    """
    if data.dtype == np.uint8:
        return data.astype(np.float32) / 255.0
    elif data.dtype == np.uint16:
        return data.astype(np.float32) / 65535.0
    elif data.dtype == np.float64:
        return data.astype(np.float32)
    return data.astype(np.float32)


def get_bit_depth(data):
    """
    Returns the bit depth category of the data.
    Returns: '32bit', '16bit', '8bit', or None.
    """
    if data is None:
        return None
    dtype = data.dtype
    if dtype in [np.float32, np.float64]:
        return "32bit"
    elif dtype == np.uint16:
        return "16bit"
    elif dtype == np.uint8:
        return "8bit"
    return None


def convert_bit_depth(data, target_depth):
    """
    Converts data to the target bit depth.
    target_depth: '8bit', '16bit', or '32bit'
    """
    if data is None:
        return None

    if target_depth == "32bit":
        return normalize_to_32bit(data)
    elif target_depth == "16bit":
        return normalize_to_16bit(data)
    elif target_depth == "8bit":
        return normalize_to_8bit(data)

    return data


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
            return None  # Alpha not present in grayscale usually

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


def merge_channels(channels, target_depth=None):
    """
    Merges a list of 4 distinct single-channel arrays/values into one RGBA image.
    channels: List of [R, G, B, A].
    target_depth: Optional. '8bit', '16bit', or '32bit'. If None, auto-detects highest bit depth.
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

    # Determine target bit depth
    if target_depth is None:
        # Auto-detect: use highest bit depth from inputs
        has_32bit = any(arr.dtype in [np.float32, np.float64] for arr in input_arrays)
        has_16bit = any(arr.dtype == np.uint16 for arr in input_arrays)

        if has_32bit:
            target_depth = "32bit"
        elif has_16bit:
            target_depth = "16bit"
        else:
            target_depth = "8bit"

    final_channels = []

    for c in channels:
        data = None
        if c is None:
            if target_depth == "32bit":
                data = np.zeros(target_shape, dtype=np.float32)
            elif target_depth == "16bit":
                data = np.zeros(target_shape, dtype=np.uint16)
            else:
                data = np.zeros(target_shape, dtype=np.uint8)
        elif isinstance(c, (int, float)):
            val = float(c)
            if target_depth == "32bit":
                # Normalize to [0,1] range
                if val > 1.0:
                    val = val / 255.0 if val <= 255 else val / 65535.0
                data = np.full(target_shape, val, dtype=np.float32)
            elif target_depth == "16bit":
                if val <= 1.0:
                    val = val * 65535
                elif val <= 255:
                    val = val * 257
                data = create_solid_channel(int(val), width, height, is_16bit=True)
            else:
                if val > 255:
                    val = val / 257 if val <= 65535 else val / 255
                data = create_solid_channel(int(val), width, height, is_16bit=False)
        elif isinstance(c, np.ndarray):
            if c.shape[:2] != target_shape:
                print(
                    f"Warning: Channel shape mismatch {c.shape} vs {target_shape}. Using empty."
                )
                if target_depth == "32bit":
                    data = np.zeros(target_shape, dtype=np.float32)
                elif target_depth == "16bit":
                    data = np.zeros(target_shape, dtype=np.uint16)
                else:
                    data = np.zeros(target_shape, dtype=np.uint8)
            else:
                data = c
                # Convert to target bit depth
                if target_depth == "32bit":
                    data = normalize_to_32bit(data)
                elif target_depth == "16bit":
                    data = normalize_to_16bit(data)
                else:
                    data = normalize_to_8bit(data)

        final_channels.append(data)

    merged = np.dstack(final_channels)
    return merged


def get_supported_formats_for_depth(bit_depth):
    """
    Returns a list of file extensions that support the given bit depth.
    """
    if bit_depth == "32bit":
        # 32-bit float is primarily supported by EXR, TIFF (float), and some HDR formats
        return ["exr", "tiff", "tif", "hdr"]
    elif bit_depth == "16bit":
        # 16-bit is well supported by PNG, TIFF, TGA, EXR
        return ["png", "tiff", "tif", "tga", "exr"]
    else:
        # 8-bit is supported by almost all formats
        return ["png", "jpg", "jpeg", "tiff", "tif", "tga", "bmp", "exr", "webp"]


def get_save_file_filter(bit_depth=None):
    """
    Returns a QFileDialog filter string based on the bit depth.
    """
    if bit_depth == "32bit":
        return "OpenEXR (*.exr);;TIFF (*.tiff *.tif);;HDR (*.hdr)"
    elif bit_depth == "16bit":
        return "PNG (*.png);;TIFF (*.tiff *.tif);;Targa (*.tga);;OpenEXR (*.exr)"
    else:
        return "PNG (*.png);;JPEG (*.jpg *.jpeg);;TIFF (*.tiff *.tif);;Targa (*.tga);;BMP (*.bmp);;WebP (*.webp)"


def save_image(path, data, target_depth=None):
    """
    Saves image data to the specified path.

    Args:
        path: Output file path
        data: Image data as numpy array
        target_depth: Optional bit depth conversion ('8bit', '16bit', '32bit')

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Convert bit depth if specified
        if target_depth is not None:
            data = convert_bit_depth(data, target_depth)

        # Convert RGB/RGBA -> BGR/BGRA for OpenCV
        to_save = data.copy()
        if data.ndim == 3:
            if data.shape[2] == 3:
                to_save = cv2.cvtColor(data, cv2.COLOR_RGB2BGR)
            elif data.shape[2] == 4:
                to_save = cv2.cvtColor(data, cv2.COLOR_RGBA2BGRA)

        # For EXR files, ensure float32 format
        path_str = str(path).lower()
        if path_str.endswith(".exr"):
            if to_save.dtype != np.float32:
                to_save = normalize_to_32bit(to_save)

        # cv2.imwrite automatically handles 16-bit if dtype is uint16
        # and float32 for EXR
        success = cv2.imwrite(str(path), to_save)
        return success
    except Exception as e:
        print(f"Error saving image to {path}: {e}")
        return False
