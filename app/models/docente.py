from app import db
from datetime import datetime

class Docente(db.Model):
    __tablename__ = 'docentes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    cvu = db.Column(db.String(50), unique=True)
    nombre_completo = db.Column(db.String(255), nullable=False)
    curp = db.Column(db.String(18), unique=True)
    rfc = db.Column(db.String(13))
    sexo = db.Column(db.String(20))
    fecha_nacimiento = db.Column(db.Date)
    pais_nacimiento = db.Column(db.String(100))
    nacionalidad = db.Column(db.String(100))
    estado_civil = db.Column(db.String(50))
    domicilio = db.Column(db.Text)
    correo_principal = db.Column(db.String(255))
    orcid = db.Column(db.String(100))
    researcher_id = db.Column(db.String(100))
    scopus_author_id = db.Column(db.String(100))
    pubmed_query = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    formaciones = db.relationship('FormacionAcademica', backref='docente', lazy='dynamic', cascade='all, delete-orphan')
    empleos = db.relationship('Empleo', backref='docente', lazy='dynamic', cascade='all, delete-orphan')
    idiomas = db.relationship('Idioma', backref='docente', lazy='dynamic', cascade='all, delete-orphan')
    cursos = db.relationship('CursoImpartido', backref='docente', lazy='dynamic', cascade='all, delete-orphan')
    proyectos = db.relationship('ProyectoInvestigacion', backref='docente', lazy='dynamic', cascade='all, delete-orphan')
    articulos = db.relationship('Articulo', backref='docente', lazy='dynamic', cascade='all, delete-orphan')
    libros = db.relationship('Libro', backref='docente', lazy='dynamic', cascade='all, delete-orphan')
    congresos = db.relationship('Congreso', backref='docente', lazy='dynamic', cascade='all, delete-orphan')
    tesis = db.relationship('TesisDirigida', backref='docente', lazy='dynamic', cascade='all, delete-orphan')
    desarrollos = db.relationship('DesarrolloTecnologico', backref='docente', lazy='dynamic', cascade='all, delete-orphan')
    actividades = db.relationship('ActividadGeneral', backref='docente', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Docente {self.nombre_completo}>'

