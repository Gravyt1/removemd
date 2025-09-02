from .type import get_type_from_file
from .strip import *
from flask import jsonify

def remove_metadata(request_files):
    """
    Main function to handle metadata removal from uploaded files.
    
    Delegates to appropriate handler functions based on number of files.
    """
    # Check if any files were provided
    if not request_files:
        return jsonify({"message": "No files provided in the request."}), 400

    num_files = len(request_files)
    
    # Delegate to appropriate handler
    if num_files == 1:
        return remove_metadata_from_single(request_files)
    else:
        return remove_metadata_from_multiple(request_files)
            
def remove_metadata_from_single(request_files):
    """
    Process metadata removal for a single uploaded file.
    
    Determines file type and applies appropriate stripping function.
    Returns cleaned content and mimetype as a tuple.
    """
    file = request_files[0]
    
    # Determine file type, mimetype, and format
    file_type, mimetype, fmt = get_type_from_file(file.filename)

    # Handle unsupported file types
    if file_type == 'not_supported':
        return jsonify({"message": f"File type of {file.filename} is not supported for metadata removal."}), 400
    
    # Process files according to type
    if file_type == 'image':
        cleaned_content = strip_image(file, fmt)
    elif file_type == 'pdf':
        cleaned_content = strip_pdf(file)
    elif file_type == 'office':
        cleaned_content = strip_office(file, fmt)
    elif file_type == 'audio':
        cleaned_content = strip_audio(file, fmt)
    elif file_type == 'video':
        cleaned_content = strip_video(file, fmt)

    return cleaned_content, mimetype, file.filename

def remove_metadata_from_multiple(request_files):
    """
    Process metadata removal for multiple uploaded files.
    
    Iterates through each file, determines its type, and applies appropriate stripping.
    Returns a list of tuples containing cleaned content, mimetype, and original filename.
    """
    cleaned_files = []
    
    for file in request_files:
        file_type, mimetype, fmt = get_type_from_file(file.filename)

        if file_type == 'not_supported':
            return jsonify({"message": f"File type of {file.filename} is not supported for metadata removal."}), 400
        
        if file_type == 'image':
            cleaned_content = strip_image(file, fmt)
        elif file_type == 'pdf':
            cleaned_content = strip_pdf(file)
        elif file_type == 'office':
            cleaned_content = strip_office(file, fmt)
        elif file_type == 'audio':
            cleaned_content = strip_audio(file, fmt)
        elif file_type == 'video':
            cleaned_content = strip_video(file, fmt)

        cleaned_files.append((cleaned_content, mimetype, file.filename))
    
    return cleaned_files
