from .api import api_remover_bp

def init_remover(app):
    app.register_blueprint(api_remover_bp)