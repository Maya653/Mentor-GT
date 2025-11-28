from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.docente import Docente
from app.models.articulo import Articulo
from app.services.api_externa_service import APIExternaService
from app.utils.decorators import docente_required

sync_bp = Blueprint('sync', __name__)


def _agregar_publicaciones(docente, publicaciones, fuente):
    """Helper para agregar publicaciones evitando duplicados"""
    agregadas = 0
    duplicadas = 0
    
    for pub in publicaciones:
        doi = pub.get('doi', '').strip() if pub.get('doi') else None
        titulo = pub.get('titulo', 'Sin título')
        
        # Verificar si ya existe
        if doi:
            existente = Articulo.query.filter_by(doi=doi).first()
            if existente:
                print(f"⚠️ Duplicado por DOI: {doi[:50]}... (fuente original: {existente.indexacion})")
                duplicadas += 1
                continue
        else:
            existente = Articulo.query.filter_by(
                docente_id=docente.id, 
                titulo=titulo
            ).first()
            if existente:
                print(f"⚠️ Duplicado por título: {titulo[:50]}...")
                duplicadas += 1
                continue
        
        print(f"✅ Nueva: {titulo[:50]}... (DOI: {doi})")
        
        # Crear nuevo artículo
        articulo = Articulo(
            docente_id=docente.id,
            titulo=titulo,
            revista=pub.get('revista', ''),
            anio=pub.get('año'),
            doi=doi if doi else None,
            autores=pub.get('autores', ''),
            estado='Publicado',
            indexacion=fuente
        )
        db.session.add(articulo)
        agregadas += 1
    
    return agregadas, duplicadas


@sync_bp.route('/')
@login_required
@docente_required
def index():
    """Página principal de sincronización"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    return render_template('docente/sync.html', docente=docente)


@sync_bp.route('/orcid', methods=['POST'])
@login_required
@docente_required
def sync_orcid():
    """Sincronizar publicaciones desde ORCID"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    
    if not docente:
        flash('Por favor completa tu perfil primero', 'warning')
        return redirect(url_for('docente.perfil'))
    
    if not docente.orcid:
        flash('No tienes configurado tu ORCID ID. Agrégalo en tu perfil.', 'warning')
        return redirect(url_for('docente.perfil'))
    
    try:
        api_service = APIExternaService(docente)
        publicaciones = api_service.obtener_publicaciones_orcid()
        
        if not publicaciones:
            flash('No se encontraron publicaciones en ORCID', 'info')
            return redirect(url_for('sync.index'))
        
        agregadas, duplicadas = _agregar_publicaciones(docente, publicaciones, 'ORCID')
        db.session.commit()
        
        if agregadas > 0:
            flash(f'✅ ORCID: {agregadas} nuevas publicaciones importadas', 'success')
        if duplicadas > 0:
            flash(f'ℹ️ {duplicadas} publicaciones ya existían (no duplicadas)', 'info')
        
    except Exception as e:
        flash(f'❌ {str(e)}', 'danger')
    
    return redirect(url_for('sync.index'))


@sync_bp.route('/scopus', methods=['POST'])
@login_required
@docente_required
def sync_scopus():
    """Sincronizar publicaciones desde Scopus"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    
    if not docente:
        flash('Por favor completa tu perfil primero', 'warning')
        return redirect(url_for('docente.perfil'))
    
    if not docente.scopus_author_id:
        flash('No tienes configurado tu Scopus Author ID. Agrégalo en tu perfil.', 'warning')
        return redirect(url_for('docente.perfil'))
    
    try:
        api_service = APIExternaService(docente)
        publicaciones = api_service.obtener_publicaciones_scopus()
        
        if not publicaciones:
            flash('No se encontraron publicaciones en Scopus', 'info')
            return redirect(url_for('sync.index'))
        
        agregadas, duplicadas = _agregar_publicaciones(docente, publicaciones, 'Scopus')
        db.session.commit()
        
        if agregadas > 0:
            flash(f'✅ Scopus: {agregadas} nuevas publicaciones importadas', 'success')
        if duplicadas > 0:
            flash(f'ℹ️ {duplicadas} publicaciones ya existían (no duplicadas)', 'info')
        
    except Exception as e:
        flash(f'❌ {str(e)}', 'danger')
    
    return redirect(url_for('sync.index'))


@sync_bp.route('/pubmed', methods=['POST'])
@login_required
@docente_required
def sync_pubmed():
    """Sincronizar publicaciones desde PubMed"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    
    if not docente:
        flash('Por favor completa tu perfil primero', 'warning')
        return redirect(url_for('docente.perfil'))
    
    if not docente.pubmed_query:
        flash('No tienes configurada tu búsqueda de PubMed. Agrégala en tu perfil.', 'warning')
        return redirect(url_for('docente.perfil'))
    
    try:
        api_service = APIExternaService(docente)
        publicaciones = api_service.obtener_publicaciones_pubmed()
        
        if not publicaciones:
            flash('No se encontraron publicaciones en PubMed', 'info')
            return redirect(url_for('sync.index'))
        
        agregadas, duplicadas = _agregar_publicaciones(docente, publicaciones, 'PubMed')
        db.session.commit()
        
        if agregadas > 0:
            flash(f'✅ PubMed: {agregadas} nuevas publicaciones importadas', 'success')
        if duplicadas > 0:
            flash(f'ℹ️ {duplicadas} publicaciones ya existían (no duplicadas)', 'info')
        
    except Exception as e:
        flash(f'❌ {str(e)}', 'danger')
    
    return redirect(url_for('sync.index'))


@sync_bp.route('/todas', methods=['POST'])
@login_required
@docente_required
def sync_todas():
    """Sincronizar publicaciones desde todas las fuentes configuradas"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    
    if not docente:
        flash('Por favor completa tu perfil primero', 'warning')
        return redirect(url_for('docente.perfil'))
    
    # Verificar si tiene algún ID configurado
    if not docente.orcid and not docente.scopus_author_id and not docente.pubmed_query:
        flash('No tienes ningún ID configurado. Agrégalos en tu perfil.', 'warning')
        return redirect(url_for('docente.perfil'))
    
    try:
        api_service = APIExternaService(docente)
        resultados = api_service.obtener_todas_publicaciones()
        
        total_agregadas = 0
        total_duplicadas = 0
        mensajes = []
        
        # ORCID
        if resultados['orcid']:
            agregadas, duplicadas = _agregar_publicaciones(docente, resultados['orcid'], 'ORCID')
            total_agregadas += agregadas
            total_duplicadas += duplicadas
            if agregadas > 0:
                mensajes.append(f"ORCID: {agregadas}")
        
        # Scopus
        if resultados['scopus']:
            agregadas, duplicadas = _agregar_publicaciones(docente, resultados['scopus'], 'Scopus')
            total_agregadas += agregadas
            total_duplicadas += duplicadas
            if agregadas > 0:
                mensajes.append(f"Scopus: {agregadas}")
        
        # PubMed
        if resultados['pubmed']:
            agregadas, duplicadas = _agregar_publicaciones(docente, resultados['pubmed'], 'PubMed')
            total_agregadas += agregadas
            total_duplicadas += duplicadas
            if agregadas > 0:
                mensajes.append(f"PubMed: {agregadas}")
        
        db.session.commit()
        
        if total_agregadas > 0:
            flash(f'✅ {total_agregadas} nuevas publicaciones importadas ({", ".join(mensajes)})', 'success')
        
        if total_duplicadas > 0:
            flash(f'ℹ️ {total_duplicadas} publicaciones ya existían (no duplicadas)', 'info')
        
        for error in resultados.get('errores', []):
            flash(f'⚠️ {error}', 'warning')
        
    except Exception as e:
        flash(f'❌ Error: {str(e)}', 'danger')
    
    return redirect(url_for('sync.index'))
