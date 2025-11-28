from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.docente import Docente
from app.models.formacion_academica import FormacionAcademica
from app.models.empleo import Empleo
from app.models.articulo import Articulo
from app.forms.docente_forms import DocenteForm
from app.forms.formacion_forms import FormacionAcademicaForm
from app.forms.empleo_forms import EmpleoForm
from app.forms.articulo_forms import ArticuloForm
from app.utils.decorators import docente_required

docente_bp = Blueprint('docente', __name__)

@docente_bp.route('/dashboard')
@login_required
@docente_required
def dashboard():
    """Dashboard del docente"""
    from app.models.curso_impartido import CursoImpartido
    from app.models.proyecto_investigacion import ProyectoInvestigacion
    from app.models.desarrollo_tecnologico import DesarrolloTecnologico
    
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    
    if not docente:
        flash('Por favor completa tu perfil primero', 'info')
        return redirect(url_for('docente.perfil'))
    
    # Estadísticas
    total_formaciones = FormacionAcademica.query.filter_by(docente_id=docente.id).count()
    total_empleos = Empleo.query.filter_by(docente_id=docente.id).count()
    total_articulos = Articulo.query.filter_by(docente_id=docente.id).count()
    total_cursos = CursoImpartido.query.filter_by(docente_id=docente.id).count()
    total_proyectos = ProyectoInvestigacion.query.filter_by(docente_id=docente.id).count()
    total_desarrollos = DesarrolloTecnologico.query.filter_by(docente_id=docente.id).count()
    
    # Actividades recientes
    actividades_recientes = []
    if total_articulos > 0:
        ultimo_articulo = Articulo.query.filter_by(docente_id=docente.id).order_by(Articulo.id.desc()).first()
        if ultimo_articulo:
            actividades_recientes.append({
                'titulo': 'Artículo publicado',
                'fecha': 'Hace 2 días',
                'color': '#0d6efd'
            })
    
    if total_proyectos > 0:
        ultimo_proyecto = ProyectoInvestigacion.query.filter_by(docente_id=docente.id).order_by(ProyectoInvestigacion.id.desc()).first()
        if ultimo_proyecto:
            actividades_recientes.append({
                'titulo': 'Proyecto actualizado',
                'fecha': 'Hace 5 días',
                'color': '#198754'
            })
    
    return render_template('docente/dashboard.html',
                         docente=docente,
                         total_formaciones=total_formaciones,
                         total_empleos=total_empleos,
                         total_articulos=total_articulos,
                         total_cursos=total_cursos,
                         total_proyectos=total_proyectos,
                         total_desarrollos=total_desarrollos,
                         actividades_recientes=actividades_recientes)

@docente_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
@docente_required
def perfil():
    """Gestionar perfil del docente"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    form = DocenteForm(obj=docente) if docente else DocenteForm()
    
    if form.validate_on_submit():
        if not docente:
            docente = Docente(user_id=current_user.id)
            db.session.add(docente)
        
        form.populate_obj(docente)
        db.session.commit()
        flash('Perfil actualizado exitosamente', 'success')
        return redirect(url_for('docente.perfil'))
    
    return render_template('docente/perfil.html', form=form, docente=docente)

@docente_bp.route('/formacion', methods=['GET', 'POST'])
@login_required
@docente_required
def formacion():
    """Listar y crear formación académica"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    if not docente:
        flash('Por favor completa tu perfil primero', 'warning')
        return redirect(url_for('docente.perfil'))
    
    formaciones = FormacionAcademica.query.filter_by(docente_id=docente.id).all()
    return render_template('docente/formacion.html', formaciones=formaciones)

@docente_bp.route('/formacion/nueva', methods=['GET', 'POST'])
@login_required
@docente_required
def nueva_formacion():
    """Crear nueva formación académica"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    if not docente:
        flash('Por favor completa tu perfil primero', 'warning')
        return redirect(url_for('docente.perfil'))
    
    form = FormacionAcademicaForm()
    if form.validate_on_submit():
        formacion = FormacionAcademica(docente_id=docente.id)
        form.populate_obj(formacion)
        db.session.add(formacion)
        db.session.commit()
        flash('Formación académica agregada exitosamente', 'success')
        return redirect(url_for('docente.formacion'))
    
    return render_template('docente/nueva_formacion.html', form=form)

@docente_bp.route('/formacion/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@docente_required
def editar_formacion(id):
    """Editar formación académica"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    formacion = FormacionAcademica.query.get_or_404(id)
    
    if formacion.docente_id != docente.id:
        flash('No tienes permisos para editar esto', 'danger')
        return redirect(url_for('docente.formacion'))
    
    form = FormacionAcademicaForm(obj=formacion)
    if form.validate_on_submit():
        form.populate_obj(formacion)
        db.session.commit()
        flash('Formación académica actualizada exitosamente', 'success')
        return redirect(url_for('docente.formacion'))
    
    return render_template('docente/editar_formacion.html', form=form, formacion=formacion)

@docente_bp.route('/formacion/<int:id>/eliminar', methods=['POST'])
@login_required
@docente_required
def eliminar_formacion(id):
    """Eliminar formación académica"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    formacion = FormacionAcademica.query.get_or_404(id)
    
    if formacion.docente_id != docente.id:
        flash('No tienes permisos para eliminar esto', 'danger')
        return redirect(url_for('docente.formacion'))
    
    db.session.delete(formacion)
    db.session.commit()
    flash('Formación académica eliminada exitosamente', 'success')
    return redirect(url_for('docente.formacion'))

@docente_bp.route('/empleos')
@login_required
@docente_required
def empleos():
    """Listar empleos"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    if not docente:
        flash('Por favor completa tu perfil primero', 'warning')
        return redirect(url_for('docente.perfil'))
    
    empleos_list = Empleo.query.filter_by(docente_id=docente.id).all()
    return render_template('docente/empleos.html', empleos=empleos_list)

@docente_bp.route('/empleos/nuevo', methods=['GET', 'POST'])
@login_required
@docente_required
def nuevo_empleo():
    """Crear nuevo empleo"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    if not docente:
        flash('Por favor completa tu perfil primero', 'warning')
        return redirect(url_for('docente.perfil'))
    
    form = EmpleoForm()
    if form.validate_on_submit():
        empleo = Empleo(docente_id=docente.id)
        form.populate_obj(empleo)
        db.session.add(empleo)
        db.session.commit()
        flash('Empleo agregado exitosamente', 'success')
        return redirect(url_for('docente.empleos'))
    
    return render_template('docente/nuevo_empleo.html', form=form)

@docente_bp.route('/empleos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@docente_required
def editar_empleo(id):
    """Editar empleo"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    empleo = Empleo.query.get_or_404(id)
    
    if empleo.docente_id != docente.id:
        flash('No tienes permisos para editar esto', 'danger')
        return redirect(url_for('docente.empleos'))
    
    form = EmpleoForm(obj=empleo)
    if form.validate_on_submit():
        form.populate_obj(empleo)
        db.session.commit()
        flash('Empleo actualizado exitosamente', 'success')
        return redirect(url_for('docente.empleos'))
    
    return render_template('docente/editar_empleo.html', form=form, empleo=empleo)

@docente_bp.route('/empleos/<int:id>/eliminar', methods=['POST'])
@login_required
@docente_required
def eliminar_empleo(id):
    """Eliminar empleo"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    empleo = Empleo.query.get_or_404(id)
    
    if empleo.docente_id != docente.id:
        flash('No tienes permisos para eliminar esto', 'danger')
        return redirect(url_for('docente.empleos'))
    
    db.session.delete(empleo)
    db.session.commit()
    flash('Empleo eliminado exitosamente', 'success')
    return redirect(url_for('docente.empleos'))

@docente_bp.route('/articulos')
@login_required
@docente_required
def articulos():
    """Listar artículos"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    if not docente:
        flash('Por favor completa tu perfil primero', 'warning')
        return redirect(url_for('docente.perfil'))
    
    articulos_list = Articulo.query.filter_by(docente_id=docente.id).all()
    return render_template('docente/articulos.html', articulos=articulos_list)

@docente_bp.route('/articulos/nuevo', methods=['GET', 'POST'])
@login_required
@docente_required
def nuevo_articulo():
    """Crear nuevo artículo"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    if not docente:
        flash('Por favor completa tu perfil primero', 'warning')
        return redirect(url_for('docente.perfil'))
    
    form = ArticuloForm()
    if form.validate_on_submit():
        articulo = Articulo(docente_id=docente.id)
        form.populate_obj(articulo)
        db.session.add(articulo)
        db.session.commit()
        flash('Artículo agregado exitosamente', 'success')
        return redirect(url_for('docente.articulos'))
    
    return render_template('docente/nuevo_articulo.html', form=form)

@docente_bp.route('/articulos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@docente_required
def editar_articulo(id):
    """Editar artículo"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    articulo = Articulo.query.get_or_404(id)
    
    if articulo.docente_id != docente.id:
        flash('No tienes permisos para editar esto', 'danger')
        return redirect(url_for('docente.articulos'))
    
    form = ArticuloForm(obj=articulo)
    if form.validate_on_submit():
        form.populate_obj(articulo)
        db.session.commit()
        flash('Artículo actualizado exitosamente', 'success')
        return redirect(url_for('docente.articulos'))
    
    return render_template('docente/editar_articulo.html', form=form, articulo=articulo)

@docente_bp.route('/articulos/<int:id>/eliminar', methods=['POST'])
@login_required
@docente_required
def eliminar_articulo(id):
    """Eliminar artículo"""
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    articulo = Articulo.query.get_or_404(id)
    
    if articulo.docente_id != docente.id:
        flash('No tienes permisos para eliminar esto', 'danger')
        return redirect(url_for('docente.articulos'))
    
    db.session.delete(articulo)
    db.session.commit()
    flash('Artículo eliminado exitosamente', 'success')
    return redirect(url_for('docente.articulos'))

