import argparse, json, os
from .utils import get_type_from_file
from .services import clean_metadata, remove_metadata

def scrub_metadata(filepaths: list[str]) -> list[str]:
    """
    Remove metadata from a list of files and save the cleaned versions.

    Args:
        filepaths (list[str]): List of file paths to process.

    Returns:
        list[str]: List of paths to the cleaned output files.
    """
    cleaned_files = []

    for filepath in filepaths:
        file_type, mimetype, fmt = get_type_from_file(filepath)
        output = remove_metadata(filepath, file_type, mimetype, fmt)

        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)

        out_path = f"cleaned_{name}{ext}"
        with open(out_path, "wb") as f:
            f.write(output.getvalue())

        cleaned_files.append(out_path)

    return cleaned_files


def analyze_metadata(filepath: str) -> dict:
    """
    Analyze and return the metadata of a file.

    Args:
        filepath (str): Path to the file to analyze.

    Returns:
        dict: Extracted metadata as a dictionary.
    """
    file_type, mimetype, fmt = get_type_from_file(filepath)
    metadata = clean_metadata(filepath, file_type, mimetype, fmt)
    return metadata


def main():
    """
    Entry point for the 'removemd' CLI.
    Allows you to remove or analyze metadata from the command line.
    """
    parser = argparse.ArgumentParser(
        prog="removemd",
        description="Remove or analyze metadata from files (images, PDFs, Office, audio, video)."
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="One or more files to process"
    )
    parser.add_argument(
        "--mode",
        choices=["remove", "analyze"],
        default="remove",
        help="Operation mode: remove (clean metadata) or analyze (display metadata)"
    )

    args = parser.parse_args()

    if args.mode == "remove":
        cleaned_files = scrub_metadata(args.files)
        for cf in cleaned_files:
            print(f"✅ Cleaned file saved: {cf}")
    else:
        for f in args.files:
            metadata = analyze_metadata(f)
            print(f"📄 Metadata for {f}:")
            print(json.dumps(metadata, indent=4, ensure_ascii=False))
