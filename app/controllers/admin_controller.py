from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.usuario import Usuario
from app.models.publicacion import Publicacion
from app.models.evento import Evento
from app.models.configuracion import Configuracion
from app.utils.decorators import admin_required
from app.forms.usuario_forms import UsuarioForm

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_profesores = Usuario.query.filter_by(rol='profesor').count()
    total_publicaciones = Publicacion.query.count()
    total_eventos = Evento.query.count()
    profesores_activos = Usuario.query.filter_by(rol='profesor', activo=True).count()
    
    return render_template('admin/dashboard.html',
                         total_profesores=total_profesores,
                         total_publicaciones=total_publicaciones,
                         total_eventos=total_eventos,
                         profesores_activos=profesores_activos)

@admin_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    usuarios_list = Usuario.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios_list)

@admin_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_usuario():
    form = UsuarioForm()
    if form.validate_on_submit():
        if Usuario.query.filter_by(email=form.email.data).first():
            flash('Este email ya está registrado', 'danger')
            return render_template('admin/nuevo_usuario.html', form=form)
        
        usuario = Usuario(
            email=form.email.data,
            nombre=form.nombre.data,
            apellidos=form.apellidos.data,
            rol=form.rol.data
        )
        usuario.set_password(form.password.data)
        db.session.add(usuario)
        db.session.commit()
        
        flash('Usuario creado exitosamente', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/nuevo_usuario.html', form=form)

@admin_bp.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    form = UsuarioForm(obj=usuario)
    
    if form.validate_on_submit():
        if form.email.data != usuario.email and Usuario.query.filter_by(email=form.email.data).first():
            flash('Este email ya está registrado', 'danger')
            return render_template('admin/editar_usuario.html', form=form, usuario=usuario)
        
        usuario.email = form.email.data
        usuario.nombre = form.nombre.data
        usuario.apellidos = form.apellidos.data
        usuario.rol = form.rol.data
        usuario.activo = form.activo.data
        
        if form.password.data:
            usuario.set_password(form.password.data)
        
        db.session.commit()
        flash('Usuario actualizado exitosamente', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/editar_usuario.html', form=form, usuario=usuario)

@admin_bp.route('/usuarios/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    if usuario.id == current_user.id:
        flash('No puedes eliminar tu propia cuenta', 'danger')
        return redirect(url_for('admin.usuarios'))
    
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado exitosamente', 'success')
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/configuracion', methods=['GET', 'POST'])
@login_required
@admin_required
def configuracion():
    if request.method == 'POST':
        current_app.config['GOOGLE_SCHOLAR_API'] = request.form.get('google_scholar_api', '')
        current_app.config['SCOPUS_API_KEY'] = request.form.get('scopus_api_key', '')
        current_app.config['ORCID_CLIENT_ID'] = request.form.get('orcid_client_id', '')
        current_app.config['PUBMED_API_KEY'] = request.form.get('pubmed_api_key', '')
        
        Configuracion.establecer('GOOGLE_SCHOLAR_API', request.form.get('google_scholar_api', ''))
        Configuracion.establecer('SCOPUS_API_KEY', request.form.get('scopus_api_key', ''))
        Configuracion.establecer('ORCID_CLIENT_ID', request.form.get('orcid_client_id', ''))
        Configuracion.establecer('PUBMED_API_KEY', request.form.get('pubmed_api_key', ''))
        
        flash('Configuración guardada exitosamente', 'success')
        return redirect(url_for('admin.configuracion'))
    
    config = {
        'google_scholar_api': Configuracion.obtener('GOOGLE_SCHOLAR_API') or current_app.config.get('GOOGLE_SCHOLAR_API', ''),
        'scopus_api_key': Configuracion.obtener('SCOPUS_API_KEY') or current_app.config.get('SCOPUS_API_KEY', ''),
        'orcid_client_id': Configuracion.obtener('ORCID_CLIENT_ID') or current_app.config.get('ORCID_CLIENT_ID', ''),
        'pubmed_api_key': Configuracion.obtener('PUBMED_API_KEY') or current_app.config.get('PUBMED_API_KEY', '')
    }
    
    return render_template('admin/configuracion.html', config=config)

@admin_bp.route('/reportes')
@login_required
@admin_required
def reportes():
    from app.services.reporte_service import ReporteService
    reporte_service = ReporteService()
    estadisticas = reporte_service.obtener_estadisticas_generales()
    return render_template('admin/reportes.html', estadisticas=estadisticas)

