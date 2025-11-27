from app import db
from datetime import datetime

class Documento(db.Model):
    __tablename__ = 'documentos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    nombre = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(50))  # cv, certificado, diploma, etc.
    ruta_archivo = db.Column(db.String(500), nullable=False)
    tamaño = db.Column(db.Integer)  # en bytes
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Documento {self.nombre}>'

