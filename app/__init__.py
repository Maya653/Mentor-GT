from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

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
    
    # Habilitar soporte para llaves foráneas en SQLite
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    import sqlite3
    
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        if isinstance(dbapi_conn, sqlite3.Connection):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder.'
    
    # Registro de Blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.docente_controller import docente_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(docente_bp, url_prefix='/docente')
    
    # Contexto global para templates del docente
    @app.context_processor
    def inject_docente():
        from flask_login import current_user
        if current_user.is_authenticated and not current_user.es_admin():
            from app.models.docente import Docente
            docente = Docente.query.filter_by(user_id=current_user.id).first()
            return {'current_docente': docente}
        return {'current_docente': None}
    
    # Ruta raíz
    @app.route('/')
    def index():
        from flask import redirect, url_for
        from flask_login import current_user
        if current_user.is_authenticated:
            if current_user.es_admin():
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('docente.dashboard'))
        return redirect(url_for('auth.login'))
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))

