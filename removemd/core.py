import argparse, json, os, sys
from .utils import get_type_from_file
from .services import clean_metadata, remove_metadata, MetadataError

def scrub_metadata(filepaths: "list[str]") -> "list[str]":
    """
    Remove metadata from a list of files and save the cleaned versions.

    Args:
        filepaths (list[str]): List of file paths to process.

    Returns:
        list[str]: List of paths to the cleaned output files, written next
        to the originals as "cleaned_<name>".

    Raises:
        FileNotFoundError: If a file does not exist.
        MetadataError: If a file is not supported or cannot be processed.
    """
    if isinstance(filepaths, str):
        filepaths = [filepaths]
    cleaned_files = []

    for filepath in filepaths:
        file_type, mimetype, fmt = get_type_from_file(filepath)
        output = remove_metadata(filepath, file_type, mimetype, fmt)

        directory, filename = os.path.split(filepath)
        out_path = os.path.join(directory, f"cleaned_{filename}")
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

    # Windows consoles may not be able to print emojis or accented metadata.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except AttributeError:
            pass

    failures = 0
    for f in args.files:
        try:
            if args.mode == "remove":
                cf = scrub_metadata([f])[0]
                print(f"✅ Cleaned file saved: {cf}")
            else:
                metadata = analyze_metadata(f)
                print(f"📄 Metadata for {f}:")
                print(json.dumps(metadata, indent=4, ensure_ascii=False, default=str))
        except (OSError, MetadataError) as e:
            failures += 1
            print(f"❌ {f}: {e}", file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
