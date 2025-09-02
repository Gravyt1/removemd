import datetime, tempfile, os, subprocess
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from docx import Document
from openpyxl import load_workbook
from pptx import Presentation
from mutagen import File as MutagenFile
from flask import jsonify

def strip_image(file, fmt):
    """
    Remove metadata from an image file by recreating it without metadata.
    
    Args:
        file: The image file object to process
        fmt: The image format (e.g., 'JPEG', 'PNG')
    
    Returns:
        BytesIO: A buffer containing the cleaned image data
    """
    try:
        # Open the image and extract pixel data only (no metadata)
        image = Image.open(file)
        data = list(image.getdata())
        
        # Create a new image with the same pixel data but no metadata
        cleaned_image = Image.new(image.mode, image.size)
        cleaned_image.putdata(data)
        
        # Save the cleaned image to a buffer
        cleaned_image_io = BytesIO()
        cleaned_image.save(cleaned_image_io, format=fmt)
        cleaned_image_io.seek(0)

        return cleaned_image_io
    
    except Exception as e:
        return jsonify({"message": "Error processing image file."}), 500

def strip_pdf(file):
    """
    Remove metadata from a PDF file while preserving content.
    
    Args:
        file: The PDF file object to process
    
    Returns:
        BytesIO: A buffer containing the cleaned PDF data
    """
    try:
        # Read the PDF and create a clean writer
        reader = PdfReader(file)
        writer = PdfWriter()

        # Copy all pages (content) without metadata
        for page in reader.pages:
            writer.add_page(page)

        # Write the cleaned PDF to a buffer
        cleaned_pdf = BytesIO()
        writer.write(cleaned_pdf)
        cleaned_pdf.seek(0)
        
        return cleaned_pdf
    
    except Exception as e:
        return jsonify({"message": "Error processing PDF file."}), 500

def strip_office(file, fmt):
    """
    Remove metadata from Microsoft Office documents (DOCX, XLSX, PPTX).
    
    Args:
        file: The Office file object to process
        fmt: The office format (DOCX, XLSX, or PPTX)
    
    Returns:
        BytesIO: A buffer containing the cleaned Office document
    """
    try:
        cleaned_office = BytesIO()
        file.seek(0)
        
        # List of text attributes to clear from metadata
        text_attrs = [
            "author", "title", "subject", "keywords", "comments", "last_modified_by",
            "category", "content_status", "identifier", "language", "version", "creator",
            "description", "manager", "company", "hyperlink_base"
        ]
        now = datetime.datetime.now()

        # Process Word documents
        if fmt == "DOCX":
            doc = Document(file)
            # Clear all text metadata attributes
            for attr in text_attrs:
                setattr(doc.core_properties, attr, "")
            # Set revision to 1 and update timestamps
            doc.core_properties.revision = 1
            doc.core_properties.created = now
            doc.core_properties.modified = now
            doc.save(cleaned_office)

        # Process Excel spreadsheets
        elif fmt == "XLSX":
            wb = load_workbook(file)
            # Clear all text metadata attributes
            for attr in text_attrs:
                setattr(wb.properties, attr, "")
            # Set revision to 1 and update timestamps
            wb.properties.revision = 1
            wb.properties.created = now
            wb.properties.modified = now
            wb.save(cleaned_office)

        # Process PowerPoint presentations
        elif fmt == "PPTX":
            prs = Presentation(file)
            # Clear all text metadata attributes
            for attr in text_attrs:
                setattr(prs.core_properties, attr, "")
            # Set revision to 1 and update timestamps
            prs.core_properties.revision = 1
            prs.core_properties.created = now
            prs.core_properties.modified = now
            prs.save(cleaned_office)

        else:
            return jsonify({"message": f"Unsupported Office file format: {fmt}"}), 400

        cleaned_office.seek(0)
        return cleaned_office

    except Exception as e:
        return jsonify({"message": "Error processing Office file."}), 500

def strip_audio(file, fmt):
    """
    Remove metadata from audio files (audio formats supported currently).
    
    Args:
        file: The audio file object to process
        fmt: The audio format (e.g., 'mp3', 'flac')
    
    Returns:
        BytesIO: A buffer containing the cleaned audio file
    """
    # List of supported audio formats
    audio = [
        "mp3", "flac", "ogg", "opus", "wv", "asf", "wma", "mpc", "m4a", "aac", "aiff", "ape", "wav"
    ]

    try:
        # Process audio files using Mutagen library
        if fmt.lower() in audio:
            file.seek(0)
            file_bytes = BytesIO(file.read())
            file_bytes.seek(0)
            
            # Load file and delete all metadata
            media = MutagenFile(fileobj=file_bytes, filename=file.filename)
            media.delete()
            
            # Save the cleaned file
            file_bytes.seek(0)
            media.save(file_bytes)
            file_bytes.seek(0)
            return file_bytes
        else:
            return jsonify({"message": "Format not available for use for the moment."}), 400
        
    except Exception as e:
        return jsonify({"message": "Error processing audio file."}), 500

def strip_video(file, fmt):
    """
    Remove metadata from video files (video formats supported currently).
    
    Args:
        file: The video file object to process
        fmt: The video format (e.g., 'mp4', 'mkv')
    
    Returns:
        BytesIO: A buffer containing the cleaned video file
    """
    # List of supported video formats
    supported_formats = [
        "mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "mpeg", "mpg", "3gp"
    ]

    if fmt.lower() not in supported_formats:
        return jsonify({"message": "Format not available for use for the moment."}), 400
    
    # Reset file pointer to beginning
    file.seek(0)
    
    # Create temporary input file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{fmt}') as temp_input:
        temp_input.write(file.read())
        temp_input_name = temp_input.name
    
    # Create temporary output file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{fmt}') as temp_output:
        temp_output_name = temp_output.name
    
    try:
        # Use ffmpeg to copy streams without metadata
        cmd = [
            'ffmpeg',
            '-i', temp_input_name,
            '-map', '0',
            '-c', 'copy',
            '-movflags', 'faststart',
            '-loglevel', 'error',
            '-y',  # Overwrite output file without asking
            temp_output_name
        ]
        
        # Execute ffmpeg command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return jsonify({"message": "Error processing video file."}), 500
        
        # Read the cleaned video into BytesIO
        cleaned_video = BytesIO()
        with open(temp_output_name, 'rb') as f:
            cleaned_video.write(f.read())
        
        # Reset pointer to beginning of BytesIO object
        cleaned_video.seek(0)
        
        return cleaned_video
        
    except subprocess.TimeoutExpired:
        return jsonify({"message": "Error processing video file, it may be corrupted."}), 500
    except Exception as e:
        return jsonify({"message": "Error processing video file."}), 500
    finally:
        # Cleanup temporary files
        for temp_file in [temp_input_name, temp_output_name]:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass  # Ignore errors during cleanup