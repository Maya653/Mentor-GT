from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.docente import Docente
from app.models.formacion_academica import FormacionAcademica
from app.models.empleo import Empleo
from app.models.articulo import Articulo
from app.models.libro import Libro
from app.models.congreso import Congreso
from app.models.curso_impartido import CursoImpartido
from app.models.tesis_dirigida import TesisDirigida
from app.models.desarrollo_tecnologico import DesarrolloTecnologico
from app.services.cv_generator_service import CVGeneratorService
from app.utils.decorators import profesor_required
import io

cv_bp = Blueprint('cv', __name__)

@cv_bp.route('/generar', methods=['GET', 'POST'])
@login_required
@profesor_required
def generar():
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    
    if not docente:
        flash('Por favor completa tu perfil primero', 'warning')
        return redirect(url_for('docente.perfil'))
    
    if request.method == 'POST':
        formato = request.form.get('formato', 'pdf')
        tipo_cv = request.form.get('tipo_cv', 'academico')
        
        cv_service = CVGeneratorService()
        
        # Obtener todos los datos del docente
        formaciones = FormacionAcademica.query.filter_by(docente_id=docente.id).all()
        empleos = Empleo.query.filter_by(docente_id=docente.id).all()
        articulos = Articulo.query.filter_by(docente_id=docente.id).all()
        libros = Libro.query.filter_by(docente_id=docente.id).all()
        congresos = Congreso.query.filter_by(docente_id=docente.id).all()
        cursos = CursoImpartido.query.filter_by(docente_id=docente.id).all()
        tesis = TesisDirigida.query.filter_by(docente_id=docente.id).all()
        desarrollos = DesarrolloTecnologico.query.filter_by(docente_id=docente.id).all()
        
        try:
            if formato == 'pdf':
                pdf_data = cv_service.generar_pdf(docente, formaciones, empleos, articulos, libros, congresos, cursos, tesis, desarrollos, tipo_cv)
                nombre_archivo = docente.nombre_completo.replace(' ', '_') if docente.nombre_completo else 'CV'
                return send_file(
                    io.BytesIO(pdf_data),
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f'CV_{nombre_archivo}.pdf'
                )
            elif formato == 'word':
                docx_data = cv_service.generar_word(docente, formaciones, empleos, articulos, libros, congresos, cursos, tesis, desarrollos, tipo_cv)
                nombre_archivo = docente.nombre_completo.replace(' ', '_') if docente.nombre_completo else 'CV'
                return send_file(
                    io.BytesIO(docx_data),
                    mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    as_attachment=True,
                    download_name=f'CV_{nombre_archivo}.docx'
                )
        except Exception as e:
            flash(f'Error al generar CV: {str(e)}', 'danger')
            return redirect(url_for('cv.generar'))
    
    return render_template('docente/generar_cv.html', docente=docente)

@cv_bp.route('/vista-previa')
@login_required
@profesor_required
def vista_previa():
    docente = Docente.query.filter_by(user_id=current_user.id).first()
    
    if not docente:
        flash('Por favor completa tu perfil primero', 'warning')
        return redirect(url_for('docente.perfil'))
    
    formaciones = FormacionAcademica.query.filter_by(docente_id=docente.id).all()
    empleos = Empleo.query.filter_by(docente_id=docente.id).all()
    articulos = Articulo.query.filter_by(docente_id=docente.id).all()
    libros = Libro.query.filter_by(docente_id=docente.id).all()
    congresos = Congreso.query.filter_by(docente_id=docente.id).all()
    
    return render_template('docente/vista_previa_cv.html',
                         docente=docente,
                         formaciones=formaciones,
                         empleos=empleos,
                         articulos=articulos,
                         libros=libros,
                         congresos=congresos)
