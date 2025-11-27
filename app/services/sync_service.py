from app import db
from app.models.usuario import Usuario
from app.models.publicacion import Publicacion
from app.services.api_externa_service import APIExternaService
from datetime import datetime

class SyncService:
    """Servicio para sincronizar datos con APIs externas"""
    
    def __init__(self):
        self.api_service = APIExternaService()
    
    def sincronizar_google_scholar(self, usuario_id):
        """Sincroniza publicaciones de Google Scholar"""
        usuario = Usuario.query.get(usuario_id)
        if not usuario or not usuario.google_scholar_id:
            raise ValueError("Usuario no tiene Google Scholar ID configurado")
        
        publicaciones_api = self.api_service.obtener_publicaciones_google_scholar(usuario.google_scholar_id)
        publicaciones_agregadas = 0
        
        for pub_data in publicaciones_api:
            # Verificar si ya existe
            if pub_data.get('doi'):
                existe = Publicacion.query.filter_by(doi=pub_data['doi'], usuario_id=usuario_id).first()
            else:
                existe = Publicacion.query.filter_by(
                    titulo=pub_data.get('titulo', ''),
                    usuario_id=usuario_id
                ).first()
            
            if not existe:
                publicacion = Publicacion(
                    usuario_id=usuario_id,
                    titulo=pub_data.get('titulo', ''),
                    autores=pub_data.get('autores', ''),
                    revista=pub_data.get('revista', ''),
                    año=pub_data.get('año'),
                    doi=pub_data.get('doi', ''),
                    tipo=pub_data.get('tipo', 'articulo'),
                    scholar_id=pub_data.get('id', '')
                )
                db.session.add(publicacion)
                publicaciones_agregadas += 1
        
        db.session.commit()
        return {'publicaciones_agregadas': publicaciones_agregadas}
    
    def sincronizar_scopus(self, usuario_id):
        """Sincroniza publicaciones de Scopus"""
        usuario = Usuario.query.get(usuario_id)
        if not usuario or not usuario.scopus_id:
            raise ValueError("Usuario no tiene Scopus ID configurado")
        
        publicaciones_api = self.api_service.obtener_publicaciones_scopus(usuario.scopus_id)
        publicaciones_agregadas = 0
        
        for pub_data in publicaciones_api:
            if pub_data.get('doi'):
                existe = Publicacion.query.filter_by(doi=pub_data['doi'], usuario_id=usuario_id).first()
            else:
                existe = Publicacion.query.filter_by(
                    titulo=pub_data.get('titulo', ''),
                    usuario_id=usuario_id
                ).first()
            
            if not existe:
                publicacion = Publicacion(
                    usuario_id=usuario_id,
                    titulo=pub_data.get('titulo', ''),
                    autores=pub_data.get('autores', ''),
                    revista=pub_data.get('revista', ''),
                    año=pub_data.get('año'),
                    doi=pub_data.get('doi', ''),
                    tipo=pub_data.get('tipo', 'articulo'),
                    scopus_id=pub_data.get('id', ''),
                    indizada=True
                )
                db.session.add(publicacion)
                publicaciones_agregadas += 1
        
        db.session.commit()
        return {'publicaciones_agregadas': publicaciones_agregadas}
    
    def sincronizar_orcid(self, usuario_id):
        """Sincroniza publicaciones de ORCID"""
        usuario = Usuario.query.get(usuario_id)
        if not usuario or not usuario.orcid_id:
            raise ValueError("Usuario no tiene ORCID ID configurado")
        
        publicaciones_api = self.api_service.obtener_publicaciones_orcid(usuario.orcid_id)
        publicaciones_agregadas = 0
        
        for pub_data in publicaciones_api:
            if pub_data.get('doi'):
                existe = Publicacion.query.filter_by(doi=pub_data['doi'], usuario_id=usuario_id).first()
            else:
                existe = Publicacion.query.filter_by(
                    titulo=pub_data.get('titulo', ''),
                    usuario_id=usuario_id
                ).first()
            
            if not existe:
                publicacion = Publicacion(
                    usuario_id=usuario_id,
                    titulo=pub_data.get('titulo', ''),
                    año=pub_data.get('año'),
                    doi=pub_data.get('doi', ''),
                    tipo=pub_data.get('tipo', 'articulo')
                )
                db.session.add(publicacion)
                publicaciones_agregadas += 1
        
        db.session.commit()
        return {'publicaciones_agregadas': publicaciones_agregadas}
    
    def sincronizar_pubmed(self, usuario_id):
        """Sincroniza publicaciones de PubMed"""
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")
        
        # Construir query de búsqueda
        query = f"{usuario.nombre} {usuario.apellidos or ''}"
        publicaciones_api = self.api_service.obtener_publicaciones_pubmed(query)
        publicaciones_agregadas = 0
        
        for pub_data in publicaciones_api:
            if pub_data.get('doi'):
                existe = Publicacion.query.filter_by(doi=pub_data['doi'], usuario_id=usuario_id).first()
            else:
                existe = Publicacion.query.filter_by(
                    titulo=pub_data.get('titulo', ''),
                    usuario_id=usuario_id
                ).first()
            
            if not existe:
                publicacion = Publicacion(
                    usuario_id=usuario_id,
                    titulo=pub_data.get('titulo', ''),
                    autores=pub_data.get('autores', ''),
                    revista=pub_data.get('revista', ''),
                    año=pub_data.get('año'),
                    doi=pub_data.get('doi', ''),
                    tipo='articulo',
                    pubmed_id=pub_data.get('id', '')
                )
                db.session.add(publicacion)
                publicaciones_agregadas += 1
        
        db.session.commit()
        return {'publicaciones_agregadas': publicaciones_agregadas}
    
    def sincronizacion_masiva(self):
        """Sincroniza publicaciones para todos los usuarios"""
        usuarios = Usuario.query.filter_by(rol='profesor', activo=True).all()
        usuarios_procesados = 0
        
        for usuario in usuarios:
            try:
                if usuario.google_scholar_id:
                    self.sincronizar_google_scholar(usuario.id)
                if usuario.scopus_id:
                    self.sincronizar_scopus(usuario.id)
                if usuario.orcid_id:
                    self.sincronizar_orcid(usuario.id)
                usuarios_procesados += 1
            except Exception as e:
                print(f"Error sincronizando usuario {usuario.id}: {e}")
                continue
        
        return {'usuarios_procesados': usuarios_procesados}

