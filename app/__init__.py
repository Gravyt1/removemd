from flask import Flask, render_template
from .modules import modules


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    for module in modules():
        module(app)

    @app.route('/')
    def home():
        return render_template('index.html')
    
    @app.route('/analyzer')
    def analyzer():
        return render_template('analyzer.html')

    return app