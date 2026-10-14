from io import BytesIO
from .strip import (
    MetadataError, strip_image, strip_pdf, strip_office, strip_audio, strip_video,
)

_STRIPPERS = {
    'image': strip_image,
    'pdf': lambda file, fmt: strip_pdf(file),
    'office': strip_office,
    'audio': strip_audio,
    'video': strip_video,
}


def remove_metadata(filepath, file_type, mimetype, fmt):
    """
    Remove metadata from a file (or a list of files of the same type).

    Returns a BytesIO with the cleaned content, or a list of
    (BytesIO, mimetype, filepath) tuples when given a list.
    Raises MetadataError when a file cannot be processed.
    """
    if isinstance(filepath, list):
        return [(remove_metadata_from_single(p, file_type, mimetype, fmt), mimetype, p)
                for p in filepath]
    return remove_metadata_from_single(filepath, file_type, mimetype, fmt)


def remove_metadata_from_single(filepath, file_type, mimetype, fmt):
    stripper = _STRIPPERS.get(file_type)
    if stripper is None:
        raise MetadataError(f"File type of {filepath} is not supported for metadata removal.")
    with open(filepath, "rb") as f:
        file = BytesIO(f.read())
    return stripper(file, fmt)
