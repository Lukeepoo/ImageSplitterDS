# ImageSplitterDS
## Image splitter for 3DS badges

A command-line utility to **split and format images** into perfectly-sized PNG tiles (64x64), ready for use as badges.

This tool supports **drag-and-drop**, **manual control**, and **smart format conversion**, all wrapped in a user-friendly, portable `.exe`.

---

## Features

- **Tile splitting** with customizable grid (e.g., 3x4, 2x5, etc.)
- **Smart aspect ratio suggestions** (like 3:4, 4:3, 16:9)
- **Automatically saves tiles** into your system's **Pictures folder**
- **Supports most image formats**: `.png`, `.jpg`, `.jpeg`, `.bmp`, `.gif`, `.webp`
- **Auto-converts non-PNG images** to PNG
- **Cleans up temporary files** after processing
- **Preview shown before splitting**
- **No dependencies required** when built as `.exe`

---

## Installation

### Option 1: Use Prebuilt Executable

1. Download `splitter.exe` from the [Releases](#) page (or build it yourself).
2. Double-click it or drag an image onto it.
3. Follow the prompts.

### Option 2: Build from Source

> Requirements: Python 3.10+ and `pillow` installed

```bash
pip install pillow
pip install pyinstaller
pyinstaller --onefile splitter.py
