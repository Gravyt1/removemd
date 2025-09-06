from flask import jsonify
from .type import get_type_from_file
from .analyze import *

def check_metadata(request_file):
    """
    Main function to handle metadata checher from uploaded file.
    
    Validates the number of files and delegates to appropriate handler functions.
    Returns JSON response with error message for invalid inputs.
    """
    # Check if any file were provided
    if not request_file:
        return jsonify({"message": "No file provided in the request."}), 400
    
    return check_metadata_from_file(request_file)


def check_metadata_from_file(file):
    """
    Process metadata checking for a single uploaded file.
    
    Determines file type and applies appropriate stripping function.
    Returns cleaned content and mimetype as a tuple.
    """

    file_type, mimetype, fmt = get_type_from_file(file.filename)

    # Handle unsupported file types
    if file_type == 'not_supported':
        return jsonify({"message": f"File type of {file.filename} is not supported for metadata checker."}), 400
    
    # Process image files
    elif file_type == 'image':
        content_info = check_image(file, fmt)

    # Process PDF files
    elif file_type == 'pdf':
        content_info = check_pdf(file)
    
    # Process office documents (Word, Excel, PowerPoint)
    elif file_type == 'office':
        content_info = check_office(file, fmt)
    
    # Process audio files (audio/video)
    elif file_type == 'audio':
        content_info = check_audio(file, fmt)

    elif file_type == 'video':
        content_info = check_video(file, fmt)
    
    # Return cleaned content and mimetype
    return content_info, mimetype, file.filename