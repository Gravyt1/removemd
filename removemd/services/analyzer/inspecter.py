from io import BytesIO
from .check import check_image, check_pdf, check_office, check_audio, check_video
from ..scrubber.strip import MetadataError


def clean_metadata(filepath, file_type, mimetype, fmt):
    """
    Extract the metadata of a single file.

    Returns a dict with the metadata. Raises MetadataError when the file
    type is not supported.
    """
    if file_type == 'not_supported':
        raise MetadataError(f"File type of {filepath} is not supported for metadata checker.")

    with open(filepath, "rb") as f:
        file = BytesIO(f.read())

    if file_type == 'image':
        return check_image(file)
    elif file_type == 'pdf':
        return check_pdf(file)
    elif file_type == 'office':
        return check_office(file, fmt)
    elif file_type == 'audio':
        return check_audio(file)
    elif file_type == 'video':
        return check_video(file, fmt.lower())
