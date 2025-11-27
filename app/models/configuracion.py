from app import db
from datetime import datetime

class Configuracion(db.Model):
    __tablename__ = 'configuraciones'
    
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(100), unique=True, nullable=False, index=True)
    valor = db.Column(db.Text)
    descripcion = db.Column(db.String(500))
    tipo = db.Column(db.String(50))  # string, int, bool, json
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def obtener(clave, default=None):
        config = Configuracion.query.filter_by(clave=clave).first()
        if config:
            if config.tipo == 'int':
                return int(config.valor) if config.valor else default
            elif config.tipo == 'bool':
                return config.valor.lower() == 'true'
            elif config.tipo == 'json':
                import json
                return json.loads(config.valor) if config.valor else default
            return config.valor
        return default
    
    @staticmethod
    def establecer(clave, valor, descripcion=None, tipo='string'):
        config = Configuracion.query.filter_by(clave=clave).first()
        if config:
            config.valor = str(valor)
            config.descripcion = descripcion or config.descripcion
            config.tipo = tipo
        else:
            config = Configuracion(
                clave=clave,
                valor=str(valor),
                descripcion=descripcion,
                tipo=tipo
            )
            db.session.add(config)
        db.session.commit()
        return config
    
    def __repr__(self):
        return f'<Configuracion {self.clave}>'

