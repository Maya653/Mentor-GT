from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.usuario import Usuario
from app.models.publicacion import Publicacion
from app.models.evento import Evento
from app.models.docencia import Docencia
from app.utils.decorators import profesor_required

profesor_bp = Blueprint('profesor', __name__)

@profesor_bp.route('/dashboard')
@login_required
@profesor_required
def dashboard():
    total_publicaciones = Publicacion.query.filter_by(usuario_id=current_user.id).count()
    total_eventos = Evento.query.filter_by(usuario_id=current_user.id).count()
    total_docencias = Docencia.query.filter_by(usuario_id=current_user.id).count()
    
    publicaciones_recientes = Publicacion.query.filter_by(usuario_id=current_user.id)\
        .order_by(Publicacion.fecha_creacion.desc()).limit(5).all()
    
    return render_template('profesor/dashboard.html',
                         total_publicaciones=total_publicaciones,
                         total_eventos=total_eventos,
                         total_docencias=total_docencias,
                         publicaciones_recientes=publicaciones_recientes)

@profesor_bp.route('/datos-personales', methods=['GET', 'POST'])
@login_required
@profesor_required
def datos_personales():
    if request.method == 'POST':
        current_user.nombre = request.form.get('nombre', current_user.nombre)
        current_user.apellidos = request.form.get('apellidos', current_user.apellidos)
        current_user.google_scholar_id = request.form.get('google_scholar_id', '')
        current_user.scopus_id = request.form.get('scopus_id', '')
        current_user.orcid_id = request.form.get('orcid_id', '')
        
        db.session.commit()
        flash('Datos personales actualizados exitosamente', 'success')
        return redirect(url_for('profesor.datos_personales'))
    
    return render_template('profesor/datos_personales.html')

@profesor_bp.route('/publicaciones')
@login_required
@profesor_required
def publicaciones():
    publicaciones_list = Publicacion.query.filter_by(usuario_id=current_user.id)\
        .order_by(Publicacion.año.desc(), Publicacion.fecha_creacion.desc()).all()
    return render_template('profesor/publicaciones.html', publicaciones=publicaciones_list)

@profesor_bp.route('/eventos')
@login_required
@profesor_required
def eventos():
    eventos_list = Evento.query.filter_by(usuario_id=current_user.id)\
        .order_by(Evento.fecha_inicio.desc()).all()
    return render_template('profesor/eventos.html', eventos=eventos_list)

@profesor_bp.route('/docencia')
@login_required
@profesor_required
def docencia():
    docencias_list = Docencia.query.filter_by(usuario_id=current_user.id)\
        .order_by(Docencia.año.desc(), Docencia.periodo.desc()).all()
    return render_template('profesor/docencia.html', docencias=docencias_list)

@profesor_bp.route('/generar-cv')
@login_required
@profesor_required
def generar_cv():
    return render_template('profesor/generar_cv.html')

