# RemoveMD - Metadata Removal Tool

**RemoveMD** is a modern, open-source, privacy-first tool to remove metadata from your files (images, videos, PDFs, audio, Office documents, and more).  
This code is the one used on www.removemd.com without limitations.

It provides a clean web interface to **scrub your files** while ensuring:  
- 🚫 **No file storage** (all processing happens in memory)  
- 🔒 **Anonymous usage** (no email required, anonymous IDs only)  
- 📦 **Multi-format compatibility** (images, videos, audio, PDFs, Office documents, etc.)  

---

## ✨ Features
- 🖼️ **Image Metadata Remover**: strip EXIF, GPS, and sensitive data from photos  
- 📄 **PDF Metadata Scrubber**: securely clean hidden PDF metadata  
- 🎥 **Video Metadata Cleaner**: anonymize your videos before sharing  
- 🎧 **Audio Metadata Scrubber**: remove hidden tags from audio files  
- 🏢 **Office Document Cleaner**: clean Word, Excel, and PowerPoint files  
- 👀 **Metadata Viewer (coming soon)**  

---

## ⚙️ Installation

### 1. Install FFmpeg

**Debian / Ubuntu**
```bash
sudo apt update
sudo apt install ffmpeg -y
```

**macOS (Homebrew)**
```bash
brew install ffmpeg
```

**Windows**  
Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/), then add it to your PATH.

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

Run the Flask server locally:
```bash
python run.py
```

Then open your browser at:
```
http://127.0.0.1:5000
```

➡️ Upload your files and download the cleaned versions without metadata.

---

## 📜 License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).  
👉 See the [LICENSE](LICENSE) file for full details.

(Sorry front-end developers, I did the front end with AI, because I'm not good at it)
