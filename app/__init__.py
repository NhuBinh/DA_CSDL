from flask import Flask

def create_app():
    app = Flask(__name__)

    # Cấu hình ứng dụng
    app.config['SECRET_KEY'] = 'nhubinh1809'

    # Đăng ký blueprint
    from .routes import main
    app.register_blueprint(main)

    return app
