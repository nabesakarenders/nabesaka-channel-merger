import numpy as np
import cv2
import os
import sys

# Ensure src is in path
sys.path.append(os.getcwd())

from src.core.processor import merge_channels, create_solid_channel, save_image, load_image

def test_merge_logic():
    print("Testing 8-bit merge...")
    # 100x100 images
    r = create_solid_channel(255, 100, 100, is_16bit=False) # White
    g = create_solid_channel(0, 100, 100, is_16bit=False)   # Black
    b = create_solid_channel(128, 100, 100, is_16bit=False) # Grey
    a = 255
    
    merged = merge_channels([r, g, b, a])
    assert merged.shape == (100, 100, 4)
    assert merged.dtype == np.uint8
    assert merged[0,0,0] == 255
    assert merged[0,0,2] == 128
    
    print("Testing 16-bit promotion...")
    r16 = create_solid_channel(65535, 100, 100, is_16bit=True)
    merged_16 = merge_channels([r16, g, b, a])
    assert merged_16.dtype == np.uint16
    assert merged_16[0,0,0] == 65535 # R kept high
    assert merged_16[0,0,1] == 0     # G promoted 0 -> 0
    assert merged_16[0,0,2] == 128 * 257 
    assert merged_16[0,0,3] == 65535
    
    print("Testing save 16-bit PNG via OpenCV...")
    save_image("test_16bit.png", merged_16)
    
    print("Testing load 16-bit PNG via OpenCV...")
    # Use direct cv2 to verify file independently of our wrapper logic first
    raw_loaded = cv2.imread("test_16bit.png", cv2.IMREAD_UNCHANGED)
    print(f"Raw Loaded dtype: {raw_loaded.dtype}, shape: {raw_loaded.shape}")
    
    assert raw_loaded.dtype == np.uint16
    assert raw_loaded.shape == (100, 100, 4)
    
    # Check values (remember raw_loaded is BGRA in OpenCV)
    # merged_16 was RGBA: R=65535, G=0, B=32896, A=65535
    # raw_loaded BGRA: 0=B, 1=G, 2=R, 3=A
    assert raw_loaded[0,0,0] == 32896 # B
    assert raw_loaded[0,0,1] == 0     # G
    assert raw_loaded[0,0,2] == 65535 # R
    assert raw_loaded[0,0,3] == 65535 # A
    
    print("Testing wrapper load_image...")
    loaded = load_image("test_16bit.png")
    assert loaded.dtype == np.uint16
    # wrapper returns RGBA
    assert loaded[0,0,0] == 65535 # R
    assert loaded[0,0,2] == 32896 # B
    
    # Cleanup
    try:
        os.remove("test_16bit.png")
    except:
        pass
        
    print("All tests passed!")

if __name__ == "__main__":
    test_merge_logic()
