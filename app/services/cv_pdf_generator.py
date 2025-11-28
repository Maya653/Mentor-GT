from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import os
from datetime import datetime

class CVPDFGenerator:
    """Generador de PDFs para CVs académicos"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._crear_estilos_personalizados()
    
    def _crear_estilos_personalizados(self):
        """Crear estilos personalizados para el CV"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CVTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CVSubtitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#666666'),
            spaceAfter=12,
            alignment=TA_CENTER
        ))
        
        # Sección CONACYT
        self.styles.add(ParagraphStyle(
            name='ConacytSection',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#8B0000'),
            spaceAfter=8,
            spaceBefore=14,
            fontName='Helvetica-Bold',
            leftIndent=5
        ))
        
        # Sección normal
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=6,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
    
    def generar_pdf(self, docente, secciones, plantilla='conacyt'):
        """Generar PDF y guardarlo en carpeta temporal"""
        # Crear carpeta para PDFs si no existe
        pdf_folder = os.path.join('app', 'static', 'pdfs')
        os.makedirs(pdf_folder, exist_ok=True)
        
        # Nombre del archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"CV_{docente.id}_{timestamp}.pdf"
        filepath = os.path.join(pdf_folder, filename)
        
        # Crear PDF
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Seleccionar plantilla
        if plantilla == 'conacyt':
            story = self._generar_plantilla_conacyt(docente, secciones)
        elif plantilla == 'profesional':
            story = self._generar_plantilla_profesional(docente, secciones)
        elif plantilla == 'academico':
            story = self._generar_plantilla_academica(docente, secciones)
        
        doc.build(story)
        
        return filename
    
    def _generar_plantilla_conacyt(self, docente, secciones):
        """Plantilla estilo CONACYT"""
        from app.models.articulo import Articulo
        from app.models.congreso import Congreso
        from app.models.curso_impartido import CursoImpartido
        from app.models.proyecto_investigacion import ProyectoInvestigacion
        from app.models.libro import Libro
        from app.models.tesis_dirigida import TesisDirigida
        from app.models.desarrollo_tecnologico import DesarrolloTecnologico
        from app.models.formacion_academica import FormacionAcademica
        from app.models.empleo import Empleo
        
        story = []
        
        # Encabezado
        story.append(Paragraph(docente.nombre_completo or 'Sin nombre', self.styles['CVTitle']))
        
        info_lines = []
        if docente.correo_principal:
            info_lines.append(f"Email: {docente.correo_principal}")
        if docente.cvu:
            info_lines.append(f"CVU: {docente.cvu}")
        if docente.orcid:
            info_lines.append(f"ORCID: {docente.orcid}")
        
        for line in info_lines:
            story.append(Paragraph(line, self.styles['CVSubtitle']))
        
        story.append(Spacer(1, 0.5*cm))
        
        # Datos Generales
        if secciones.get('datos_generales'):
            story.append(Paragraph("DATOS GENERALES", self.styles['ConacytSection']))
            
            data = [
                ['CURP:', docente.curp or 'No especificado'],
                ['RFC:', docente.rfc or 'No especificado'],
                ['Nacionalidad:', docente.nacionalidad or 'No especificado'],
            ]
            
            if docente.fecha_nacimiento:
                data.append(['Fecha de Nacimiento:', docente.fecha_nacimiento.strftime('%d/%m/%Y')])
            
            t = Table(data, colWidths=[4*cm, 12*cm])
            t.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#8B0000')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.4*cm))
        
        # Formación Académica
        if secciones.get('formacion_academica'):
            formaciones = FormacionAcademica.query.filter_by(docente_id=docente.id).all()
            if formaciones:
                story.append(Paragraph("FORMACIÓN ACADÉMICA", self.styles['ConacytSection']))
                
                for form in sorted(formaciones, key=lambda x: x.fecha_fin or '', reverse=True):
                    texto = f"<b>{(form.nivel or 'N/A').upper()}</b> - {form.grado_obtenido or 'Sin título'}<br/>"
                    texto += f"{form.institucion or 'Sin institución'}, {form.pais or 'Sin país'}<br/>"
                    if form.fecha_inicio and form.fecha_fin:
                        texto += f"{form.fecha_inicio.year} - {form.fecha_fin.year}"
                    
                    story.append(Paragraph(texto, self.styles['Normal']))
                    story.append(Spacer(1, 0.3*cm))
        
        # Experiencia Laboral
        if secciones.get('experiencia_laboral'):
            empleos = Empleo.query.filter_by(docente_id=docente.id).order_by(Empleo.fecha_inicio.desc()).all()
            if empleos:
                story.append(Paragraph("EXPERIENCIA LABORAL", self.styles['ConacytSection']))
                
                for emp in empleos:
                    texto = f"<b>{emp.puesto or 'Sin puesto'}</b><br/>"
                    texto += f"{emp.institucion or 'Sin institución'}<br/>"
                    inicio = emp.fecha_inicio.strftime('%m/%Y') if emp.fecha_inicio else 'N/A'
                    fin = emp.fecha_fin.strftime('%m/%Y') if emp.fecha_fin else 'Actualidad'
                    texto += f"{inicio} - {fin}"
                    
                    story.append(Paragraph(texto, self.styles['Normal']))
                    story.append(Spacer(1, 0.3*cm))
        
        # Artículos Científicos
        if secciones.get('articulos_cientificos'):
            articulos = Articulo.query.filter_by(docente_id=docente.id).order_by(Articulo.anio.desc()).all()
            if articulos:
                story.append(Paragraph("ARTÍCULOS CIENTÍFICOS", self.styles['ConacytSection']))
                
                for i, art in enumerate(articulos, 1):
                    texto = f"{i}. {art.autores or 'Sin autores'}. ({art.anio or 'S/F'}). "
                    texto += f"<b>{art.titulo}</b>. "
                    if art.revista:
                        texto += f"<i>{art.revista}</i>. "
                    if art.volumen:
                        texto += f"Vol. {art.volumen}"
                    if art.numero:
                        texto += f"({art.numero})"
                    if art.paginas:
                        texto += f", pp. {art.paginas}. "
                    if art.doi:
                        texto += f"DOI: {art.doi}"
                    
                    story.append(Paragraph(texto, self.styles['Normal']))
                    story.append(Spacer(1, 0.2*cm))
        
        # Libros y Capítulos
        if secciones.get('libros_capitulos'):
            libros = Libro.query.filter_by(docente_id=docente.id).order_by(Libro.anio.desc()).all()
            if libros:
                story.append(Paragraph("LIBROS Y CAPÍTULOS", self.styles['ConacytSection']))
                
                for i, libro in enumerate(libros, 1):
                    texto = f"{i}. {libro.autores or 'Sin autores'}. ({libro.anio or 'S/F'}). "
                    texto += f"<b>{libro.titulo}</b>. "
                    if libro.editorial:
                        texto += f"{libro.editorial}. "
                    if libro.pais:
                        texto += f"{libro.pais}. "
                    if libro.isbn:
                        texto += f"ISBN: {libro.isbn}"
                    
                    story.append(Paragraph(texto, self.styles['Normal']))
                    story.append(Spacer(1, 0.2*cm))
        
        # Congresos y Ponencias
        if secciones.get('congresos_ponencias'):
            congresos = Congreso.query.filter_by(docente_id=docente.id).order_by(Congreso.fecha.desc()).all()
            if congresos:
                story.append(Paragraph("CONGRESOS Y PONENCIAS", self.styles['ConacytSection']))
                
                for i, cong in enumerate(congresos, 1):
                    texto = f"{i}. <b>{cong.nombre_congreso}</b>. "
                    if cong.titulo_ponencia:
                        texto += f"Ponencia: {cong.titulo_ponencia}. "
                    if cong.ciudad and cong.pais:
                        texto += f"{cong.ciudad}, {cong.pais}. "
                    if cong.fecha:
                        texto += f"{cong.fecha.strftime('%B %Y')}"
                    
                    story.append(Paragraph(texto, self.styles['Normal']))
                    story.append(Spacer(1, 0.2*cm))
        
        # Proyectos de Investigación
        if secciones.get('proyectos_investigacion'):
            proyectos = ProyectoInvestigacion.query.filter_by(docente_id=docente.id).all()
            if proyectos:
                story.append(Paragraph("PROYECTOS DE INVESTIGACIÓN", self.styles['ConacytSection']))
                
                for proy in proyectos:
                    texto = f"<b>{proy.nombre_proyecto}</b><br/>"
                    if proy.objetivo_general:
                        texto += f"{proy.objetivo_general}<br/>"
                    if proy.financiamiento:
                        texto += f"Financiamiento: {proy.financiamiento}"
                    
                    story.append(Paragraph(texto, self.styles['Normal']))
                    story.append(Spacer(1, 0.3*cm))
        
        # Cursos Impartidos
        if secciones.get('cursos_impartidos'):
            cursos = CursoImpartido.query.filter_by(docente_id=docente.id).order_by(CursoImpartido.fecha_inicio.desc()).all()
            if cursos:
                story.append(Paragraph("CURSOS IMPARTIDOS", self.styles['ConacytSection']))
                
                for curso in cursos:
                    texto = f"<b>{curso.nombre_curso}</b><br/>"
                    if curso.programa_educativo:
                        texto += f"{curso.programa_educativo}<br/>"
                    if curso.fecha_inicio and curso.fecha_fin:
                        texto += f"{curso.fecha_inicio.strftime('%m/%Y')} - {curso.fecha_fin.strftime('%m/%Y')}"
                    
                    story.append(Paragraph(texto, self.styles['Normal']))
                    story.append(Spacer(1, 0.3*cm))
        
        # Tesis Dirigidas
        if secciones.get('tesis_dirigidas'):
            tesis = TesisDirigida.query.filter_by(docente_id=docente.id).all()
            if tesis:
                story.append(Paragraph("TESIS DIRIGIDAS", self.styles['ConacytSection']))
                
                for t in tesis:
                    texto = f"<b>{t.titulo}</b><br/>"
                    if t.estudiante_nombre:
                        texto += f"Tesista: {t.estudiante_nombre}<br/>"
                    if t.nivel:
                        texto += f"Nivel: {t.nivel}"
                    
                    story.append(Paragraph(texto, self.styles['Normal']))
                    story.append(Spacer(1, 0.3*cm))
        
        # Desarrollos Tecnológicos
        if secciones.get('desarrollos_tecnologicos'):
            desarrollos = DesarrolloTecnologico.query.filter_by(docente_id=docente.id).all()
            if desarrollos:
                story.append(Paragraph("DESARROLLOS TECNOLÓGICOS", self.styles['ConacytSection']))
                
                for des in desarrollos:
                    texto = f"<b>{des.nombre}</b><br/>"
                    if des.tipo:
                        texto += f"Tipo: {des.tipo}<br/>"
                    if des.descripcion:
                        texto += f"{des.descripcion}"
                    
                    story.append(Paragraph(texto, self.styles['Normal']))
                    story.append(Spacer(1, 0.3*cm))
        
        return story
    
    def _generar_plantilla_profesional(self, docente, secciones):
        """Plantilla moderna profesional"""
        # Similar a CONACYT pero con estilos diferentes
        return self._generar_plantilla_conacyt(docente, secciones)
    
    def _generar_plantilla_academica(self, docente, secciones):
        """Plantilla académica detallada"""
        # Similar a CONACYT pero con estilos diferentes
        return self._generar_plantilla_conacyt(docente, secciones)