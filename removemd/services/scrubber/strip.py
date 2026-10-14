import datetime, tempfile, os, subprocess
from PIL import Image, ImageFile, ImageSequence
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from docx import Document
from openpyxl import load_workbook
from pptx import Presentation

ImageFile.LOAD_TRUNCATED_IMAGES = True


class MetadataError(Exception):
    """A file could not be processed."""


STRIP_AUDIO_FORMATS = [
    "mp3", "flac", "ogg", "opus", "wav", "aac", "m4a",
    "wma", "asf", "aiff", "alac", "ape", "mpc", "wv"
]
STRIP_VIDEO_FORMATS = [
    "mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "mpeg", "mpg", "3gp", "3g2"
]

# Extensions Pillow reads but writes under another format name.
PILLOW_SAVE_FORMAT = {"JFIF": "JPEG", "PGM": "PPM", "PBM": "PPM", "PNM": "PPM"}
MULTI_FRAME_FORMATS = ("GIF", "WEBP", "PNG", "TIFF")

# Never let ffmpeg open anything but local files.
LOCAL_INPUT_ONLY = ['-protocol_whitelist', 'file']

_EXIF_ORIENTATION = 0x0112
_ORIENTATION_TRANSPOSE = {
    2: Image.Transpose.FLIP_LEFT_RIGHT,
    3: Image.Transpose.ROTATE_180,
    4: Image.Transpose.FLIP_TOP_BOTTOM,
    5: Image.Transpose.TRANSPOSE,
    6: Image.Transpose.ROTATE_270,
    7: Image.Transpose.TRANSVERSE,
    8: Image.Transpose.ROTATE_90,
}


def _upright_transposition(image):
    """
    The transposition the EXIF Orientation tag asks viewers to apply, or None.
    The tag is removed with the rest of the EXIF, so the rotation has to be
    applied to the pixels or the picture comes back sideways.
    """
    if image.format == "TIFF":
        # Pillow already rotates TIFF images when decoding.
        return None
    try:
        orientation = image.getexif().get(_EXIF_ORIENTATION)
    except Exception:
        return None
    return _ORIENTATION_TRANSPOSE.get(orientation)


def strip_image(file, fmt):
    try:
        image = Image.open(file)
        image.load()
        save_format = PILLOW_SAVE_FORMAT.get(fmt.upper(), fmt.upper())
        save_params = {"format": save_format}
        transposition = _upright_transposition(image)

        # Animations and multi-page files: every frame is kept.
        if save_format in MULTI_FRAME_FORMATS and getattr(image, "n_frames", 1) > 1:
            loop = image.info.get("loop")
            frames, durations = [], []
            for frame in ImageSequence.Iterator(image):
                frame.load()
                durations.append(frame.info.get("duration"))
                copy = frame.copy()
                if transposition is not None:
                    copy = copy.transpose(transposition)
                frames.append(copy)
            save_params.update({"save_all": True, "append_images": frames[1:]})
            if save_format != "TIFF":
                if all(d is not None for d in durations):
                    save_params["duration"] = durations
                if loop is not None:
                    save_params["loop"] = loop
            image = frames[0]
        elif transposition is not None:
            image = image.transpose(transposition)

        if save_format == "JPEG":
            if image.mode not in ("RGB", "L", "CMYK"):
                image = image.convert("RGB")
            save_params["quality"] = 95

        cleaned_image_io = BytesIO()
        image.save(cleaned_image_io, **save_params)
        cleaned_image_io.seek(0)
        return cleaned_image_io
    except Exception as e:
        raise MetadataError(f"Error processing image file: {e}") from e


def strip_pdf(file):
    try:
        reader = PdfReader(file)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        cleaned_pdf = BytesIO()
        writer.write(cleaned_pdf)
        cleaned_pdf.seek(0)
        return cleaned_pdf
    except Exception as e:
        raise MetadataError(f"Error processing PDF file: {e}") from e


def strip_office(file, fmt):
    text_attrs = [
        "author", "title", "subject", "keywords", "comments", "last_modified_by",
        "category", "content_status", "identifier", "language", "version",
    ]
    now = datetime.datetime.now()
    try:
        cleaned_office = BytesIO()
        file.seek(0)

        if fmt in ("DOCX", "PPTX"):
            doc = Document(file) if fmt == "DOCX" else Presentation(file)
            props = doc.core_properties
            for attr in text_attrs:
                setattr(props, attr, "")
            props.revision = 1
            props.created = now
            props.modified = now
            props.last_printed = now
            doc.save(cleaned_office)

        elif fmt == "XLSX":
            wb = load_workbook(file)
            props = wb.properties
            # openpyxl uses its own (camelCase) property names.
            for attr in ("creator", "title", "description", "subject", "identifier",
                         "language", "lastModifiedBy", "category", "contentStatus",
                         "version", "keywords"):
                setattr(props, attr, None)
            props.lastPrinted = None
            props.revision = None
            props.created = now
            props.modified = now
            wb.save(cleaned_office)

        else:
            raise MetadataError(f"Unsupported Office file format: {fmt}")

        cleaned_office.seek(0)
        return cleaned_office
    except MetadataError:
        raise
    except Exception as e:
        raise MetadataError(f"Error processing Office file: {e}") from e


def _run_ffmpeg(file, fmt, options, kind):
    file.seek(0)
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{fmt}') as temp_input:
        temp_input.write(file.read())
        temp_input_name = temp_input.name
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{fmt}') as temp_output:
        temp_output_name = temp_output.name

    try:
        cmd = ['ffmpeg', '-nostdin', *LOCAL_INPUT_ONLY, '-i', temp_input_name,
               *options, '-loglevel', 'error', '-y', temp_output_name]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                stdin=subprocess.DEVNULL, timeout=300)
        if result.returncode != 0:
            raise MetadataError(f"Error processing {kind} file with FFmpeg: {result.stderr.strip()}")
        if os.path.getsize(temp_output_name) == 0:
            raise MetadataError(f"Error processing {kind} file - empty output")
        with open(temp_output_name, 'rb') as f:
            return BytesIO(f.read())
    except FileNotFoundError as e:
        raise MetadataError("FFmpeg is required for audio and video files but was not found in PATH.") from e
    except subprocess.TimeoutExpired as e:
        raise MetadataError(f"{kind.capitalize()} processing timed out") from e
    finally:
        for temp_file in [temp_input_name, temp_output_name]:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except OSError:
                pass


def strip_audio(file, fmt):
    if fmt.lower() not in STRIP_AUDIO_FORMATS:
        raise MetadataError(f"Audio format not supported: {fmt}")
    return _run_ffmpeg(file, fmt.lower(), [
        '-map_metadata', '-1',
        '-fflags', '+bitexact',  # no "encoder=Lavf..." tag
        '-c', 'copy',
    ], "audio")


def strip_video(file, fmt):
    if fmt.lower() not in STRIP_VIDEO_FORMATS:
        raise MetadataError(f"Video format not supported: {fmt}")
    return _run_ffmpeg(file, fmt.lower(), [
        '-map', '0',
        '-map_metadata', '-1',
        '-map_metadata:s', '-1',  # per-stream tags (handler name, language...)
        '-map_chapters', '-1',
        '-fflags', '+bitexact',
        '-c', 'copy',
        '-movflags', 'faststart',
    ], "video")
