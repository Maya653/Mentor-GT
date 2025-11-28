from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.docente import Docente
from app.models.articulo import Articulo
from app.services.api_externa_service import APIExternaService
from app.utils.decorators import profesor_required, admin_required

sync_bp = Blueprint('sync', __name__)

@sync_bp.route('/')
@login_required
@profesor_required
def index():
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    return render_template('docente/sync.html', docente=docente)

@sync_bp.route('/orcid', methods=['POST'])
@login_required
@profesor_required
def sync_orcid():
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    
    if not docente:
        flash('Por favor completa tu perfil primero', 'warning')
        return redirect(url_for('docente.perfil'))
    
    if not docente.orcid:
        flash('Por favor agrega tu ORCID en tu perfil primero', 'warning')
        return redirect(url_for('docente.perfil'))
    
    try:
        api_service = APIExternaService()
        publicaciones = api_service.obtener_publicaciones_orcid(docente.orcid)
        
        agregadas = 0
        for pub in publicaciones:
            doi = pub.get('doi', '').strip() if pub.get('doi') else None
            titulo = pub.get('titulo', 'Sin título')
            
            # Verificar si ya existe (por DOI o título)
            if doi:
                existente = Articulo.query.filter_by(doi=doi).first()
                if existente:
                    continue
            else:
                # Si no hay DOI, verificar por título
                existente = Articulo.query.filter_by(
                    docente_id=docente.id, 
                    titulo=titulo
                ).first()
                if existente:
                    continue
            
            # Crear nuevo artículo (DOI None si está vacío)
            articulo = Articulo(
                docente_id=docente.id,
                titulo=titulo,
                revista=pub.get('revista'),
                anio=pub.get('año'),
                doi=doi if doi else None,
                autores=pub.get('autores'),
                estado='Publicado'
            )
            db.session.add(articulo)
            agregadas += 1
        
        db.session.commit()
        flash(f'Sincronización exitosa: {agregadas} publicaciones importadas desde ORCID', 'success')
        
    except Exception as e:
        flash(f'Error en sincronización: {str(e)}', 'danger')
    
    return redirect(url_for('sync.index'))
