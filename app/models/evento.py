from app import db
from datetime import datetime

class Evento(db.Model):
    __tablename__ = 'eventos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    nombre = db.Column(db.String(300), nullable=False)
    tipo = db.Column(db.String(50))  # congreso, conferencia, seminario, taller, etc.
    organizador = db.Column(db.String(200))
    lugar = db.Column(db.String(200))
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    rol = db.Column(db.String(50))  # ponente, organizador, asistente, etc.
    descripcion = db.Column(db.Text)
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Evento {self.nombre[:50]}>'

