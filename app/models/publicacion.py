from app import db
from datetime import datetime

class Publicacion(db.Model):
    __tablename__ = 'publicaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    titulo = db.Column(db.String(500), nullable=False)
    autores = db.Column(db.Text)  # Lista de autores separados por comas
    revista = db.Column(db.String(300))
    volumen = db.Column(db.String(50))
    numero = db.Column(db.String(50))
    paginas = db.Column(db.String(50))
    año = db.Column(db.Integer)
    doi = db.Column(db.String(200))
    isbn = db.Column(db.String(100))
    tipo = db.Column(db.String(50))  # artículo, libro, capítulo, etc.
    indizada = db.Column(db.Boolean, default=False)  # Si está en índices como JCR, Scopus
    
    # IDs de APIs externas
    scopus_id = db.Column(db.String(100))
    pubmed_id = db.Column(db.String(100))
    scholar_id = db.Column(db.String(100))
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Publicacion {self.titulo[:50]}>'

