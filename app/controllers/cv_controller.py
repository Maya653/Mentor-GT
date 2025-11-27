from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.usuario import Usuario
from app.models.publicacion import Publicacion
from app.models.evento import Evento
from app.models.docencia import Docencia
from app.services.cv_generator_service import CVGeneratorService
from app.utils.decorators import profesor_required
import io

cv_bp = Blueprint('cv', __name__)

@cv_bp.route('/generar', methods=['GET', 'POST'])
@login_required
@profesor_required
def generar():
    if request.method == 'POST':
        formato = request.form.get('formato', 'pdf')
        tipo_cv = request.form.get('tipo_cv', 'academico')  # academico, sni, conacyt
        
        cv_service = CVGeneratorService()
        
        # Obtener datos del usuario
        usuario = Usuario.query.get(current_user.id)
        publicaciones = Publicacion.query.filter_by(usuario_id=current_user.id)\
            .order_by(Publicacion.año.desc()).all()
        eventos = Evento.query.filter_by(usuario_id=current_user.id)\
            .order_by(Evento.fecha_inicio.desc()).all()
        docencias = Docencia.query.filter_by(usuario_id=current_user.id)\
            .order_by(Docencia.año.desc()).all()
        
        try:
            if formato == 'pdf':
                pdf_data = cv_service.generar_pdf(usuario, publicaciones, eventos, docencias, tipo_cv)
                return send_file(
                    io.BytesIO(pdf_data),
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f'CV_{usuario.nombre}_{usuario.apellidos}.pdf'
                )
            elif formato == 'word':
                docx_data = cv_service.generar_word(usuario, publicaciones, eventos, docencias, tipo_cv)
                return send_file(
                    io.BytesIO(docx_data),
                    mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    as_attachment=True,
                    download_name=f'CV_{usuario.nombre}_{usuario.apellidos}.docx'
                )
        except Exception as e:
            flash(f'Error al generar CV: {str(e)}', 'danger')
            return redirect(url_for('cv.generar'))
    
    return render_template('profesor/generar_cv.html')

@cv_bp.route('/vista-previa')
@login_required
@profesor_required
def vista_previa():
    usuario = Usuario.query.get(current_user.id)
    publicaciones = Publicacion.query.filter_by(usuario_id=current_user.id)\
        .order_by(Publicacion.año.desc()).all()
    eventos = Evento.query.filter_by(usuario_id=current_user.id)\
        .order_by(Evento.fecha_inicio.desc()).all()
    docencias = Docencia.query.filter_by(usuario_id=current_user.id)\
        .order_by(Docencia.año.desc()).all()
    
    return render_template('profesor/vista_previa_cv.html',
                         usuario=usuario,
                         publicaciones=publicaciones,
                         eventos=eventos,
                         docencias=docencias)

