from app import db
from datetime import datetime

class Docencia(db.Model):
    __tablename__ = 'docencias'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    nombre_curso = db.Column(db.String(200), nullable=False)
    nivel = db.Column(db.String(50))  # licenciatura, maestría, doctorado
    institucion = db.Column(db.String(200))
    periodo = db.Column(db.String(50))  # semestre, año, etc.
    año = db.Column(db.Integer)
    horas = db.Column(db.Integer)
    descripcion = db.Column(db.Text)
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Docencia {self.nombre_curso[:50]}>'

