from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus.flowables import Flowable
from io import BytesIO
import os
from datetime import datetime

# Colores institucionales CONAHCYT
CONAHCYT_AZUL = colors.HexColor('#1a365d')  # Azul oscuro institucional
CONAHCYT_GRIS = colors.HexColor('#4a5568')  # Gris para texto secundario
CONAHCYT_LINEA = colors.HexColor('#2d3748')  # Color para líneas
CONAHCYT_FONDO = colors.HexColor('#f7fafc')  # Fondo claro para tablas

# Colores PROFESIONAL (elegante, moderno)
PROF_NEGRO = colors.HexColor('#1a1a2e')      # Negro azulado
PROF_DORADO = colors.HexColor('#d4af37')     # Dorado elegante
PROF_GRIS = colors.HexColor('#6c757d')       # Gris neutro
PROF_FONDO = colors.HexColor('#f8f9fa')      # Fondo muy claro
PROF_ACENTO = colors.HexColor('#16213e')     # Azul muy oscuro

# Colores ACADÉMICO (verde limón + azul marino)
ACAD_VERDE = colors.HexColor('#84cc16')      # Verde limón
ACAD_VERDE_OSCURO = colors.HexColor('#65a30d')  # Verde limón oscuro
ACAD_AZUL = colors.HexColor('#1e3a5f')       # Azul marino
ACAD_AZUL_CLARO = colors.HexColor('#3b82f6') # Azul claro
ACAD_FONDO = colors.HexColor('#f0fdf4')      # Fondo verde muy claro


class HeaderFlowable(Flowable):
    """Encabezado personalizado estilo CONAHCYT"""
    
    def __init__(self, width):
        Flowable.__init__(self)
        self.width = width
        self.height = 1.2*cm
    
    def draw(self):
        # Línea superior
        self.canv.setStrokeColor(CONAHCYT_AZUL)
        self.canv.setLineWidth(2)
        self.canv.line(0, self.height, self.width, self.height)
        
        # Texto del encabezado
        self.canv.setFont('Helvetica-Bold', 14)
        self.canv.setFillColor(CONAHCYT_AZUL)
        self.canv.drawString(0, 0.3*cm, "Ciencia y Tecnología")
        
        # Línea inferior
        self.canv.setLineWidth(1)
        self.canv.line(0, 0, self.width, 0)


class CVPDFGenerator:
    """Generador de PDFs para CVs académicos - Formato CONAHCYT"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._crear_estilos_conahcyt()
    
    def _crear_estilos_conahcyt(self):
        """Crear estilos personalizados estilo CONAHCYT/CVU"""
        
        # Encabezado institucional
        self.styles.add(ParagraphStyle(
            name='ConahcytHeader',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=CONAHCYT_AZUL,
            fontName='Helvetica-Bold',
            spaceAfter=6
        ))
        
        # Nombre del investigador (grande y prominente)
        self.styles.add(ParagraphStyle(
            name='CVTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=CONAHCYT_AZUL,
            spaceAfter=2,
            spaceBefore=10,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Puesto/cargo actual
        self.styles.add(ParagraphStyle(
            name='CVPuesto',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=CONAHCYT_GRIS,
            spaceAfter=2,
            fontName='Helvetica-Bold'
        ))
        
        # Número de CVU
        self.styles.add(ParagraphStyle(
            name='CVCVU',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=CONAHCYT_GRIS,
            spaceAfter=12,
            fontName='Helvetica'
        ))
        
        # Subtítulo/contacto
        self.styles.add(ParagraphStyle(
            name='CVSubtitle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=CONAHCYT_GRIS,
            spaceAfter=8,
            alignment=TA_LEFT
        ))
        
        # Sección principal CONAHCYT (títulos de sección)
        self.styles.add(ParagraphStyle(
            name='ConacytSection',
            parent=self.styles['Heading2'],
            fontSize=11,
            textColor=CONAHCYT_AZUL,
            spaceAfter=8,
            spaceBefore=16,
            fontName='Helvetica-Bold',
            borderPadding=0,
            leftIndent=0
        ))
        
        # Texto de perfil (justificado)
        self.styles.add(ParagraphStyle(
            name='PerfilText',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leading=12
        ))
        
        # Etiqueta de campo (negrita)
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=CONAHCYT_GRIS,
            fontName='Helvetica-Bold'
        ))
        
        # Valor de campo
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.black
        ))
        
        # Item de lista (artículos, etc.)
        self.styles.add(ParagraphStyle(
            name='ListItem',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            spaceAfter=8,
            leftIndent=0,
            leading=11
        ))
        
        # Título de item (negrita)
        self.styles.add(ParagraphStyle(
            name='ItemTitle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            spaceAfter=2
        ))
        
        # Detalles de item
        self.styles.add(ParagraphStyle(
            name='ItemDetails',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=CONAHCYT_GRIS,
            spaceAfter=6,
            leading=10
        ))
        
        # Sección normal (compatibilidad)
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=CONAHCYT_AZUL,
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
        
        # Seleccionar plantilla y configurar documento
        if plantilla == 'conacyt':
            # Documento estilo CONAHCYT con encabezado/pie
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=1.5*cm,
                leftMargin=1.5*cm,
                topMargin=2.5*cm,
                bottomMargin=2*cm
            )
            story = self._generar_plantilla_conacyt(docente, secciones)
            
            # Construir con encabezado/pie de página
            doc.build(
                story,
                onFirstPage=self._encabezado_conahcyt,
                onLaterPages=self._encabezado_conahcyt
            )
        elif plantilla == 'profesional':
            # Documento estilo PROFESIONAL elegante
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2.8*cm,
                bottomMargin=2*cm
            )
            story = self._generar_plantilla_profesional(docente, secciones)
            doc.build(
                story,
                onFirstPage=self._encabezado_profesional,
                onLaterPages=self._encabezado_profesional
            )
        
        elif plantilla == 'academico':
            # Documento estilo ACADÉMICO verde/azul
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2.8*cm,
                bottomMargin=2*cm
            )
            story = self._generar_plantilla_academica(docente, secciones)
            doc.build(
                story,
                onFirstPage=self._encabezado_academico,
                onLaterPages=self._encabezado_academico
            )
        
        else:
            # Plantilla por defecto (CONACYT)
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=1.5*cm,
                leftMargin=1.5*cm,
                topMargin=2.5*cm,
                bottomMargin=2*cm
            )
            story = self._generar_plantilla_conacyt(docente, secciones)
            doc.build(
                story,
                onFirstPage=self._encabezado_conahcyt,
                onLaterPages=self._encabezado_conahcyt
            )
        
        return filename
    
    def _encabezado_conahcyt(self, canvas, doc):
        """Dibujar encabezado y pie de página estilo CONAHCYT"""
        canvas.saveState()
        
        # Dimensiones de la página
        width, height = letter
        
        # === ENCABEZADO ===
        # Línea superior
        canvas.setStrokeColor(CONAHCYT_AZUL)
        canvas.setLineWidth(2)
        canvas.line(1.5*cm, height - 1.2*cm, width - 1.5*cm, height - 1.2*cm)
        
        # Texto "Ciencia y Tecnología"
        canvas.setFont('Helvetica-Bold', 12)
        canvas.setFillColor(CONAHCYT_AZUL)
        canvas.drawString(1.5*cm, height - 1.8*cm, "Ciencia y Tecnología")
        
        # Línea debajo del texto
        canvas.setLineWidth(0.5)
        canvas.line(1.5*cm, height - 2*cm, width - 1.5*cm, height - 2*cm)
        
        # === PIE DE PÁGINA ===
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(CONAHCYT_GRIS)
        page_num = canvas.getPageNumber()
        canvas.drawRightString(width - 1.5*cm, 1*cm, f"Página {page_num}")
        
        fecha = datetime.now().strftime('%d/%m/%Y')
        canvas.drawString(1.5*cm, 1*cm, f"Generado: {fecha}")
        
        canvas.setStrokeColor(CONAHCYT_LINEA)
        canvas.setLineWidth(0.5)
        canvas.line(1.5*cm, 1.3*cm, width - 1.5*cm, 1.3*cm)
        
        canvas.restoreState()
    
    def _encabezado_profesional(self, canvas, doc):
        """Dibujar encabezado y pie de página estilo PROFESIONAL elegante"""
        canvas.saveState()
        
        width, height = A4
        
        # === ENCABEZADO ===
        # Barra superior dorada
        canvas.setFillColor(PROF_DORADO)
        canvas.rect(0, height - 0.8*cm, width, 0.8*cm, fill=1, stroke=0)
        
        # Barra negra debajo
        canvas.setFillColor(PROF_NEGRO)
        canvas.rect(0, height - 2.2*cm, width, 1.4*cm, fill=1, stroke=0)
        
        # Texto "CURRICULUM VITAE"
        canvas.setFont('Helvetica-Bold', 16)
        canvas.setFillColor(colors.white)
        canvas.drawCentredString(width/2, height - 1.7*cm, "CURRICULUM VITAE")
        
        # Línea dorada decorativa
        canvas.setStrokeColor(PROF_DORADO)
        canvas.setLineWidth(2)
        canvas.line(2*cm, height - 2.4*cm, width - 2*cm, height - 2.4*cm)
        
        # === PIE DE PÁGINA ===
        # Barra inferior
        canvas.setFillColor(PROF_NEGRO)
        canvas.rect(0, 0, width, 1.2*cm, fill=1, stroke=0)
        
        # Línea dorada
        canvas.setStrokeColor(PROF_DORADO)
        canvas.setLineWidth(2)
        canvas.line(0, 1.2*cm, width, 1.2*cm)
        
        # Número de página
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.white)
        page_num = canvas.getPageNumber()
        canvas.drawCentredString(width/2, 0.4*cm, f"— {page_num} —")
        
        canvas.restoreState()
    
    def _encabezado_academico(self, canvas, doc):
        """Dibujar encabezado y pie de página estilo ACADÉMICO verde/azul"""
        canvas.saveState()
        
        width, height = A4
        
        # === ENCABEZADO ===
        # Gradiente simulado con rectángulos (azul marino)
        canvas.setFillColor(ACAD_AZUL)
        canvas.rect(0, height - 1.8*cm, width, 1.8*cm, fill=1, stroke=0)
        
        # Franja verde limón
        canvas.setFillColor(ACAD_VERDE)
        canvas.rect(0, height - 2.2*cm, width, 0.4*cm, fill=1, stroke=0)
        
        # Texto "CV ACADÉMICO"
        canvas.setFont('Helvetica-Bold', 18)
        canvas.setFillColor(colors.white)
        canvas.drawCentredString(width/2, height - 1.3*cm, "CURRÍCULUM VITAE ACADÉMICO")
        
        # Icono decorativo (círculos)
        canvas.setFillColor(ACAD_VERDE)
        canvas.circle(2.5*cm, height - 0.9*cm, 0.25*cm, fill=1, stroke=0)
        canvas.circle(width - 2.5*cm, height - 0.9*cm, 0.25*cm, fill=1, stroke=0)
        
        # === PIE DE PÁGINA ===
        # Franja verde
        canvas.setFillColor(ACAD_VERDE)
        canvas.rect(0, 0.8*cm, width, 0.3*cm, fill=1, stroke=0)
        
        # Franja azul
        canvas.setFillColor(ACAD_AZUL)
        canvas.rect(0, 0, width, 0.8*cm, fill=1, stroke=0)
        
        # Información del pie
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.white)
        page_num = canvas.getPageNumber()
        canvas.drawCentredString(width/2, 0.3*cm, f"Página {page_num}")
        
        fecha = datetime.now().strftime('%d/%m/%Y')
        canvas.drawString(2*cm, 0.3*cm, f"Generado: {fecha}")
        
        canvas.restoreState()
    
    def _generar_plantilla_conacyt(self, docente, secciones):
        """Plantilla estilo CONAHCYT/CVU oficial"""
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
        page_width = letter[0] - 3*cm  # Ancho disponible
        
        # ==========================================
        # ENCABEZADO PRINCIPAL (Nombre + CVU)
        # ==========================================
        story.append(Spacer(1, 0.3*cm))
        
        # Nombre del investigador
        story.append(Paragraph(
            (docente.nombre_completo or 'Sin nombre').upper(), 
            self.styles['CVTitle']
        ))
        
        # Obtener empleo actual para mostrar el puesto
        empleo_actual = Empleo.query.filter_by(docente_id=docente.id).order_by(Empleo.fecha_inicio.desc()).first()
        if empleo_actual and empleo_actual.puesto:
            story.append(Paragraph(empleo_actual.puesto.upper(), self.styles['CVPuesto']))
        
        # Número de CVU
        if docente.cvu:
            story.append(Paragraph(f"NO. CVU: {docente.cvu}", self.styles['CVCVU']))
        
        story.append(Spacer(1, 0.3*cm))
        
        # Línea separadora
        story.append(HRFlowable(
            width="100%", 
            thickness=1, 
            color=CONAHCYT_LINEA,
            spaceBefore=4,
            spaceAfter=12
        ))
        
        # ==========================================
        # SECCIÓN: PERFIL (si hay datos)
        # ==========================================
        # Por ahora usamos la información disponible para crear un perfil
        
        # ==========================================
        # SECCIÓN: INFORMACIÓN GENERAL
        # ==========================================
        if secciones.get('datos_generales'):
            story.append(Paragraph("INFORMACIÓN GENERAL", self.styles['ConacytSection']))
            story.append(Spacer(1, 0.2*cm))
            
            # Tabla de información general (3 columnas como en el CVU)
            col_width = page_width / 3
            
            # Primera fila
            data_row1 = [
                [Paragraph("<b>CURP</b>", self.styles['FieldLabel']),
                 Paragraph("<b>DOMICILIO</b>", self.styles['FieldLabel']),
                 Paragraph("<b>NACIONALIDAD</b>", self.styles['FieldLabel'])],
                [Paragraph(docente.curp or 'No especificado', self.styles['FieldValue']),
                 Paragraph(docente.domicilio or 'No especificado', self.styles['FieldValue']),
                 Paragraph(docente.nacionalidad or 'No especificada', self.styles['FieldValue'])]
            ]
            
            t1 = Table(data_row1, colWidths=[col_width, col_width, col_width])
            t1.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(t1)
            
            # Segunda fila
            fecha_nac = docente.fecha_nacimiento.strftime('%Y-%m-%d') if docente.fecha_nacimiento else 'No especificada'
            data_row2 = [
                [Paragraph("<b>RFC</b>", self.styles['FieldLabel']),
                 Paragraph("<b>FECHA NACIMIENTO</b>", self.styles['FieldLabel']),
                 Paragraph("<b>ESTADO CIVIL</b>", self.styles['FieldLabel'])],
                [Paragraph(docente.rfc or 'No especificado', self.styles['FieldValue']),
                 Paragraph(fecha_nac, self.styles['FieldValue']),
                 Paragraph(docente.estado_civil or 'No especificado', self.styles['FieldValue'])]
            ]
            
            t2 = Table(data_row2, colWidths=[col_width, col_width, col_width])
            t2.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(t2)
            
            # Tercera fila
            data_row3 = [
                [Paragraph("<b>SEXO</b>", self.styles['FieldLabel']),
                 Paragraph("<b>PAÍS DE NACIMIENTO</b>", self.styles['FieldLabel']),
                 Paragraph("", self.styles['FieldLabel'])],
                [Paragraph(docente.sexo or 'No especificado', self.styles['FieldValue']),
                 Paragraph(docente.pais_nacimiento or 'No especificado', self.styles['FieldValue']),
                 Paragraph("", self.styles['FieldValue'])]
            ]
            
            t3 = Table(data_row3, colWidths=[col_width, col_width, col_width])
            t3.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(t3)
            
            story.append(Spacer(1, 0.3*cm))
            
            # ==========================================
            # IDENTIFICADORES
            # ==========================================
            story.append(Paragraph("IDENTIFICADORES", self.styles['ConacytSection']))
            story.append(Spacer(1, 0.2*cm))
            
            id_data = []
            if docente.orcid:
                id_data.append([
                    Paragraph("<b>ORCID:</b>", self.styles['FieldLabel']),
                    Paragraph(docente.orcid, self.styles['FieldValue'])
                ])
            if docente.researcher_id:
                id_data.append([
                    Paragraph("<b>RESEARCHER ID:</b>", self.styles['FieldLabel']),
                    Paragraph(docente.researcher_id, self.styles['FieldValue'])
                ])
            if docente.scopus_author_id:
                id_data.append([
                    Paragraph("<b>SCOPUS AUTHOR ID:</b>", self.styles['FieldLabel']),
                    Paragraph(docente.scopus_author_id, self.styles['FieldValue'])
                ])
            
            if id_data:
                t_ids = Table(id_data, colWidths=[4*cm, page_width - 4*cm])
                t_ids.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                story.append(t_ids)
            else:
                story.append(Paragraph("No se han registrado identificadores.", self.styles['FieldValue']))
            
            story.append(Spacer(1, 0.3*cm))
            
            # ==========================================
            # MEDIOS DE CONTACTO
            # ==========================================
            story.append(Paragraph("MEDIOS DE CONTACTO", self.styles['ConacytSection']))
            story.append(Spacer(1, 0.2*cm))
            
            contact_data = []
            if docente.correo_principal:
                contact_data.append([
                    Paragraph("<b>CORREO PRINCIPAL</b>", self.styles['FieldLabel']),
                    Paragraph(docente.correo_principal.upper(), self.styles['FieldValue'])
                ])
            
            if contact_data:
                t_contact = Table(contact_data, colWidths=[4*cm, page_width - 4*cm])
                t_contact.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                story.append(t_contact)
            
            story.append(Spacer(1, 0.3*cm))
            story.append(HRFlowable(width="100%", thickness=0.5, color=CONAHCYT_LINEA, spaceAfter=8))
        
        # ==========================================
        # EMPLEO ACTUAL
        # ==========================================
        if secciones.get('experiencia_laboral'):
            empleos = Empleo.query.filter_by(docente_id=docente.id).order_by(Empleo.fecha_inicio.desc()).all()
            
            if empleos:
                # Empleo actual (el más reciente)
                emp_actual = empleos[0] if empleos else None
                if emp_actual:
                    story.append(Paragraph("EMPLEO ACTUAL", self.styles['ConacytSection']))
                    story.append(Spacer(1, 0.2*cm))
                    story.append(HRFlowable(width="100%", thickness=0.5, color=CONAHCYT_LINEA, spaceAfter=6))
                    
                    story.append(Paragraph(
                        f"<b>{(emp_actual.puesto or 'Sin puesto').upper()}</b>",
                        self.styles['ItemTitle']
                    ))
                    story.append(Paragraph(
                        emp_actual.institucion or 'Sin institución',
                        self.styles['FieldValue']
                    ))
                    
                    inicio = emp_actual.fecha_inicio.strftime('%Y-%m-%d') if emp_actual.fecha_inicio else 'N/A'
                    fin = emp_actual.fecha_fin.strftime('%Y-%m-%d') if emp_actual.fecha_fin else 'PRESENTE'
                    story.append(Paragraph(f"{inicio} - {fin}", self.styles['ItemDetails']))
                    
                    if emp_actual.logros:
                        story.append(Paragraph(f"LOGROS: {emp_actual.logros}", self.styles['ItemDetails']))
                    
                    story.append(Spacer(1, 0.4*cm))
                
                # Trayectoria profesional (todos los empleos)
                if len(empleos) > 1:
                    story.append(Paragraph("TRAYECTORIA PROFESIONAL", self.styles['ConacytSection']))
                    story.append(Spacer(1, 0.2*cm))
                    
                    for emp in empleos[1:]:  # Excluir el empleo actual
                        story.append(Paragraph(
                            f"<b>{(emp.puesto or 'Sin puesto').upper()}</b>",
                            self.styles['ItemTitle']
                        ))
                        story.append(Paragraph(emp.institucion or 'Sin institución', self.styles['FieldValue']))
                        
                        inicio = emp.fecha_inicio.strftime('%Y-%m-%d') if emp.fecha_inicio else 'N/A'
                        fin = emp.fecha_fin.strftime('%Y-%m-%d') if emp.fecha_fin else 'PRESENTE'
                        story.append(Paragraph(f"{inicio} - {fin}", self.styles['ItemDetails']))
                        
                        if emp.logros:
                            story.append(Paragraph(f"LOGROS: {emp.logros}", self.styles['ItemDetails']))
                        
                        story.append(Spacer(1, 0.3*cm))
        
        # ==========================================
        # FORMACIÓN ACADÉMICA
        # ==========================================
        if secciones.get('formacion_academica'):
            formaciones = FormacionAcademica.query.filter_by(docente_id=docente.id).all()
            if formaciones:
                story.append(Paragraph("FORMACIÓN ACADÉMICA", self.styles['ConacytSection']))
                story.append(Spacer(1, 0.2*cm))
                
                for form in sorted(formaciones, key=lambda x: x.fecha_fin or datetime.min.date(), reverse=True):
                    story.append(Paragraph(
                        f"<b>{(form.nivel or 'N/A').upper()}</b>",
                        self.styles['ItemTitle']
                    ))
                    story.append(Paragraph(
                        f"{form.grado_obtenido or 'Sin título'} - {form.institucion or 'Sin institución'}",
                        self.styles['FieldValue']
                    ))
                    
                    if form.pais:
                        story.append(Paragraph(form.pais, self.styles['ItemDetails']))
                    
                    if form.fecha_inicio and form.fecha_fin:
                        story.append(Paragraph(
                            f"{form.fecha_inicio.strftime('%Y-%m-%d')} - {form.fecha_fin.strftime('%Y-%m-%d')}",
                            self.styles['ItemDetails']
                        ))
                    
                    story.append(Spacer(1, 0.3*cm))
        
        # ==========================================
        # ARTÍCULOS CIENTÍFICOS
        # ==========================================
        if secciones.get('articulos_cientificos'):
            articulos = Articulo.query.filter_by(docente_id=docente.id).order_by(Articulo.anio.desc()).all()
            if articulos:
                story.append(Paragraph("ARTÍCULOS", self.styles['ConacytSection']))
                story.append(Spacer(1, 0.2*cm))
                
                for art in articulos:
                    # Título del artículo
                    story.append(Paragraph(
                        f"<b>{art.titulo or 'Sin título'}</b>",
                        self.styles['ItemTitle']
                    ))
                    
                    # Autores y revista
                    detalles = []
                    if art.autores:
                        detalles.append(art.autores)
                    if art.revista:
                        detalles.append(f"<i>{art.revista}</i>")
                    if art.anio:
                        detalles.append(f"({art.anio})")
                    
                    if detalles:
                        story.append(Paragraph(" | ".join(detalles), self.styles['ItemDetails']))
                    
                    # DOI si existe
                    if art.doi:
                        story.append(Paragraph(f"DOI: {art.doi}", self.styles['ItemDetails']))
                    
                    story.append(Spacer(1, 0.25*cm))
        
        # ==========================================
        # LIBROS Y CAPÍTULOS
        # ==========================================
        if secciones.get('libros_capitulos'):
            libros = Libro.query.filter_by(docente_id=docente.id).order_by(Libro.anio.desc()).all()
            if libros:
                story.append(Paragraph("LIBROS Y CAPÍTULOS", self.styles['ConacytSection']))
                story.append(Spacer(1, 0.2*cm))
                
                for libro in libros:
                    story.append(Paragraph(
                        f"<b>{libro.titulo or 'Sin título'}</b>",
                        self.styles['ItemTitle']
                    ))
                    
                    detalles = []
                    if libro.autores:
                        detalles.append(libro.autores)
                    if libro.editorial:
                        detalles.append(libro.editorial)
                    if libro.anio:
                        detalles.append(f"({libro.anio})")
                    
                    if detalles:
                        story.append(Paragraph(" | ".join(detalles), self.styles['ItemDetails']))
                    
                    if libro.isbn:
                        story.append(Paragraph(f"ISBN: {libro.isbn}", self.styles['ItemDetails']))
                    
                    story.append(Spacer(1, 0.25*cm))
        
        # ==========================================
        # CONGRESOS Y PONENCIAS
        # ==========================================
        if secciones.get('congresos_ponencias'):
            congresos = Congreso.query.filter_by(docente_id=docente.id).order_by(Congreso.fecha.desc()).all()
            if congresos:
                story.append(Paragraph("PARTICIPACIÓN EN CONGRESOS", self.styles['ConacytSection']))
                story.append(Spacer(1, 0.2*cm))
                
                for cong in congresos:
                    story.append(Paragraph(
                        f"<b>{cong.nombre_congreso or 'Sin nombre'}</b>",
                        self.styles['ItemTitle']
                    ))
                    
                    if cong.titulo_ponencia:
                        story.append(Paragraph(
                            f"Ponencia: {cong.titulo_ponencia}",
                            self.styles['FieldValue']
                        ))
                    
                    detalles = []
                    if cong.ciudad:
                        detalles.append(cong.ciudad)
                    if cong.pais:
                        detalles.append(cong.pais)
                    if cong.fecha:
                        detalles.append(cong.fecha.strftime('%Y-%m-%d'))
                    
                    if detalles:
                        story.append(Paragraph(" | ".join(detalles), self.styles['ItemDetails']))
                    
                    story.append(Spacer(1, 0.25*cm))
        
        # ==========================================
        # PROYECTOS DE INVESTIGACIÓN
        # ==========================================
        if secciones.get('proyectos_investigacion'):
            proyectos = ProyectoInvestigacion.query.filter_by(docente_id=docente.id).all()
            if proyectos:
                story.append(Paragraph("PROYECTOS DE INVESTIGACIÓN", self.styles['ConacytSection']))
                story.append(Spacer(1, 0.2*cm))
                
                for proy in proyectos:
                    story.append(Paragraph(
                        f"<b>{proy.nombre_proyecto or 'Sin nombre'}</b>",
                        self.styles['ItemTitle']
                    ))
                    
                    if proy.objetivo_general:
                        story.append(Paragraph(proy.objetivo_general, self.styles['FieldValue']))
                    
                    if proy.financiamiento:
                        story.append(Paragraph(
                            f"Financiamiento: {proy.financiamiento}",
                            self.styles['ItemDetails']
                        ))
                    
                    story.append(Spacer(1, 0.25*cm))
        
        # ==========================================
        # CURSOS IMPARTIDOS
        # ==========================================
        if secciones.get('cursos_impartidos'):
            cursos = CursoImpartido.query.filter_by(docente_id=docente.id).order_by(CursoImpartido.fecha_inicio.desc()).all()
            if cursos:
                story.append(Paragraph("CURSOS IMPARTIDOS", self.styles['ConacytSection']))
                story.append(Spacer(1, 0.2*cm))
                
                for curso in cursos:
                    story.append(Paragraph(
                        f"<b>{curso.nombre_curso or 'Sin nombre'}</b>",
                        self.styles['ItemTitle']
                    ))
                    
                    if curso.programa_educativo:
                        story.append(Paragraph(curso.programa_educativo, self.styles['FieldValue']))
                    
                    if curso.fecha_inicio and curso.fecha_fin:
                        story.append(Paragraph(
                            f"{curso.fecha_inicio.strftime('%Y-%m-%d')} - {curso.fecha_fin.strftime('%Y-%m-%d')}",
                            self.styles['ItemDetails']
                        ))
                    
                    story.append(Spacer(1, 0.25*cm))
        
        # ==========================================
        # TESIS DIRIGIDAS
        # ==========================================
        if secciones.get('tesis_dirigidas'):
            tesis_list = TesisDirigida.query.filter_by(docente_id=docente.id).all()
            if tesis_list:
                story.append(Paragraph("TESIS DIRIGIDAS", self.styles['ConacytSection']))
                story.append(Spacer(1, 0.2*cm))
                
                for tesis in tesis_list:
                    story.append(Paragraph(
                        f"<b>{tesis.titulo or 'Sin título'}</b>",
                        self.styles['ItemTitle']
                    ))
                    
                    detalles = []
                    if tesis.estudiante_nombre:
                        detalles.append(f"Tesista: {tesis.estudiante_nombre}")
                    if tesis.nivel:
                        detalles.append(f"Nivel: {tesis.nivel}")
                    
                    if detalles:
                        story.append(Paragraph(" | ".join(detalles), self.styles['ItemDetails']))
                    
                    story.append(Spacer(1, 0.25*cm))
        
        # ==========================================
        # DESARROLLOS TECNOLÓGICOS
        # ==========================================
        if secciones.get('desarrollos_tecnologicos'):
            desarrollos = DesarrolloTecnologico.query.filter_by(docente_id=docente.id).all()
            if desarrollos:
                story.append(Paragraph("DESARROLLOS TECNOLÓGICOS", self.styles['ConacytSection']))
                story.append(Spacer(1, 0.2*cm))
                
                for des in desarrollos:
                    story.append(Paragraph(
                        f"<b>{des.nombre or 'Sin nombre'}</b>",
                        self.styles['ItemTitle']
                    ))
                    
                    if des.tipo:
                        story.append(Paragraph(f"Tipo: {des.tipo}", self.styles['FieldValue']))
                    
                    if des.descripcion:
                        story.append(Paragraph(des.descripcion, self.styles['ItemDetails']))
                    
                    story.append(Spacer(1, 0.25*cm))
        
        return story
    
    def _generar_plantilla_profesional(self, docente, secciones):
        """Plantilla PROFESIONAL - Elegante y moderna con dorado/negro"""
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
        page_width = A4[0] - 4*cm
        
        # Estilos personalizados para profesional
        prof_title = ParagraphStyle(
            'ProfTitle', parent=self.styles['Heading1'],
            fontSize=22, textColor=PROF_NEGRO, alignment=TA_CENTER,
            fontName='Helvetica-Bold', spaceAfter=4, spaceBefore=8
        )
        prof_subtitle = ParagraphStyle(
            'ProfSubtitle', parent=self.styles['Normal'],
            fontSize=11, textColor=PROF_GRIS, alignment=TA_CENTER, spaceAfter=15
        )
        prof_section = ParagraphStyle(
            'ProfSection', parent=self.styles['Heading2'],
            fontSize=12, textColor=PROF_NEGRO, fontName='Helvetica-Bold',
            spaceBefore=18, spaceAfter=10, borderPadding=(5, 0, 5, 0)
        )
        prof_item = ParagraphStyle(
            'ProfItem', parent=self.styles['Normal'],
            fontSize=10, textColor=PROF_NEGRO, fontName='Helvetica-Bold', spaceAfter=2
        )
        prof_detail = ParagraphStyle(
            'ProfDetail', parent=self.styles['Normal'],
            fontSize=9, textColor=PROF_GRIS, spaceAfter=8, leading=11
        )
        
        # ==========================================
        # ENCABEZADO
        # ==========================================
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph((docente.nombre_completo or 'Sin nombre').upper(), prof_title))
        
        # Línea dorada decorativa
        story.append(HRFlowable(width="40%", thickness=2, color=PROF_DORADO, spaceBefore=8, spaceAfter=8))
        
        # Información de contacto
        contacto = []
        if docente.correo_principal:
            contacto.append(f"📧 {docente.correo_principal}")
        if docente.orcid:
            contacto.append(f"🔗 ORCID: {docente.orcid}")
        if contacto:
            story.append(Paragraph(" | ".join(contacto), prof_subtitle))
        
        story.append(Spacer(1, 0.5*cm))
        
        # ==========================================
        # PERFIL PROFESIONAL
        # ==========================================
        if secciones.get('datos_generales'):
            story.append(HRFlowable(width="100%", thickness=1, color=PROF_DORADO, spaceAfter=4))
            story.append(Paragraph("PERFIL PROFESIONAL", prof_section))
            
            # Tabla elegante de datos
            data = []
            if docente.nacionalidad:
                data.append(['Nacionalidad:', docente.nacionalidad])
            if docente.fecha_nacimiento:
                data.append(['Fecha de Nacimiento:', docente.fecha_nacimiento.strftime('%d de %B, %Y')])
            if docente.cvu:
                data.append(['CVU:', docente.cvu])
            
            if data:
                t = Table(data, colWidths=[4*cm, page_width - 4*cm])
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('TEXTCOLOR', (0, 0), (0, -1), PROF_DORADO),
                    ('TEXTCOLOR', (1, 0), (1, -1), PROF_NEGRO),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                story.append(t)
        
        # ==========================================
        # EXPERIENCIA PROFESIONAL
        # ==========================================
        if secciones.get('experiencia_laboral'):
            empleos = Empleo.query.filter_by(docente_id=docente.id).order_by(Empleo.fecha_inicio.desc()).all()
            if empleos:
                story.append(HRFlowable(width="100%", thickness=1, color=PROF_DORADO, spaceAfter=4))
                story.append(Paragraph("EXPERIENCIA PROFESIONAL", prof_section))
                
                for emp in empleos:
                    story.append(Paragraph(f"▸ {emp.puesto or 'Sin puesto'}", prof_item))
                    
                    inicio = emp.fecha_inicio.strftime('%b %Y') if emp.fecha_inicio else 'N/A'
                    fin = emp.fecha_fin.strftime('%b %Y') if emp.fecha_fin else 'Presente'
                    story.append(Paragraph(
                        f"{emp.institucion or 'Sin institución'} • {inicio} - {fin}",
                        prof_detail
                    ))
                    
                    if emp.logros:
                        story.append(Paragraph(f"<i>{emp.logros[:200]}...</i>" if len(emp.logros or '') > 200 else f"<i>{emp.logros}</i>", prof_detail))
        
        # ==========================================
        # FORMACIÓN ACADÉMICA
        # ==========================================
        if secciones.get('formacion_academica'):
            formaciones = FormacionAcademica.query.filter_by(docente_id=docente.id).all()
            if formaciones:
                story.append(HRFlowable(width="100%", thickness=1, color=PROF_DORADO, spaceAfter=4))
                story.append(Paragraph("FORMACIÓN ACADÉMICA", prof_section))
                
                for form in sorted(formaciones, key=lambda x: x.fecha_fin or datetime.min.date(), reverse=True):
                    story.append(Paragraph(f"▸ {(form.nivel or 'N/A').upper()} - {form.grado_obtenido or 'Sin título'}", prof_item))
                    
                    periodo = ""
                    if form.fecha_inicio and form.fecha_fin:
                        periodo = f" • {form.fecha_inicio.year} - {form.fecha_fin.year}"
                    story.append(Paragraph(f"{form.institucion or 'Sin institución'}{periodo}", prof_detail))
        
        # ==========================================
        # PUBLICACIONES
        # ==========================================
        if secciones.get('articulos_cientificos'):
            articulos = Articulo.query.filter_by(docente_id=docente.id).order_by(Articulo.anio.desc()).all()
            if articulos:
                story.append(HRFlowable(width="100%", thickness=1, color=PROF_DORADO, spaceAfter=4))
                story.append(Paragraph(f"PUBLICACIONES CIENTÍFICAS ({len(articulos)})", prof_section))
                
                for i, art in enumerate(articulos[:10], 1):  # Limitar a 10
                    story.append(Paragraph(f"{i}. {art.titulo or 'Sin título'}", prof_item))
                    detalles = []
                    if art.revista:
                        detalles.append(f"<i>{art.revista}</i>")
                    if art.anio:
                        detalles.append(f"({art.anio})")
                    if detalles:
                        story.append(Paragraph(" ".join(detalles), prof_detail))
        
        # ==========================================
        # LIBROS
        # ==========================================
        if secciones.get('libros_capitulos'):
            libros = Libro.query.filter_by(docente_id=docente.id).order_by(Libro.anio.desc()).all()
            if libros:
                story.append(HRFlowable(width="100%", thickness=1, color=PROF_DORADO, spaceAfter=4))
                story.append(Paragraph("LIBROS Y CAPÍTULOS", prof_section))
                
                for libro in libros:
                    story.append(Paragraph(f"▸ {libro.titulo or 'Sin título'}", prof_item))
                    detalles = []
                    if libro.editorial:
                        detalles.append(libro.editorial)
                    if libro.anio:
                        detalles.append(f"({libro.anio})")
                    if detalles:
                        story.append(Paragraph(" • ".join(detalles), prof_detail))
        
        # ==========================================
        # CONGRESOS
        # ==========================================
        if secciones.get('congresos_ponencias'):
            congresos = Congreso.query.filter_by(docente_id=docente.id).order_by(Congreso.fecha.desc()).all()
            if congresos:
                story.append(HRFlowable(width="100%", thickness=1, color=PROF_DORADO, spaceAfter=4))
                story.append(Paragraph("PARTICIPACIÓN EN EVENTOS", prof_section))
                
                for cong in congresos[:8]:
                    story.append(Paragraph(f"▸ {cong.nombre_congreso or 'Sin nombre'}", prof_item))
                    if cong.fecha:
                        story.append(Paragraph(f"{cong.ciudad or ''}, {cong.pais or ''} • {cong.fecha.strftime('%B %Y')}", prof_detail))
        
        # ==========================================
        # PROYECTOS
        # ==========================================
        if secciones.get('proyectos_investigacion'):
            proyectos = ProyectoInvestigacion.query.filter_by(docente_id=docente.id).all()
            if proyectos:
                story.append(HRFlowable(width="100%", thickness=1, color=PROF_DORADO, spaceAfter=4))
                story.append(Paragraph("PROYECTOS DE INVESTIGACIÓN", prof_section))
                
                for proy in proyectos:
                    story.append(Paragraph(f"▸ {proy.nombre_proyecto or 'Sin nombre'}", prof_item))
                    if proy.financiamiento:
                        story.append(Paragraph(f"Financiamiento: {proy.financiamiento}", prof_detail))
        
        # ==========================================
        # DOCENCIA
        # ==========================================
        if secciones.get('cursos_impartidos'):
            cursos = CursoImpartido.query.filter_by(docente_id=docente.id).all()
            if cursos:
                story.append(HRFlowable(width="100%", thickness=1, color=PROF_DORADO, spaceAfter=4))
                story.append(Paragraph("EXPERIENCIA DOCENTE", prof_section))
                
                for curso in cursos[:8]:
                    story.append(Paragraph(f"▸ {curso.nombre_curso or 'Sin nombre'}", prof_item))
                    if curso.programa_educativo:
                        story.append(Paragraph(curso.programa_educativo, prof_detail))
        
        # ==========================================
        # TESIS DIRIGIDAS
        # ==========================================
        if secciones.get('tesis_dirigidas'):
            tesis = TesisDirigida.query.filter_by(docente_id=docente.id).all()
            if tesis:
                story.append(HRFlowable(width="100%", thickness=1, color=PROF_DORADO, spaceAfter=4))
                story.append(Paragraph("DIRECCIÓN DE TESIS", prof_section))
                
                for t in tesis:
                    story.append(Paragraph(f"▸ {t.titulo or 'Sin título'}", prof_item))
                    if t.estudiante_nombre:
                        story.append(Paragraph(f"Tesista: {t.estudiante_nombre} • Nivel: {t.nivel or 'N/A'}", prof_detail))
        
        # ==========================================
        # DESARROLLOS
        # ==========================================
        if secciones.get('desarrollos_tecnologicos'):
            desarrollos = DesarrolloTecnologico.query.filter_by(docente_id=docente.id).all()
            if desarrollos:
                story.append(HRFlowable(width="100%", thickness=1, color=PROF_DORADO, spaceAfter=4))
                story.append(Paragraph("DESARROLLOS TECNOLÓGICOS", prof_section))
                
                for des in desarrollos:
                    story.append(Paragraph(f"▸ {des.nombre or 'Sin nombre'}", prof_item))
                    if des.tipo:
                        story.append(Paragraph(f"Tipo: {des.tipo}", prof_detail))
        
        return story
    
    def _generar_plantilla_academica(self, docente, secciones):
        """Plantilla ACADÉMICA - Colores verde limón y azul marino"""
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
        page_width = A4[0] - 4*cm
        
        # Estilos personalizados para académico
        acad_title = ParagraphStyle(
            'AcadTitle', parent=self.styles['Heading1'],
            fontSize=20, textColor=ACAD_AZUL, alignment=TA_CENTER,
            fontName='Helvetica-Bold', spaceAfter=6, spaceBefore=10
        )
        acad_subtitle = ParagraphStyle(
            'AcadSubtitle', parent=self.styles['Normal'],
            fontSize=10, textColor=ACAD_VERDE_OSCURO, alignment=TA_CENTER, spaceAfter=12
        )
        # Estilo para texto dentro de sección (blanco sobre fondo azul)
        acad_section_text = ParagraphStyle(
            'AcadSectionText', parent=self.styles['Normal'],
            fontSize=12, textColor=colors.white, fontName='Helvetica-Bold',
            alignment=TA_LEFT
        )
        acad_subsection = ParagraphStyle(
            'AcadSubsection', parent=self.styles['Normal'],
            fontSize=10, textColor=ACAD_AZUL, fontName='Helvetica-Bold',
            spaceBefore=10, spaceAfter=4
        )
        acad_item = ParagraphStyle(
            'AcadItem', parent=self.styles['Normal'],
            fontSize=10, textColor=ACAD_AZUL, fontName='Helvetica-Bold', spaceAfter=2
        )
        acad_detail = ParagraphStyle(
            'AcadDetail', parent=self.styles['Normal'],
            fontSize=9, textColor=colors.black, spaceAfter=8, leading=11
        )
        acad_highlight = ParagraphStyle(
            'AcadHighlight', parent=self.styles['Normal'],
            fontSize=9, textColor=ACAD_VERDE_OSCURO, fontName='Helvetica-Oblique', spaceAfter=6
        )
        
        # Función helper para crear títulos de sección con fondo
        def crear_seccion(texto):
            """Crear título de sección con fondo azul usando tabla"""
            t = Table(
                [[Paragraph(texto, acad_section_text)]],
                colWidths=[page_width]
            )
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), ACAD_AZUL),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
            return t
        
        # ==========================================
        # ENCABEZADO
        # ==========================================
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph((docente.nombre_completo or 'Sin nombre').upper(), acad_title))
        
        # Línea decorativa verde
        story.append(HRFlowable(width="60%", thickness=3, color=ACAD_VERDE, spaceBefore=6, spaceAfter=6))
        
        # Puesto actual
        empleo_actual = Empleo.query.filter_by(docente_id=docente.id).order_by(Empleo.fecha_inicio.desc()).first()
        if empleo_actual:
            story.append(Paragraph(f"🎓 {empleo_actual.puesto or 'Docente'}", acad_subtitle))
            story.append(Paragraph(f"📍 {empleo_actual.institucion or ''}", acad_subtitle))
        
        # Contacto
        contacto = []
        if docente.correo_principal:
            contacto.append(f"✉️ {docente.correo_principal}")
        if docente.orcid:
            contacto.append(f"🔗 {docente.orcid}")
        if contacto:
            story.append(Paragraph(" • ".join(contacto), acad_subtitle))
        
        story.append(Spacer(1, 0.4*cm))
        
        # ==========================================
        # INFORMACIÓN PERSONAL
        # ==========================================
        if secciones.get('datos_generales'):
            story.append(Spacer(1, 0.3*cm))
            story.append(crear_seccion("📋 INFORMACIÓN PERSONAL"))
            
            # Tabla con fondo verde claro
            col_width = page_width / 2
            data = [
                [Paragraph("<b>CVU:</b>", acad_detail), 
                 Paragraph(docente.cvu or 'No registrado', acad_detail),
                 Paragraph("<b>CURP:</b>", acad_detail),
                 Paragraph(docente.curp or 'No registrado', acad_detail)],
                [Paragraph("<b>ORCID:</b>", acad_detail),
                 Paragraph(docente.orcid or 'No registrado', acad_detail),
                 Paragraph("<b>Nacionalidad:</b>", acad_detail),
                 Paragraph(docente.nacionalidad or 'No registrada', acad_detail)],
            ]
            
            t = Table(data, colWidths=[3*cm, 5.5*cm, 3*cm, 5.5*cm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), ACAD_FONDO),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, ACAD_VERDE),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.3*cm))
        
        # ==========================================
        # FORMACIÓN ACADÉMICA
        # ==========================================
        if secciones.get('formacion_academica'):
            formaciones = FormacionAcademica.query.filter_by(docente_id=docente.id).all()
            if formaciones:
                story.append(Spacer(1, 0.3*cm))
                story.append(crear_seccion("🎓 FORMACIÓN ACADÉMICA"))
                
                for form in sorted(formaciones, key=lambda x: x.fecha_fin or datetime.min.date(), reverse=True):
                    # Icono según nivel
                    icono = "🎯" if "doctor" in (form.nivel or '').lower() else "📚" if "maestr" in (form.nivel or '').lower() else "📖"
                    story.append(Paragraph(f"{icono} <b>{(form.nivel or 'N/A').upper()}</b>", acad_item))
                    story.append(Paragraph(f"{form.grado_obtenido or 'Sin título'}", acad_detail))
                    story.append(Paragraph(f"<i>{form.institucion or 'Sin institución'}, {form.pais or ''}</i>", acad_highlight))
                    
                    if form.fecha_inicio and form.fecha_fin:
                        story.append(Paragraph(f"📅 {form.fecha_inicio.year} - {form.fecha_fin.year}", acad_detail))
                    
                    story.append(Spacer(1, 0.2*cm))
        
        # ==========================================
        # TRAYECTORIA LABORAL
        # ==========================================
        if secciones.get('experiencia_laboral'):
            empleos = Empleo.query.filter_by(docente_id=docente.id).order_by(Empleo.fecha_inicio.desc()).all()
            if empleos:
                story.append(Spacer(1, 0.3*cm))
                story.append(crear_seccion("💼 TRAYECTORIA PROFESIONAL"))
                
                for emp in empleos:
                    story.append(Paragraph(f"🏛️ <b>{emp.puesto or 'Sin puesto'}</b>", acad_item))
                    story.append(Paragraph(f"{emp.institucion or 'Sin institución'}", acad_detail))
                    
                    inicio = emp.fecha_inicio.strftime('%m/%Y') if emp.fecha_inicio else 'N/A'
                    fin = emp.fecha_fin.strftime('%m/%Y') if emp.fecha_fin else 'Actualidad'
                    story.append(Paragraph(f"📅 {inicio} - {fin}", acad_highlight))
                    
                    if emp.logros:
                        story.append(Paragraph(f"✅ {emp.logros[:150]}..." if len(emp.logros or '') > 150 else f"✅ {emp.logros}", acad_detail))
                    
                    story.append(Spacer(1, 0.2*cm))
        
        # ==========================================
        # PRODUCCIÓN CIENTÍFICA
        # ==========================================
        if secciones.get('articulos_cientificos'):
            articulos = Articulo.query.filter_by(docente_id=docente.id).order_by(Articulo.anio.desc()).all()
            if articulos:
                story.append(Spacer(1, 0.3*cm))
                story.append(crear_seccion(f"📝 ARTÍCULOS CIENTÍFICOS ({len(articulos)} publicaciones)"))
                
                for i, art in enumerate(articulos, 1):
                    story.append(Paragraph(f"<b>{i}.</b> {art.titulo or 'Sin título'}", acad_item))
                    
                    info = []
                    if art.autores:
                        info.append(art.autores)
                    story.append(Paragraph(", ".join(info) if info else "", acad_detail))
                    
                    pub_info = []
                    if art.revista:
                        pub_info.append(f"<i>{art.revista}</i>")
                    if art.anio:
                        pub_info.append(f"({art.anio})")
                    if art.doi:
                        pub_info.append(f"DOI: {art.doi}")
                    
                    if pub_info:
                        story.append(Paragraph(" | ".join(pub_info), acad_highlight))
                    
                    story.append(Spacer(1, 0.15*cm))
        
        # ==========================================
        # LIBROS
        # ==========================================
        if secciones.get('libros_capitulos'):
            libros = Libro.query.filter_by(docente_id=docente.id).order_by(Libro.anio.desc()).all()
            if libros:
                story.append(Spacer(1, 0.3*cm))
                story.append(crear_seccion("📚 LIBROS Y CAPÍTULOS DE LIBRO"))
                
                for libro in libros:
                    story.append(Paragraph(f"📖 <b>{libro.titulo or 'Sin título'}</b>", acad_item))
                    if libro.autores:
                        story.append(Paragraph(libro.autores, acad_detail))
                    
                    info = []
                    if libro.editorial:
                        info.append(libro.editorial)
                    if libro.anio:
                        info.append(f"({libro.anio})")
                    if libro.isbn:
                        info.append(f"ISBN: {libro.isbn}")
                    
                    if info:
                        story.append(Paragraph(" | ".join(info), acad_highlight))
                    
                    story.append(Spacer(1, 0.15*cm))
        
        # ==========================================
        # CONGRESOS
        # ==========================================
        if secciones.get('congresos_ponencias'):
            congresos = Congreso.query.filter_by(docente_id=docente.id).order_by(Congreso.fecha.desc()).all()
            if congresos:
                story.append(Spacer(1, 0.3*cm))
                story.append(crear_seccion(f"🎤 PARTICIPACIÓN EN CONGRESOS ({len(congresos)})"))
                
                for cong in congresos:
                    story.append(Paragraph(f"🏆 <b>{cong.nombre_congreso or 'Sin nombre'}</b>", acad_item))
                    
                    if cong.titulo_ponencia:
                        story.append(Paragraph(f"Ponencia: {cong.titulo_ponencia}", acad_detail))
                    
                    info = []
                    if cong.ciudad:
                        info.append(cong.ciudad)
                    if cong.pais:
                        info.append(cong.pais)
                    if cong.fecha:
                        info.append(cong.fecha.strftime('%d/%m/%Y'))
                    
                    if info:
                        story.append(Paragraph(f"📍 {' • '.join(info)}", acad_highlight))
                    
                    story.append(Spacer(1, 0.15*cm))
        
        # ==========================================
        # PROYECTOS
        # ==========================================
        if secciones.get('proyectos_investigacion'):
            proyectos = ProyectoInvestigacion.query.filter_by(docente_id=docente.id).all()
            if proyectos:
                story.append(Spacer(1, 0.3*cm))
                story.append(crear_seccion("🔬 PROYECTOS DE INVESTIGACIÓN"))
                
                for proy in proyectos:
                    story.append(Paragraph(f"🎯 <b>{proy.nombre_proyecto or 'Sin nombre'}</b>", acad_item))
                    
                    if proy.objetivo_general:
                        story.append(Paragraph(proy.objetivo_general, acad_detail))
                    
                    if proy.financiamiento:
                        story.append(Paragraph(f"💰 Financiamiento: {proy.financiamiento}", acad_highlight))
                    
                    story.append(Spacer(1, 0.15*cm))
        
        # ==========================================
        # DOCENCIA
        # ==========================================
        if secciones.get('cursos_impartidos'):
            cursos = CursoImpartido.query.filter_by(docente_id=docente.id).all()
            if cursos:
                story.append(Spacer(1, 0.3*cm))
                story.append(crear_seccion(f"👨‍🏫 CURSOS IMPARTIDOS ({len(cursos)})"))
                
                for curso in cursos:
                    story.append(Paragraph(f"📕 <b>{curso.nombre_curso or 'Sin nombre'}</b>", acad_item))
                    
                    if curso.programa_educativo:
                        story.append(Paragraph(curso.programa_educativo, acad_detail))
                    
                    if curso.fecha_inicio and curso.fecha_fin:
                        story.append(Paragraph(
                            f"📅 {curso.fecha_inicio.strftime('%m/%Y')} - {curso.fecha_fin.strftime('%m/%Y')}",
                            acad_highlight
                        ))
                    
                    story.append(Spacer(1, 0.1*cm))
        
        # ==========================================
        # TESIS DIRIGIDAS
        # ==========================================
        if secciones.get('tesis_dirigidas'):
            tesis = TesisDirigida.query.filter_by(docente_id=docente.id).all()
            if tesis:
                story.append(Spacer(1, 0.3*cm))
                story.append(crear_seccion(f"🎓 DIRECCIÓN DE TESIS ({len(tesis)})"))
                
                for t in tesis:
                    story.append(Paragraph(f"📜 <b>{t.titulo or 'Sin título'}</b>", acad_item))
                    
                    info = []
                    if t.estudiante_nombre:
                        info.append(f"Tesista: {t.estudiante_nombre}")
                    if t.nivel:
                        info.append(f"Nivel: {t.nivel}")
                    
                    if info:
                        story.append(Paragraph(" | ".join(info), acad_highlight))
                    
                    story.append(Spacer(1, 0.1*cm))
        
        # ==========================================
        # DESARROLLOS TECNOLÓGICOS
        # ==========================================
        if secciones.get('desarrollos_tecnologicos'):
            desarrollos = DesarrolloTecnologico.query.filter_by(docente_id=docente.id).all()
            if desarrollos:
                story.append(Spacer(1, 0.3*cm))
                story.append(crear_seccion("💻 DESARROLLOS TECNOLÓGICOS"))
                
                for des in desarrollos:
                    story.append(Paragraph(f"⚙️ <b>{des.nombre or 'Sin nombre'}</b>", acad_item))
                    
                    if des.tipo:
                        story.append(Paragraph(f"Tipo: {des.tipo}", acad_detail))
                    
                    if des.descripcion:
                        story.append(Paragraph(des.descripcion, acad_highlight))
                    
                    story.append(Spacer(1, 0.1*cm))
        
        return story