from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_class=Config):
    import os
    basedir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(basedir, 'views')
    static_dir = os.path.join(basedir, 'static')
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder.'
    
    # Registro de Blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.profesor_controller import profesor_bp
    from app.controllers.cv_controller import cv_bp
    from app.controllers.publicacion_controller import publicacion_bp
    from app.controllers.sync_controller import sync_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(profesor_bp, url_prefix='/profesor')
    app.register_blueprint(cv_bp, url_prefix='/cv')
    app.register_blueprint(publicacion_bp, url_prefix='/publicaciones')
    app.register_blueprint(sync_bp, url_prefix='/sync')
    
    # Ruta raíz
    @app.route('/')
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            if current_user.es_admin():
                from flask import redirect, url_for
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('profesor.dashboard'))
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models.usuario import Usuario
    return Usuario.query.get(int(user_id))

