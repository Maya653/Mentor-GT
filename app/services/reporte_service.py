from app.models.usuario import Usuario
from app.models.publicacion import Publicacion
from app.models.evento import Evento
from app.models.docencia import Docencia
from datetime import datetime

class ReporteService:
    """Servicio para generar reportes y estadísticas"""
    
    def obtener_estadisticas_generales(self):
        """Obtiene estadísticas generales del sistema"""
        total_usuarios = Usuario.query.count()
        total_profesores = Usuario.query.filter_by(rol='profesor').count()
        total_admins = Usuario.query.filter_by(rol='admin').count()
        usuarios_activos = Usuario.query.filter_by(activo=True).count()
        
        total_publicaciones = Publicacion.query.count()
        publicaciones_indizadas = Publicacion.query.filter_by(indizada=True).count()
        
        total_eventos = Evento.query.count()
        total_docencias = Docencia.query.count()
        
        # Estadísticas por año
        publicaciones_por_año = {}
        publicaciones = Publicacion.query.filter(Publicacion.año.isnot(None)).all()
        for pub in publicaciones:
            año = pub.año
            if año:
                publicaciones_por_año[año] = publicaciones_por_año.get(año, 0) + 1
        
        return {
            'total_usuarios': total_usuarios,
            'total_profesores': total_profesores,
            'total_admins': total_admins,
            'usuarios_activos': usuarios_activos,
            'total_publicaciones': total_publicaciones,
            'publicaciones_indizadas': publicaciones_indizadas,
            'total_eventos': total_eventos,
            'total_docencias': total_docencias,
            'publicaciones_por_año': publicaciones_por_año
        }
    
    def obtener_estadisticas_profesor(self, usuario_id):
        """Obtiene estadísticas de un profesor específico"""
        publicaciones = Publicacion.query.filter_by(usuario_id=usuario_id).count()
        publicaciones_indizadas = Publicacion.query.filter_by(usuario_id=usuario_id, indizada=True).count()
        eventos = Evento.query.filter_by(usuario_id=usuario_id).count()
        docencias = Docencia.query.filter_by(usuario_id=usuario_id).count()
        
        return {
            'total_publicaciones': publicaciones,
            'publicaciones_indizadas': publicaciones_indizadas,
            'total_eventos': eventos,
            'total_docencias': docencias
        }

