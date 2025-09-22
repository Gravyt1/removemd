import mimetypes, os

def get_type_from_file(filepath):
    """
    Determine the file type and metadata based on the filename extension.
    
    Args:
        filepath (str): The path of the file.
        
    Returns:
        tuple: A tuple containing:
            - file_type (str): Category of file ('image', 'pdf', 'office', 'media', or 'not_supported')
            - mimetype (str): The MIME type of the file (e.g., 'image/jpeg')
            - format (str): The uppercase file format (e.g., 'JPEG', 'PDF', 'DOCX')
    """

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    filename = os.path.basename(filepath)
    
    
    # Extract file extension (without the dot) and convert to lowercase
    ext = filename.split('.')[-1].lower()
    
    # Guess MIME type based on filename
    mimetype, _ = mimetypes.guess_type(filename)
    
    # List of image formats supported by Pillow library
    pillow_formats = [
        'jpg', 'jpeg', 'png', 'tiff', 'bmp', 'gif', 'webp',
        'ppm', 'pgm', 'pbm', 'pnm', 'tif', 'ico', 'icns',
        'jfif', 'pcx', 'sgi', 'tga', 'xbm', 'xpm'
    ]

    # Check if file is an image format supported by Pillow
    if ext in pillow_formats:
        # Standardize format names for consistency
        if ext == 'jpg':
            ext = 'jpeg'
        if ext == 'tif':
            ext = 'tiff'
        return 'image', mimetype, ext.upper()
    
    # Check if file is a PDF
    elif ext == 'pdf':
        return 'pdf', mimetype, ext.upper()
    
    # Check if file is a Microsoft Office document
    elif ext in ['docx', 'xlsx', 'pptx']:
        return 'office', mimetype, ext.upper()
    
    # Check if file is a supported audio format
    elif ext in ["mp3", "flac", "ogg", "opus", "wv", "asf", "wma", "mpc", "m4a", "aac", "aiff", "ape", "wav"]:
        return 'audio', mimetype, ext.upper()
    
    elif ext in ["mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "mpeg", "mpg", "3gp", "3g2"]:
        return 'video', mimetype, ext.upper()
    
    # File format is not supported
    else:
        return 'not_supported', mimetype, ext.upper()