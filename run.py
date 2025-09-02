from app import create_app

APP = create_app()

if __name__ == '__main__':
    APP.run(port=5000, debug=True)