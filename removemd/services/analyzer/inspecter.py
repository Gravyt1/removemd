from .check import *

def clean_metadata(file, file_type, mimetype, fmt):
    """
    Process metadata checking for a single uploaded file.
    
    Determines file type and applies appropriate stripping function.
    Returns cleaned content and mimetype as a tuple.
    """

    # Handle unsupported file types
    if file_type == 'not_supported':
        return print(f"File type of {file.filename} is not supported for metadata checker.")
    
    # Process image files
    elif file_type == 'image':
        content_info = check_image(file)

    # Process PDF files
    elif file_type == 'pdf':
        content_info = check_pdf(file)
    
    # Process office documents (Word, Excel, PowerPoint)
    elif file_type == 'office':
        content_info = check_office(file, fmt)
    
    # Process audio files (audio/video)
    elif file_type == 'audio':
        content_info = check_audio(file)

    elif file_type == 'video':
        content_info = check_video(file, fmt)
    
    # Return cleaned content and mimetype
    return content_info