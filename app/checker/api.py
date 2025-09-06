# [file name]: api_viewer.py
from flask import Blueprint, request, jsonify, Response
from .checker import check_metadata

api_viewer_bp = Blueprint('api_viewer', __name__)

@api_viewer_bp.route('/api/analyze', methods=['POST'])
def analyze_metadata():
    """API endpoint for metadata analysis"""
    try:
        try:
            # Get list of uploaded files from the request
            request_file = request.files.get('file')
                 
            output = check_metadata(request_file)
            content_info, mimetype, filename = output
            return jsonify({
                "filename": filename,
                "mimetype": mimetype,
                "metadata": content_info.get("metadata", content_info.get("error", {}))
            })
        except ValueError:
            if isinstance(output[0], Response):
                return output

    except Exception as e:
        return jsonify({"message": "Error processing file checking request."}), 500