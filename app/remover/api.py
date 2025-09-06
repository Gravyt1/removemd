from flask import Blueprint, request, send_file, jsonify
from .remover import remove_metadata
from io import BytesIO
import zipfile
from werkzeug.utils import secure_filename

# Create a Blueprint for API routes related to metadata removal
api_remover_bp = Blueprint('api_remover', __name__)

@api_remover_bp.route('/api/remove', methods=['POST'])
def remove():
    """
    Handle POST requests to remove metadata from uploaded files.
    
    Supports both single file and multiple files (returned as a zip archive).
    Returns the cleaned file(s) as downloadable attachment(s).
    """
    try:
        # Get list of uploaded files from the request
        request_files = request.files.getlist("file")
        
        # Process files to remove metadata
        output = remove_metadata(request_files)  # plus de current_user

        # Handle single file output
        if isinstance(output, tuple):
            cleaned_content, mimetype, filename = output
            safe_filename = secure_filename(filename)
            download_name = f"cleaned_{safe_filename}"
            
            return send_file(
                cleaned_content,
                as_attachment=True,
                download_name=download_name,
                mimetype=mimetype
            )

        # Handle multiple files output (returns as a zip archive)
        elif isinstance(output, list):
            zip_buffer = BytesIO()
            
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for cleaned_content, mimetype, original_name in output:
                    zip_file.writestr(f"cleaned_{original_name}", cleaned_content.read())
                    cleaned_content.seek(0)

            zip_buffer.seek(0)
            
            return send_file(
                zip_buffer,
                as_attachment=True,
                download_name="cleaned_files.zip",
                mimetype="application/zip"
            )
    
    except Exception as e:
        print(f"Error processing file removal request: {e}")
        return jsonify({"message": "Error processing file removal request."}), 500
