# Texture Channel Merger

A desktop GUI application for combining image channels (R, G, B, A) from separate source images into a single output texture. Useful for game developers and texture artists who need to pack multiple grayscale maps into an RGBA texture.

## Features

- Load images for individual R, G, B, or Alpha channels
- Smart loading: automatically populates RGB channels when dropping a color image
- Value mode: set channels to solid values (0-255) instead of images
- Real-time preview of merged result
- Support for 8-bit and 16-bit images, experimental support for 32-bit images.
- Export to PNG, TGA, TIFF, or EXR formats, experimental support for other file formats supported by OpenCV library.
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
## Important Note
This project was developed with the help of various LLMs. It is **NOT** vibe coded. It was not and is not built entirely by *AI*. LLMs were used to fill holes in my knowledge and help code sections I have absolutely no knowledge in.

While the project has been checked by myself for issues, my Python knowledge is mediocre at best, so I encourage you to check out the source instead of relying on pre-built binaries if you have the time/knowledge to do so. To the best of my knowledge it is free of major bugs or issues but as is with any random open source project you fine online, **you use this at your own risk**.

## Known Issues

- Issue with X asset being missing when built for Linux

## License

MIT
