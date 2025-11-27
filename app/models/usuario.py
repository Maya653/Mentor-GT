from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100))
    rol = db.Column(db.String(20), nullable=False, default='profesor')  # admin o profesor
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # IDs de APIs externas
    google_scholar_id = db.Column(db.String(100))
    scopus_id = db.Column(db.String(100))
    orcid_id = db.Column(db.String(100))
    
    # Relaciones
    publicaciones = db.relationship('Publicacion', backref='autor', lazy='dynamic', cascade='all, delete-orphan')
    eventos = db.relationship('Evento', backref='participante', lazy='dynamic', cascade='all, delete-orphan')
    docencias = db.relationship('Docencia', backref='profesor', lazy='dynamic', cascade='all, delete-orphan')
    documentos = db.relationship('Documento', backref='propietario', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def es_admin(self):
        return self.rol == 'admin'
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

