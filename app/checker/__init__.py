from .api import api_viewer_bp

def init_viewer(app):
    app.register_blueprint(api_viewer_bp)