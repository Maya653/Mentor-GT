from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.usuario import Usuario
from app.models.publicacion import Publicacion
from app.services.sync_service import SyncService
from app.utils.decorators import profesor_required, admin_required

sync_bp = Blueprint('sync', __name__)

@sync_bp.route('/')
@login_required
@profesor_required
def index():
    return render_template('profesor/sync.html')

@sync_bp.route('/google-scholar', methods=['POST'])
@login_required
@profesor_required
def sync_google_scholar():
    sync_service = SyncService()
    try:
        resultado = sync_service.sincronizar_google_scholar(current_user.id)
        flash(f'Sincronización exitosa: {resultado["publicaciones_agregadas"]} publicaciones agregadas', 'success')
    except Exception as e:
        flash(f'Error en sincronización: {str(e)}', 'danger')
    
    return redirect(url_for('sync.index'))

@sync_bp.route('/scopus', methods=['POST'])
@login_required
@profesor_required
def sync_scopus():
    sync_service = SyncService()
    try:
        resultado = sync_service.sincronizar_scopus(current_user.id)
        flash(f'Sincronización exitosa: {resultado["publicaciones_agregadas"]} publicaciones agregadas', 'success')
    except Exception as e:
        flash(f'Error en sincronización: {str(e)}', 'danger')
    
    return redirect(url_for('sync.index'))

@sync_bp.route('/orcid', methods=['POST'])
@login_required
@profesor_required
def sync_orcid():
    sync_service = SyncService()
    try:
        resultado = sync_service.sincronizar_orcid(current_user.id)
        flash(f'Sincronización exitosa: {resultado["publicaciones_agregadas"]} publicaciones agregadas', 'success')
    except Exception as e:
        flash(f'Error en sincronización: {str(e)}', 'danger')
    
    return redirect(url_for('sync.index'))

@sync_bp.route('/pubmed', methods=['POST'])
@login_required
@profesor_required
def sync_pubmed():
    sync_service = SyncService()
    try:
        resultado = sync_service.sincronizar_pubmed(current_user.id)
        flash(f'Sincronización exitosa: {resultado["publicaciones_agregadas"]} publicaciones agregadas', 'success')
    except Exception as e:
        flash(f'Error en sincronización: {str(e)}', 'danger')
    
    return redirect(url_for('sync.index'))

@sync_bp.route('/masiva', methods=['POST'])
@login_required
@admin_required
def sync_masiva():
    sync_service = SyncService()
    try:
        resultado = sync_service.sincronizacion_masiva()
        flash(f'Sincronización masiva completada: {resultado["usuarios_procesados"]} usuarios procesados', 'success')
    except Exception as e:
        flash(f'Error en sincronización masiva: {str(e)}', 'danger')
    
    return redirect(url_for('admin.dashboard'))

