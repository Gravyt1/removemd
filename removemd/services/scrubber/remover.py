from .strip import *

def remove_metadata(filepath, file_type, mimetype, fmt):
    """
    Main function to handle metadata removal from uploaded files.
    
    Delegates to appropriate handler functions based on number of files.
    """
    if isinstance(filepath, list):
        return remove_metadata_from_multiple(filepath, file_type, mimetype, fmt)
    else:
        return remove_metadata_from_single(filepath, file_type, mimetype, fmt)
            
def remove_metadata_from_single(filepath, file_type, mimetype, fmt):
    """
    Process metadata removal for a single uploaded file.
    
    Determines file type and applies appropriate stripping function.
    Returns cleaned content and mimetype as a tuple.
    """
    with open(filepath, "rb") as f:
        file = BytesIO(f.read())


    # Handle unsupported file types
    if file_type == 'not_supported':
        return f"File type of {file.filename} is not supported for metadata removal."
    
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

    return cleaned_content

def remove_metadata_from_multiple(filepath, file_type, mimetype, fmt):
    """
    Process metadata removal for multiple uploaded files.
    
    Iterates through each file, determines its type, and applies appropriate stripping.
    Returns a list of tuples containing cleaned content, mimetype, and original filename.
    """
    cleaned_files = []
    
    for file in filepath:
        with open(file, "rb") as f:
            file = BytesIO(f.read())

        if file_type == 'not_supported':
            return f"File type of {file.filename} is not supported for metadata removal."
        
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
