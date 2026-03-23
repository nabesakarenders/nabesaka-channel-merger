# Texture Channel Merger

A desktop GUI application for combining image channels (R, G, B, A) from separate source images into a single output texture. Useful for game developers and texture artists who need to pack multiple grayscale maps into an RGBA texture.

## Features

- Load images for individual R, G, B, or Alpha channels
- Smart loading: automatically populates RGB channels when dropping a color image
- Value mode: set channels to solid values (0-255) instead of images
- Real-time preview of merged result
- Support for 8-bit and 16-bit images
- Export to PNG, TGA, TIFF, or EXR formats
- Resolution mismatch detection and validation

## Installation

```bash
# Clone the repository
git clone https://github.com/nabesaka/ChannelMerger.git
cd ChannelMerger

# Create and activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py
```

1. For each channel (R, G, B, A), select **Image** mode and drag-drop an image, or use **Value** mode to set a solid value
2. Select which channel from the image to use (Red, Green, Blue, Alpha, or Gray)
3. Preview updates automatically
4. Click **Export Merged Texture** to save

## Building

```bash
# Windows
pyinstaller --noconfirm --onefile --windowed --name "ChannelMerger" --icon "assets/images/app_icon.ico" --add-data "assets;assets" --paths "." --clean src/main.py

# Linux
pyinstaller --noconfirm --onefile --windowed --name "ChannelMerger" --icon "assets/images/app_icon.ico" --add-data "assets:assets" --paths "." --clean src/main.py
```

## License

MIT
