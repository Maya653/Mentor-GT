from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.docente import Docente
from app.models.articulo import Articulo
from app.models.empleo import Empleo
from app.models.formacion_academica import FormacionAcademica
from app.utils.decorators import admin_required
from app.services.cv_generator_service import CVGeneratorService
import io

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Dashboard del administrador"""
    from app.models.curso_impartido import CursoImpartido
    from app.models.proyecto_investigacion import ProyectoInvestigacion
    
    total_docentes = Docente.query.count()
    total_usuarios = User.query.count()
    total_articulos = Articulo.query.count()
    total_cursos = CursoImpartido.query.count()
    total_proyectos = ProyectoInvestigacion.query.count()
    
    # Docentes recientes (últimos 2)
    docentes_recientes = Docente.query.order_by(Docente.created_at.desc()).limit(2).all()
    
    # Actividades recientes (simuladas por ahora)
    actividades_recientes = []
    if total_articulos > 0:
        ultimo_articulo = Articulo.query.order_by(Articulo.id.desc()).first()
        if ultimo_articulo and ultimo_articulo.docente:
            actividades_recientes.append({
                'titulo': 'Nuevo artículo registrado',
                'docente': ultimo_articulo.docente.nombre_completo,
                'fecha': 'Hace 2 días',
                'color': '#0d6efd'
            })
    
    if total_proyectos > 0:
        ultimo_proyecto = ProyectoInvestigacion.query.order_by(ProyectoInvestigacion.id.desc()).first()
        if ultimo_proyecto and ultimo_proyecto.docente:
            actividades_recientes.append({
                'titulo': 'Proyecto finalizado',
                'docente': ultimo_proyecto.docente.nombre_completo,
                'fecha': 'Hace 5 días',
                'color': '#198754'
            })
    
    return render_template('admin/dashboard.html',
                         total_docentes=total_docentes,
                         total_usuarios=total_usuarios,
                         total_articulos=total_articulos,
                         total_cursos=total_cursos,
                         total_proyectos=total_proyectos,
                         docentes_recientes=docentes_recientes,
                         actividades_recientes=actividades_recientes)

@admin_bp.route('/docentes')
@login_required
@admin_required
def docentes():
    """Listar y buscar docentes"""
    from flask import request
    from sqlalchemy import or_
    
    # Obtener parámetros de búsqueda
    query = request.args.get('q', '').strip()
    area_filter = request.args.get('area', '').strip()
    nivel_filter = request.args.get('nivel', '').strip()
    
    # Consulta base
    docentes_query = Docente.query
    
    # Búsqueda por texto
    if query:
        docentes_query = docentes_query.filter(
            or_(
                Docente.nombre_completo.ilike(f'%{query}%'),
                Docente.cvu.ilike(f'%{query}%'),
                Docente.curp.ilike(f'%{query}%'),
                Docente.rfc.ilike(f'%{query}%'),
                Docente.orcid.ilike(f'%{query}%')
            )
        )
    
    # Filtro por área (basado en empleo actual)
    if area_filter:
        docentes_query = docentes_query.join(Empleo).filter(
            Empleo.actual == True,
            Empleo.area_adscripcion.ilike(f'%{area_filter}%')
        )
    
    # Filtro por nivel (basado en formación académica)
    if nivel_filter:
        docentes_query = docentes_query.join(FormacionAcademica).filter(
            FormacionAcademica.nivel == nivel_filter
        )
    
    # Obtener docentes
    docentes_list = docentes_query.distinct().all()
    
    # Calcular nivel máximo y empleo actual para cada docente
    docentes_con_nivel = []
    for docente in docentes_list:
        nivel_maximo = None
        formaciones = docente.formaciones.all()
        if formaciones:
            # Ordenar por prioridad: doctorado > maestria > licenciatura
            niveles_prioridad = {'doctorado': 3, 'maestria': 2, 'licenciatura': 1, 'especialidad': 1}
            formaciones_ordenadas = sorted(
                formaciones,
                key=lambda f: niveles_prioridad.get(f.nivel, 0),
                reverse=True
            )
            nivel_maximo = formaciones_ordenadas[0].nivel if formaciones_ordenadas else None
        
        # Obtener empleo actual
        empleo_actual = None
        for empleo in docente.empleos:
            if empleo.actual:
                empleo_actual = empleo
                break
        
        docentes_con_nivel.append({
            'docente': docente,
            'nivel_maximo': nivel_maximo,
            'empleo_actual': empleo_actual
        })
    
    # Obtener áreas disponibles para el filtro
    areas_disponibles = db.session.query(Empleo.area_adscripcion).filter(
        Empleo.actual == True,
        Empleo.area_adscripcion.isnot(None)
    ).distinct().all()
    areas_disponibles = [area[0] for area in areas_disponibles if area[0]]
    
    return render_template('admin/docentes.html', 
                         docentes_con_nivel=docentes_con_nivel,
                         areas_disponibles=areas_disponibles)

@admin_bp.route('/docentes/<int:id>')
@login_required
@admin_required
def ver_docente(id):
    """Ver perfil completo de un docente"""
    docente = Docente.query.get_or_404(id)
    
    formaciones = docente.formaciones.all()
    empleos = docente.empleos.all()
    articulos = docente.articulos.all()
    idiomas = docente.idiomas.all()
    cursos = docente.cursos.all()
    proyectos = docente.proyectos.all()
    libros = docente.libros.all()
    congresos = docente.congresos.all()
    tesis = docente.tesis.all()
    desarrollos = docente.desarrollos.all()
    actividades = docente.actividades.all()
    
    return render_template('admin/ver_docente.html',
                         docente=docente,
                         formaciones=formaciones,
                         empleos=empleos,
                         articulos=articulos,
                         idiomas=idiomas,
                         cursos=cursos,
                         proyectos=proyectos,
                         libros=libros,
                         congresos=congresos,
                         tesis=tesis,
                         desarrollos=desarrollos,
                         actividades=actividades)

@admin_bp.route('/docentes/<int:id>/cv', methods=['GET', 'POST'])
@login_required
@admin_required
def docente_cv(id):
    """Generar y visualizar el CV de un docente desde el panel admin"""
    docente = Docente.query.get_or_404(id)
    
    formaciones = FormacionAcademica.query.filter_by(docente_id=docente.id).all()
    empleos = Empleo.query.filter_by(docente_id=docente.id).all()
    articulos = Articulo.query.filter_by(docente_id=docente.id).all()
    libros = docente.libros.all()
    congresos = docente.congresos.all()
    cursos = docente.cursos.all()
    proyectos = docente.proyectos.all()
    tesis = docente.tesis.all()
    desarrollos = docente.desarrollos.all()
    
    selected_sections = request.form.getlist('sections') or CVGeneratorService.DEFAULT_SECTIONS
    formato = request.form.get('formato', 'pdf')
    tipo_cv = request.form.get('tipo_cv', 'academico')
    
    if request.method == 'POST':
        cv_service = CVGeneratorService()
        try:
            if formato == 'pdf':
                pdf_data = cv_service.generar_pdf(
                    docente,
                    formaciones=formaciones,
                    empleos=empleos,
                    articulos=articulos,
                    libros=libros,
                    congresos=congresos,
                    cursos=cursos,
                    proyectos=proyectos,
                    tesis=tesis,
                    desarrollos=desarrollos,
                    tipo_cv=tipo_cv,
                    sections=selected_sections
                )
                nombre_archivo = docente.nombre_completo.replace(' ', '_') if docente.nombre_completo else 'CV'
                return send_file(
                    io.BytesIO(pdf_data),
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f'CV_{nombre_archivo}.pdf'
                )
            elif formato == 'word':
                word_data = cv_service.generar_word(
                    docente,
                    formaciones=formaciones,
                    empleos=empleos,
                    articulos=articulos,
                    libros=libros,
                    congresos=congresos,
                    cursos=cursos,
                    proyectos=proyectos,
                    tesis=tesis,
                    desarrollos=desarrollos,
                    tipo_cv=tipo_cv,
                    sections=selected_sections
                )
                nombre_archivo = docente.nombre_completo.replace(' ', '_') if docente.nombre_completo else 'CV'
                return send_file(
                    io.BytesIO(word_data),
                    mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    as_attachment=True,
                    download_name=f'CV_{nombre_archivo}.docx'
                )
        except Exception as e:
            flash(f'Error al generar el CV: {str(e)}', 'danger')
            return redirect(url_for('admin.docente_cv', id=id))
    
    return render_template(
        'admin/docente_cv.html',
        docente=docente,
        formaciones=formaciones,
        empleos=empleos,
        articulos=articulos,
        libros=libros,
        congresos=congresos,
        cursos=cursos,
        proyectos=proyectos,
        tesis=tesis,
        desarrollos=desarrollos,
        selected_sections=selected_sections,
        formato=formato,
        tipo_cv=tipo_cv
    )
