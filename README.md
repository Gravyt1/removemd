# 🧼 RemoveMD

🚀 **Protect your privacy by removing metadata from your files.**  
Supports images, PDF documents, Office files, audio, and video.

## 🔒 Why RemoveMD?

Metadata can contain sensitive information such as:
- 📍 GPS location  
- 🧑‍💼 Author name  
- 📱 Device model  
- 🕵️‍♂️ Technical details invisible to the naked eye  

RemoveMD helps you clean all that up in seconds.

---

## 🧰 Features

- ✂️ Removes sensitive metadata (location, author, device, etc.)  
- 📁 Batch processing (handle multiple files at once)  
- 🖥️ Command-line interface (CLI) and Python library  
- 🛡️ Open source and privacy-friendly  

---

## 📦 Installation

```bash
pip install removemd
```

---

## ⚡ Usage

### 🖥️ Command Line

```bash
removemd file1.jpg file2.pdf file3.mp3
```

➡️ This generates cleaned files like `cleaned_file1.jpg`, `cleaned_file2.pdf`, etc.

### 🐍 Python

```python
import removemd

# Clean multiple files
removemd.scrub_metadata(["image.jpg", "document.pdf"])

# Analyze metadata from a file
metadata = removemd.analyze_metadata("image.jpg")
print(metadata)
```

---

## 🛠️ Development

```bash
git clone https://github.com/Gravyt1/removemd.git
cd removemd
pip install -e .
```

---

## 🌐 Hosted Version

👉 Try the online version at [removemd.com](https://removemd.com)  
Unlimited processing, premium features, and an intuitive interface.
You can support me by using this website.

---

